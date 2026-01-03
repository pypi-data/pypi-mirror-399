from typing import Literal

from elementary_python_sdk.core.logger import get_logger
from elementary_python_sdk.core.types.base import ElementaryVersionedModel

logger = get_logger()


class Asset(ElementaryVersionedModel):
    name: str
    description: str
    owners: list[str]
    tags: list[str]

    @property
    def id(self) -> str:
        return f"asset.{self.name}"


class TableAsset(Asset):
    kind: Literal["table_asset"] = "table_asset"
    db_type: str | None = None
    database_name: str
    schema_name: str
    table_name: str
    depends_on: list[str] | None = None
    metadata: dict | None = None

    @property
    def fqn(self) -> str:
        return f"{self.database_name}.{self.schema_name}.{self.table_name}"
