"""Boolean test decorator implementation."""

from datetime import datetime
from typing import Any, Callable

from elementary_python_sdk.core.tests.runners.base import (
    CommonTestFields,
    SingleResultTestRunner,
    TestRunnerParams,
    TestRunnerResult,
)
from elementary_python_sdk.core.tests.runners.executor import (
    DecoratedFunctionExecution,
    execute_test,
    execute_test_decorator,
)
from elementary_python_sdk.core.types.test import (
    QualityDimension,
    TestExecutionStatus,
    TestSeverity,
)

try:
    from numpy import bool_ as numpy_bool  # type: ignore[import-not-found]

    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


class BooleanTestParams(TestRunnerParams):
    pass


class BooleanTestRunner(SingleResultTestRunner[BooleanTestParams, bool]):

    def validate_test_argument(
        self, test_argument: Any, params: BooleanTestParams
    ) -> bool:
        if isinstance(test_argument, bool):
            return test_argument

        if HAS_NUMPY and isinstance(test_argument, numpy_bool):
            return bool(test_argument)

        raise TypeError(
            f"Boolean test must return bool, got {type(test_argument).__name__}"
        )

    def build_result(
        self,
        test_argument: bool,
        params: BooleanTestParams,
        common: CommonTestFields,
    ) -> TestRunnerResult:
        status = TestExecutionStatus.PASS if test_argument else TestExecutionStatus.FAIL
        failure_count = 0 if test_argument else 1

        description = common.description or ""

        return TestRunnerResult(
            status=status,
            description=description,
            failure_count=failure_count,
        )

    def get_default_quality_dimension(
        self,
        common: CommonTestFields,
    ) -> QualityDimension | None:
        return QualityDimension.VALIDITY if common.column_name else None


def execute_boolean_test(
    name: str,
    test_argument: bool | Exception,
    start_time: datetime | None = None,
    code: str | None = None,
    severity: TestSeverity = TestSeverity.ERROR,
    description: str | None = None,
    metadata: dict | None = None,
    tags: list[str] | None = None,
    owners: list[str] | None = None,
    column_name: str | None = None,
    quality_dimension: QualityDimension | None = None,
    skip: bool = False,
) -> None:
    test_runner = BooleanTestRunner()
    params = BooleanTestParams()
    common = CommonTestFields(
        name=name,
        description=description,
        tags=tags,
        owners=owners,
        metadata=metadata,
        column_name=column_name,
        quality_dimension=quality_dimension,
        severity=severity,
    )

    execute_test(
        test_runner=test_runner,
        params=params,
        common=common,
        argument=test_argument,
        start_time=start_time,
        code=code,
        skip=skip,
    )


def boolean_test(
    name: str,
    severity: TestSeverity = TestSeverity.ERROR,
    description: str | None = None,
    tags: list[str] | None = None,
    owners: list[str] | None = None,
    metadata: dict | None = None,
    column_name: str | None = None,
    quality_dimension: QualityDimension | None = None,
    skip: bool = False,
) -> Callable[[Callable[..., bool]], Callable[..., bool | None]]:

    def decorator(func: Callable[..., bool]) -> Callable[..., bool | None]:
        def execute_test(
            decorated_function_execution: DecoratedFunctionExecution,
        ) -> None:
            execute_boolean_test(
                name=name,
                test_argument=decorated_function_execution.function_result,
                start_time=decorated_function_execution.start_time,
                code=decorated_function_execution.function_source_code,
                severity=severity,
                description=description,
                tags=tags,
                owners=owners,
                metadata=metadata,
                column_name=column_name,
                quality_dimension=quality_dimension,
                skip=skip,
            )

        return execute_test_decorator(execute_test, func, name)

    return decorator
