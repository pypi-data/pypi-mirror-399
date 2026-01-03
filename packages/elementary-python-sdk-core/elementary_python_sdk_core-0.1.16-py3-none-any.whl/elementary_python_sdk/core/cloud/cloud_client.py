from datetime import datetime, timezone

import requests
from elementary_python_sdk.core.cloud.request import ElementaryCloudIngestRequest
from elementary_python_sdk.core.logger import get_logger
from elementary_python_sdk.core.test_context import TestContext

logger = get_logger()


class ElementaryCloudClient:
    def __init__(self, project_id: str, api_key: str, url: str):
        self.project_id = project_id
        self.api_key = api_key
        self.url = url

    def send_to_cloud(self, test_context: TestContext):
        objects = test_context.get_elementary_objects()
        request = ElementaryCloudIngestRequest(
            project=self.project_id,
            timestamp=datetime.now(timezone.utc),
            objects=objects,
        )
        logger.info(f"Sending request to {self.url}")
        response = requests.post(
            f"{self.url}",
            json=request.model_dump(mode="json"),
            headers={"Authorization": f"Bearer {self.api_key}"},
        )
        logger.info(f"Response status code: {response.status_code} from {self.url}")
        return response.json()
