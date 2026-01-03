from abc import ABC, abstractmethod

from elementary_python_sdk.core.cloud.request import ElementaryObject


class TestContext(ABC):

    @abstractmethod
    def get_elementary_objects(self) -> list[ElementaryObject]:
        pass
