"""Expected range test decorator implementation."""

from datetime import datetime
from typing import Any, Callable, Iterable

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


class ExpectedRangeParams(TestRunnerParams):
    min: float | None = None
    max: float | None = None


class ExpectedRangeRunner(SingleResultTestRunner[ExpectedRangeParams, Iterable[float]]):
    def try_cast_to_float(self, test_argument: Any) -> float:
        try:
            return float(test_argument)
        except (TypeError, ValueError):
            raise TypeError(
                f"Range test must return numeric value, got {type(test_argument).__name__}"
            )

    def validate_test_argument(
        self, test_argument: Any, params: ExpectedRangeParams
    ) -> list[float]:
        if isinstance(test_argument, Iterable):
            return [self.try_cast_to_float(value) for value in test_argument]
        return [self.try_cast_to_float(test_argument)]

    def is_in_range(self, value: float, params: ExpectedRangeParams) -> bool:
        return (params.min is None or value >= params.min) and (
            params.max is None or value <= params.max
        )

    def build_result(
        self,
        test_argument: Iterable[float],
        params: ExpectedRangeParams,
        common: CommonTestFields,
    ) -> TestRunnerResult:
        values_outside_range = [
            value for value in test_argument if not self.is_in_range(value, params)
        ]
        status = (
            TestExecutionStatus.FAIL
            if values_outside_range
            else TestExecutionStatus.PASS
        )
        failure_count = len(values_outside_range)
        range_str = f"[{params.min if params.min is not None else '-∞'}, {params.max if params.max is not None else '∞'}]"
        description = (
            f"{failure_count} values are outside expected range {range_str}. For example: {values_outside_range[0]}"
            if status == TestExecutionStatus.FAIL
            else f"All values are in the expected range {range_str}"
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
        return QualityDimension.VALIDITY


def execute_expected_range_test(
    name: str,
    test_argument: Iterable[float] | Exception,
    min: float | None = None,
    max: float | None = None,
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

    test_runner = ExpectedRangeRunner()
    params = ExpectedRangeParams(min=min, max=max)
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


def expected_range(
    name: str,
    min: float | None = None,
    max: float | None = None,
    severity: TestSeverity = TestSeverity.ERROR,
    description: str | None = None,
    metadata: dict | None = None,
    tags: list[str] | None = None,
    owners: list[str] | None = None,
    column_name: str | None = None,
    quality_dimension: QualityDimension | None = None,
    skip: bool = False,
) -> Callable[[Callable[..., float]], Callable[..., float | None]]:

    def decorator(func: Callable[..., float]) -> Callable[..., float | None]:
        def execute_test(
            decorated_function_execution: DecoratedFunctionExecution,
        ) -> None:
            execute_expected_range_test(
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
                column_name=column_name,
                quality_dimension=quality_dimension,
                skip=skip,
            )

        return execute_test_decorator(execute_test, func, name)

    return decorator
