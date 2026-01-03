from typing import Literal

from pydantic import BaseModel


class ElementaryBaseModel(BaseModel):
    kind: str


class ElementaryVersionedModel(ElementaryBaseModel):
    # Inheriting models can override this in case we want to support multiple versions
    version: Literal[1] = 1
