import traceback
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime
from typing import Any, Callable, Generator, TypeVar

import pytz
from elementary_python_sdk.core.cloud.request import ElementaryObject
from elementary_python_sdk.core.logger import get_logger
from elementary_python_sdk.core.test_context import TestContext
from elementary_python_sdk.core.types.asset import TableAsset
from elementary_python_sdk.core.types.test import (
    QualityDimension,
    Test,
    TestExecution,
    TestExecutionStatus,
    TestSeverity,
)

logger = get_logger()


class ElementaryTestContext(TestContext):

    def __init__(self, asset: TableAsset | None = None, raise_on_error: bool = False):
        self.asset = asset
        self.raise_on_error = raise_on_error
        self.tests: dict[str, Test] = {}
        self.executed_tests: list[TestExecution] = []
        self._lazy_executions: list[
            tuple[list[Test], Callable[[list[Test]], list[TestExecution]]]
        ] = []
        self.context_start_time = datetime.now(pytz.utc)

    def register_test(self, test: Test) -> None:
        self.tests[test.id] = test
        logger.debug(f"Registered test: {test.name}")

    def execute(
        self,
        tests: list[Test],
        execution_func: Callable[[list[Test]], list[TestExecution]],
        lazy: bool = False,
    ) -> None:
        if lazy:
            self._lazy_executions.append((tests, execution_func))
            for test in tests:
                logger.debug(f"Registered lazy test execution for {test.name}")
        else:
            self._execute_tests(tests, execution_func)

    def record_error_execution(
        self,
        test: Test,
        exception: Exception,
        description: str,
        start_time: datetime | None = None,
        code: str | None = None,
        quality_dimension: QualityDimension | None = None,
    ) -> TestExecution:
        if start_time is None:
            start_time = self.context_start_time

        traceback_str = traceback.format_exc()
        error_execution = TestExecution(
            test_id=test.id,
            test_sub_unique_id=test.id,
            sub_type=test.test_type.value,
            failure_count=0,
            status=TestExecutionStatus.ERROR,
            code=code,
            start_time=start_time,
            duration_seconds=(datetime.now(pytz.utc) - start_time).total_seconds(),
            exception=str(exception),
            traceback=traceback_str,
            description=f"{description} - {exception}",
            column_name=test.column_name,
            quality_dimension=quality_dimension,
        )
        self.executed_tests.append(error_execution)
        return error_execution

    def log_test_completion(
        self,
        test_name: str,
        execution: TestExecution,
    ) -> None:
        log_msg = f"Test '{test_name}' completed: {execution.status.value} (duration: {execution.duration_seconds:.3f}s)"
        if execution.status == TestExecutionStatus.PASS:
            logger.info(log_msg)
        elif execution.status == TestExecutionStatus.WARN:
            logger.warning(log_msg)
        elif execution.status == TestExecutionStatus.FAIL:
            logger.error(f"{log_msg} - {execution.description}")
        elif execution.status == TestExecutionStatus.ERROR:
            logger.error(f"{log_msg} - {execution.description}")
            if execution.exception:
                logger.error(f"Exception: {execution.exception}")
        else:
            logger.info(log_msg)

    def record_context_exception(self, exception: Exception) -> None:
        already_executed_tests = set(
            execution.test_id for execution in self.executed_tests
        )
        not_executed_tests = [
            test
            for test in self.tests.values()
            if test.id not in already_executed_tests
        ]
        for test in not_executed_tests:
            self.record_error_execution(
                test=test,
                exception=exception,
                description="Test context failed with exception",
            )

    def _execute_tests(
        self,
        tests: list[Test],
        execution_func: Callable[[list[Test]], list[TestExecution]],
    ) -> None:
        try:
            executions = execution_func(tests)
            self.executed_tests.extend(executions)
            tests_by_id = {test.id: test for test in tests}
            for execution in executions:
                self.log_test_completion(tests_by_id[execution.test_id].name, execution)

        except Exception as e:
            if self.raise_on_error:
                raise e
            for test in tests:
                error_execution = self.record_error_execution(
                    test=test,
                    exception=e,
                    description="Failed to execute test",
                )
                self.log_test_completion(test.name, error_execution)

    def get_elementary_objects(self) -> list[ElementaryObject]:
        objects: list[ElementaryObject] = []

        if self.asset:
            objects.append(self.asset)

        objects.extend(list(self.tests.values()))

        for tests, execution_func in self._lazy_executions:
            self._execute_tests(tests, execution_func)

        self._lazy_executions.clear()

        objects.extend(self.executed_tests)
        self._log_context_summary()

        return objects

    def _specific_test_context(
        self,
        test_execution_callback: Callable[[Any], None],
    ) -> Generator["InnerTestContext", None, None]:
        inner_context = InnerTestContext(
            test_execution_callback,
            asset=self.asset,
            raise_on_error=self.raise_on_error,
        )

        try:
            yield from _elementary_test_context(inner_context)
        finally:
            for test_id, test in inner_context.tests.items():
                self.tests[test_id] = test

            self.executed_tests.extend(inner_context.executed_tests)

            for tests, execution_func in inner_context._lazy_executions:
                self._lazy_executions.append((tests, execution_func))

    @contextmanager
    def boolean_test(
        self,
        name: str,
        severity: TestSeverity = TestSeverity.ERROR,
        description: str | None = None,
        tags: list[str] | None = None,
        owners: list[str] | None = None,
        metadata: dict | None = None,
        column_name: str | None = None,
        quality_dimension: QualityDimension | None = None,
        skip: bool = False,
    ) -> Generator["InnerTestContext", None, None]:
        from elementary_python_sdk.core.tests.runners.impl import (
            execute_boolean_test,
        )

        inner_context_start_time = datetime.now(pytz.utc)

        def execute_test(value: Any) -> None:
            execute_boolean_test(
                name=name,
                test_argument=value,
                start_time=inner_context_start_time,
                severity=severity,
                description=description,
                tags=tags,
                owners=owners,
                metadata=metadata,
                column_name=column_name,
                quality_dimension=quality_dimension,
                skip=skip,
            )

        yield from self._specific_test_context(execute_test)

    @contextmanager
    def expected_range_test(
        self,
        name: str,
        min: float | None = None,
        max: float | None = None,
        severity: TestSeverity = TestSeverity.ERROR,
        description: str | None = None,
        tags: list[str] | None = None,
        owners: list[str] | None = None,
        metadata: dict | None = None,
        column_name: str | None = None,
        quality_dimension: QualityDimension | None = None,
        skip: bool = False,
    ) -> Generator["InnerTestContext", None, None]:
        from elementary_python_sdk.core.tests.runners.impl import (
            execute_expected_range_test,
        )

        inner_context_start_time = datetime.now(pytz.utc)

        def execute_test(value: Any) -> None:
            execute_expected_range_test(
                name=name,
                min=min,
                max=max,
                test_argument=value,
                tags=tags,
                owners=owners,
                start_time=inner_context_start_time,
                severity=severity,
                description=description,
                metadata=metadata,
                column_name=column_name,
                quality_dimension=quality_dimension,
                skip=skip,
            )

        yield from self._specific_test_context(execute_test)

    @contextmanager
    def expected_values_test(
        self,
        name: str,
        expected: list[Any],
        allow_none: bool = False,
        code: str | None = None,
        severity: TestSeverity = TestSeverity.ERROR,
        description: str | None = None,
        tags: list[str] | None = None,
        owners: list[str] | None = None,
        metadata: dict | None = None,
        column_name: str | None = None,
        quality_dimension: QualityDimension | None = None,
        skip: bool = False,
    ) -> Generator["InnerTestContext", None, None]:
        from elementary_python_sdk.core.tests.runners.impl import (
            execute_expected_values_test,
        )

        inner_context_start_time = datetime.now(pytz.utc)

        def execute_test(value: Any) -> None:
            execute_expected_values_test(
                name=name,
                expected=expected,
                test_argument=value,
                allow_none=allow_none,
                start_time=inner_context_start_time,
                code=code,
                severity=severity,
                description=description,
                metadata=metadata,
                tags=tags,
                owners=owners,
                column_name=column_name,
                quality_dimension=quality_dimension,
                skip=skip,
            )

        yield from self._specific_test_context(execute_test)

    @contextmanager
    def row_count_test(
        self,
        name: str,
        min: int | None = None,
        max: int | None = None,
        severity: TestSeverity = TestSeverity.ERROR,
        description: str | None = None,
        metadata: dict | None = None,
        tags: list[str] | None = None,
        owners: list[str] | None = None,
        skip: bool = False,
    ) -> Generator["InnerTestContext", None, None]:
        from elementary_python_sdk.core.tests.runners.impl import (
            execute_row_count_test,
        )

        inner_context_start_time = datetime.now(pytz.utc)

        def execute_test(value: Any) -> None:
            execute_row_count_test(
                name=name,
                min=min,
                max=max,
                test_argument=value,
                start_time=inner_context_start_time,
                severity=severity,
                description=description,
                metadata=metadata,
                tags=tags,
                owners=owners,
                skip=skip,
            )

        yield from self._specific_test_context(execute_test)

    def _log_context_summary(self) -> None:
        total_tests = len(self.executed_tests)

        if total_tests == 0:
            logger.info("Test context completed with no tests executed")
            return

        status_counts: dict[TestExecutionStatus, int] = {}
        failed_tests = []
        warned_tests = []
        errored_tests = []

        for execution in self.executed_tests:
            test_name = self.tests[execution.test_id].name
            status_counts[execution.status] = status_counts.get(execution.status, 0) + 1

            if execution.status == TestExecutionStatus.FAIL:
                failed_tests.append(test_name)
            elif execution.status == TestExecutionStatus.WARN:
                warned_tests.append(test_name)
            elif execution.status == TestExecutionStatus.ERROR:
                errored_tests.append(test_name)

        logger.info("=" * 60)
        logger.info("Test Context Summary")
        logger.info("=" * 60)

        if self.asset:
            if isinstance(self.asset, TableAsset):
                logger.info(f"Asset: {self.asset.fqn}")
            else:
                logger.info(f"Asset: {self.asset.name}")

        logger.info(f"Total tests executed: {total_tests}")
        for status, count in sorted(status_counts.items()):
            logger.info(f"  {status}: {count}")

        if errored_tests:
            logger.error(f"Tests with errors ({len(errored_tests)}):")
            for test_name in errored_tests:
                logger.error(f"  - {test_name}")

        if failed_tests:
            logger.error(f"Failed tests ({len(failed_tests)}):")
            for test_name in failed_tests:
                logger.error(f"  - {test_name}")

        if warned_tests:
            logger.warning(f"Tests with warnings ({len(warned_tests)}):")
            for test_name in warned_tests:
                logger.warning(f"  - {test_name}")

        logger.info("=" * 60)


class InnerTestContext(ElementaryTestContext):
    def __init__(
        self,
        test_execution_callback: Callable[[Any], None],
        asset: TableAsset | None = None,
        raise_on_error: bool = False,
    ):
        self.test_execution_callback = test_execution_callback
        super().__init__(asset=asset, raise_on_error=raise_on_error)

    def check_value(self, value: Any) -> None:
        self.test_execution_callback(value)


def log_context_initialization(test_context: ElementaryTestContext) -> None:
    if test_context.asset:
        if isinstance(test_context.asset, TableAsset):
            logger.info(f"Starting test context for asset: {test_context.asset.fqn}")
        else:
            logger.info(f"Starting test context for asset: {test_context.asset.name}")
    else:
        logger.info("Starting test context without asset")


TestContextType = TypeVar("TestContextType", bound=ElementaryTestContext)


def _elementary_test_context(
    test_context: TestContextType,
) -> Generator[TestContextType, None, None]:
    previous_context = get_active_context()
    set_active_context(test_context)
    try:
        yield test_context
    except Exception as e:
        logger.exception(f"Error in elementary test context: {e}")
        test_context.record_context_exception(e)
        if test_context.raise_on_error:
            raise
    finally:
        set_active_context(previous_context)


@contextmanager
def elementary_test_context(
    asset: TableAsset | None = None, raise_on_error: bool = False
) -> Generator[ElementaryTestContext, None, None]:
    """Context manager for elementary tests.

    Args:
        asset: Optional asset that tests are running against

    Yields:
        ElementaryTestContext instance

    Example:
        ```python
        with elementary_test_context(asset=my_asset) as ctx:
            result = check_data(df)
        ```
        this will work when check_data is using one of elementary test decorators, for example:
        ```python
        @boolean_test(name="has_data", severity="ERROR")
        def check_data(df: pd.DataFrame) -> bool:
            return df.shape[0] > 0
        ```

        if you wish to execute the test directly without wrapping your function with a decorator, you can use inner context like this
        ```python
        with elementary_test_context(asset=my_asset) as ctx:
            with ctx.boolean_test(name="has_data", severity="ERROR") as inner_ctx:
                inner_ctx.check_value(df.shape[0] > 0)
        ```
    """
    test_context = ElementaryTestContext(asset=asset, raise_on_error=raise_on_error)
    yield from _elementary_test_context(test_context)


# Thread-local storage for the active test context
_active_context: ContextVar[ElementaryTestContext | None] = ContextVar(
    "_active_context", default=None
)


def get_active_context() -> ElementaryTestContext | None:
    return _active_context.get()


def set_active_context(context: ElementaryTestContext | None) -> None:
    _active_context.set(context)
