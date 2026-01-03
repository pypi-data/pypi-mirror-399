"""Expected values test decorator implementation."""

from datetime import datetime
from typing import Any, Callable, Iterable, TypeVar

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

T = TypeVar("T")

MAX_VALUES_IN_DESCRIPTION = 5


class ExpectedValuesParams(TestRunnerParams):
    expected: list[Any]
    allow_none: bool = False


class ExpectedValuesRunner(SingleResultTestRunner[ExpectedValuesParams, Iterable[Any]]):
    def validate_test_argument(
        self, test_argument: Any, params: ExpectedValuesParams
    ) -> Iterable[Any]:
        return (
            test_argument
            if isinstance(test_argument, Iterable)
            else list([test_argument])
        )

    def build_result(
        self,
        test_argument: Iterable[Any],
        params: ExpectedValuesParams,
        common: CommonTestFields,
    ) -> TestRunnerResult:
        non_matched_values = [
            value for value in test_argument if value not in params.expected
        ]
        status = (
            TestExecutionStatus.FAIL if non_matched_values else TestExecutionStatus.PASS
        )
        failure_count = len(non_matched_values)
        unique_non_matched_values = list(set(non_matched_values))[
            :MAX_VALUES_IN_DESCRIPTION
        ]

        description = (
            f"All values matched expected values {params.expected}"
            if status == TestExecutionStatus.PASS
            else f"{failure_count} values do not match expected value {params.expected}. Examples for non-matched values: {unique_non_matched_values}"
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
        return QualityDimension.ACCURACY


def execute_expected_values_test(
    name: str,
    expected: list[Any],
    test_argument: Any | Exception,
    allow_none: bool = False,
    start_time: datetime | None = None,
    code: str | None = None,
    severity: TestSeverity = TestSeverity.ERROR,
    description: str | None = None,
    tags: list[str] | None = None,
    owners: list[str] | None = None,
    metadata: dict | None = None,
    column_name: str | None = None,
    quality_dimension: QualityDimension | None = None,
    skip: bool = False,
) -> None:

    test_runner = ExpectedValuesRunner()
    params = ExpectedValuesParams(expected=expected, allow_none=allow_none)
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


def expected_values(
    name: str,
    expected: Any,
    allow_none: bool = False,
    severity: TestSeverity = TestSeverity.ERROR,
    description: str | None = None,
    metadata: dict | None = None,
    tags: list[str] | None = None,
    owners: list[str] | None = None,
    column_name: str | None = None,
    quality_dimension: QualityDimension | None = None,
    skip: bool = False,
) -> Callable[[Callable[..., T]], Callable[..., T | None]]:

    def decorator(func: Callable[..., T]) -> Callable[..., T | None]:
        def execute_test(
            decorated_function_execution: DecoratedFunctionExecution,
        ) -> None:
            execute_expected_values_test(
                name=name,
                expected=expected,
                test_argument=decorated_function_execution.function_result,
                allow_none=allow_none,
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
