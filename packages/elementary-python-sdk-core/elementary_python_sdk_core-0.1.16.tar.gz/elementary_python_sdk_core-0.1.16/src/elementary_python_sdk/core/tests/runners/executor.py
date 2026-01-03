"""Common test execution logic for all test runners."""

import functools
import inspect
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Generic, TypeVar

import pytz
from elementary_python_sdk.core.logger import get_logger
from elementary_python_sdk.core.tests.context import get_active_context
from elementary_python_sdk.core.tests.runners.base import (
    CommonTestFields,
    TestRunner,
    TestRunnerParams,
)
from elementary_python_sdk.core.types.test import Test, TestExecution

logger = get_logger()

T = TypeVar("T")
TParams = TypeVar("TParams", bound=TestRunnerParams)
TResult = TypeVar("TResult")


@dataclass
class DecoratedFunctionExecution(Generic[TResult]):
    function_result: TResult | Exception
    start_time: datetime
    function_source_code: str | None


def execute_test(
    test_runner: TestRunner[TParams, TResult],
    params: TParams,
    common: CommonTestFields,
    argument: TResult | Exception | None,
    start_time: datetime | None = None,
    code: str | None = None,
    lazy: bool = False,
    skip: bool = False,
) -> None:
    start_time = start_time or datetime.now(pytz.utc)
    context = get_active_context()
    if context is None:
        logger.warning(
            f"No active context for test {common.name}, skipping test recording"
        )
        return

    asset_id = context.asset.id if context.asset else None

    tests = test_runner.resolve_tests(
        params=params,
        common=common,
        asset_id=asset_id,
    )

    for test in tests:
        context.register_test(test)
    if skip:
        # If the test is skipped, we don't need to execute it, but we still had to register the test in the context so it will be recorded and sent to Elementary Cloud
        return
    if isinstance(argument, Exception):
        if context.raise_on_error:
            raise argument
        for test in tests:
            context.record_error_execution(
                test=test,
                exception=argument,
                description="Exception raised when cacluting the test argument",
                start_time=start_time,
                code=code,
                quality_dimension=common.quality_dimension,
            )
    else:

        def execution_resolver(tests: list[Test]) -> list[TestExecution]:
            end_time = datetime.now(pytz.utc)
            duration_seconds = (end_time - start_time).total_seconds()
            return test_runner.resolve_test_results(
                tests=tests,
                params=params,
                test_argument=argument,
                start_time=start_time,
                duration_seconds=duration_seconds,
                code=code,
                common=common,
            )

        context.execute(tests, execution_resolver, lazy=lazy)


def _get_function_source(func: Callable) -> str | None:
    """Try to get the source code of a function.

    Args:
        func: Function to get source from

    Returns:
        Source code string or None if not available
    """
    try:
        return inspect.getsource(func)
    except (OSError, TypeError):
        return None


def execute_test_decorator(
    execute_test: Callable[[DecoratedFunctionExecution], None],
    func: Callable[..., T],
    test_name: str,
) -> Callable[..., T | None]:

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T | None:
        context = get_active_context()
        if context is None:
            logger.warning(
                f"No active context for test {test_name}, running without recording"
            )
            return func(*args, **kwargs)

        logger.info(f"Starting test: {test_name}")

        code = _get_function_source(func)
        start_time = datetime.now(pytz.utc)

        try:
            decorated_function_result: T | Exception = func(*args, **kwargs)
        except Exception as e:
            decorated_function_result = e

        execute_test(
            DecoratedFunctionExecution(decorated_function_result, start_time, code)
        )
        if isinstance(decorated_function_result, Exception):
            # If we got here after running execute_test, it means the error should be ignored, because otherwise the execute_test would have raised an exception and we wouldn't get here
            logger.error(
                "Exception raised when cacluting the test argument but the error was marked as ignored, decorator will return None instead of raising the exception"
            )
            return None
        return decorated_function_result

    return wrapper
