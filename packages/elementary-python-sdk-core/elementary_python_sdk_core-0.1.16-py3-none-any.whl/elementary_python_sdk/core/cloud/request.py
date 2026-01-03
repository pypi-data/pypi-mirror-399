from __future__ import annotations

from datetime import datetime
from typing import Annotated, Union

from elementary_python_sdk.core.types.asset import TableAsset
from elementary_python_sdk.core.types.test import Test, TestExecution
from pydantic import BaseModel, Field

ElementaryObject = Annotated[
    Union[TableAsset, Test, TestExecution],
    Field(discriminator="kind"),
]


class ElementaryCloudIngestRequest(BaseModel):
    project: str
    timestamp: datetime
    objects: list[ElementaryObject]


class ElementaryCloudIngestError(BaseModel):
    status_code: int
    error: str
