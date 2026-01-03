"""Base classes for Python test runners."""

import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Callable, Generic, TypeVar

import pytz
from elementary_python_sdk.core.types.test import (
    QualityDimension,
    Test,
    TestExecution,
    TestExecutionStatus,
    TestSeverity,
    TestType,
)
from pydantic import BaseModel


class TestRunnerParams(BaseModel, ABC):
    """Base class for test-specific parameters.

    Each test type should define its own params class inheriting from this.
    For example: ExpectedRangeParams(min, max), BooleanTestParams(), etc.
    """

    pass


class CommonTestFields(BaseModel):
    """Common fields shared by all test types.

    These fields are applicable to all tests regardless of type.
    """

    name: str
    description: str | None = None
    tags: list[str] | None = None
    owners: list[str] | None = None
    metadata: dict | None = None
    column_name: str | None = None
    quality_dimension: QualityDimension | None = None
    severity: TestSeverity = TestSeverity.ERROR


class TestRunnerResult(BaseModel):
    status: TestExecutionStatus
    description: str
    failure_count: int


TParams = TypeVar("TParams", bound=TestRunnerParams)
TArgument = TypeVar("TArgument")


def _serialize_value(value: Any) -> str:
    try:
        return json.dumps(value, sort_keys=True, default=str)
    except Exception:
        return str(type(value).__name__)


class TestRunner(ABC, Generic[TParams, TArgument]):

    @abstractmethod
    def validate_test_argument(self, test_argument: Any, params: TParams) -> TArgument:
        pass

    @abstractmethod
    def resolve_tests(
        self,
        params: TParams,
        common: CommonTestFields,
        asset_id: str | None,
    ) -> list[Test]:
        pass

    @abstractmethod
    def resolve_test_results(
        self,
        tests: list[Test],
        params: TParams,
        test_argument: Any,
        start_time: datetime,
        duration_seconds: float,
        code: str | None,
        common: CommonTestFields,
    ) -> list[TestExecution]:
        pass


class SingleResultTestRunner(TestRunner[TParams, TArgument]):

    @abstractmethod
    def build_result(
        self,
        test_argument: TArgument,
        params: TParams,
        common: CommonTestFields,
    ) -> TestRunnerResult:
        pass

    def get_test_type(self) -> TestType:
        return TestType.PYTHON

    def get_default_quality_dimension(
        self,
        common: CommonTestFields,
    ) -> QualityDimension | None:
        return None

    def get_config(
        self,
        params: TParams,
        func: Callable,
        func_args: tuple,
        func_kwargs: dict,
    ) -> dict:
        config = {
            "function": func.__name__,
            "args": [_serialize_value(arg) for arg in func_args],
            "kwargs": {k: _serialize_value(v) for k, v in func_kwargs.items()},
        }

        for key, value in params.model_dump().items():
            if not callable(value):
                config[key] = value

        return config

    def _generate_test_id(
        self,
        test_name: str,
        asset_id: str | None,
    ) -> str:
        test_type = self.get_test_type().value.replace("python_", "")
        base_id = f"{test_type}.{test_name}"

        if asset_id:
            return f"test.[{asset_id}].{base_id}"
        else:
            return f"test.{base_id}"

    def resolve_tests(
        self,
        params: TParams,
        common: CommonTestFields,
        asset_id: str | None,
    ) -> list[Test]:
        test_id = self._generate_test_id(common.name, asset_id)

        test = Test(
            id=test_id,
            name=common.name,
            test_type=self.get_test_type(),
            asset_id=asset_id,
            description=common.description,
            column_name=common.column_name,
            severity=common.severity,
            config=params.model_dump(),
            meta=common.metadata,
            tags=common.tags,
            owners=common.owners,
        )

        return [test]

    def resolve_test_results(
        self,
        tests: list[Test],
        params: TParams,
        test_argument: Any,
        start_time: datetime,
        duration_seconds: float,
        code: str | None,
        common: CommonTestFields,
    ) -> list[TestExecution]:
        test = tests[0]
        start_time = datetime.now(pytz.utc)
        validated_test_argument = self.validate_test_argument(test_argument, params)
        test_result = self.build_result(validated_test_argument, params, common)
        quality_dim = common.quality_dimension or self.get_default_quality_dimension(
            common
        )

        execution = TestExecution(
            test_id=test.id,
            test_sub_unique_id=test.id,
            sub_type=self.get_test_type().value,
            failure_count=test_result.failure_count,
            status=test_result.status,
            code=code,
            start_time=start_time,
            duration_seconds=duration_seconds,
            description=test_result.description,
            column_name=common.column_name,
            quality_dimension=quality_dim,
        )

        return [execution]
