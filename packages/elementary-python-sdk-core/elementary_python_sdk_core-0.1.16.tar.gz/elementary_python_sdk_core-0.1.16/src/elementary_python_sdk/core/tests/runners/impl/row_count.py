"""Row count test decorator implementation."""

from collections.abc import Sized
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


class RowCountParams(TestRunnerParams):
    min: int | None = None
    max: int | None = None


class RowCountRunner(SingleResultTestRunner[RowCountParams, Sized]):

    def validate_test_argument(
        self, test_argument: Any, params: RowCountParams
    ) -> Sized:
        if not isinstance(test_argument, Sized):
            raise TypeError(
                f"Row count test must return a Sized object (with __len__), "
                f"got {type(test_argument).__name__}"
            )
        return test_argument

    def build_result(
        self,
        test_argument: Sized,
        params: RowCountParams,
        common: CommonTestFields,
    ) -> TestRunnerResult:
        count = len(test_argument)
        in_range = (params.min is None or count >= params.min) and (
            params.max is None or count <= params.max
        )

        status = TestExecutionStatus.PASS if in_range else TestExecutionStatus.FAIL
        failure_count = 0 if in_range else 1

        range_str = f"[{params.min if params.min is not None else 0}, {params.max if params.max is not None else float('inf')}]"
        description = (
            f"Row count {count} is within expected range {range_str}"
            if in_range
            else f"Row count {count} is outside expected range {range_str}"
        )

        return TestRunnerResult(
            status=status,
            description=description,
            failure_count=failure_count,
        )

    def get_default_quality_dimension(
        self,
        common: CommonTestFields,
    ) -> QualityDimension | None:
        return QualityDimension.COMPLETENESS


def execute_row_count_test(
    name: str,
    test_argument: Sized | Exception,
    min: int | None = None,
    max: int | None = None,
    start_time: datetime | None = None,
    code: str | None = None,
    severity: TestSeverity = TestSeverity.ERROR,
    description: str | None = None,
    metadata: dict | None = None,
    tags: list[str] | None = None,
    owners: list[str] | None = None,
    skip: bool = False,
) -> None:

    test_runner = RowCountRunner()
    params = RowCountParams(min=min, max=max)
    common = CommonTestFields(
        name=name,
        description=description,
        tags=tags,
        owners=owners,
        metadata=metadata,
        column_name=None,
        quality_dimension=QualityDimension.COMPLETENESS,
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


def row_count(
    name: str,
    min: int | None = None,
    max: int | None = None,
    severity: TestSeverity = TestSeverity.ERROR,
    description: str | None = None,
    metadata: dict | None = None,
    tags: list[str] | None = None,
    owners: list[str] | None = None,
    skip: bool = False,
) -> Callable[[Callable[..., Sized]], Callable[..., Sized | None]]:

    def decorator(func: Callable[..., Sized]) -> Callable[..., Sized | None]:
        def execute_test(
            decorated_function_execution: DecoratedFunctionExecution,
        ) -> None:
            execute_row_count_test(
                name=name,
                test_argument=decorated_function_execution.function_result,
                min=min,
                max=max,
                start_time=decorated_function_execution.start_time,
                code=decorated_function_execution.function_source_code,
                severity=severity,
                description=description,
                metadata=metadata,
                tags=tags,
                owners=owners,
                skip=skip,
            )

        return execute_test_decorator(execute_test, func, name)

    return decorator
