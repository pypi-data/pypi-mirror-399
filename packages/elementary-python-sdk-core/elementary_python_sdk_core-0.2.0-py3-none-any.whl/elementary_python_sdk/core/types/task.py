from datetime import datetime, timedelta
from typing import Literal

from elementary_python_sdk.core.types.asset import ElementaryVersionedModel


class TaskExecution(ElementaryVersionedModel):
    kind: Literal["task_execution"] = "task_execution"
    task_name: str
    job_name: str | None = None
    orcherstrator: str | None = None

    asset_ids: list[str] = []

    start_time: datetime
    duration_seconds: float

    @property
    def end_time(self) -> datetime:
        return self.start_time + timedelta(seconds=self.duration_seconds)
