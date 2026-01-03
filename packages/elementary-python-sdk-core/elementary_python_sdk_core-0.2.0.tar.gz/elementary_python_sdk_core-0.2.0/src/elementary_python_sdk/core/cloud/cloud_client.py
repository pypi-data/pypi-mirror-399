from datetime import datetime, timezone

import requests
from elementary_python_sdk.core.cloud.request import ElementaryCloudIngestRequest
from elementary_python_sdk.core.logger import get_logger
from elementary_python_sdk.core.test_context import TestContext

logger = get_logger()


class ElementaryCloudClient:
    """Client for sending collected test results to Elementary Cloud."""

    def __init__(self, project_id: str, api_key: str, url: str):
        """Create an Elementary Cloud client.

        Args:
            project_id: The id of the current project that sends the results to Elementary Cloud. Elementary cloud will use that id to identify changes between project runs.
            For example, if you don't send a table asset that was previously sent in this project, Elementary will assume it was deleted.
            api_key: Elementary API key.
            url: Elementary ingest endpoint URL.
        """
        self.project_id = project_id
        self.api_key = api_key
        self.url = url

    def send_to_cloud(self, test_context: TestContext):
        """Send all results collected in a test context to Elementary Cloud.

        This pulls Elementary objects from the context (assets, tests, executions), and POSTs it to the configured `url`.

        Args:
            test_context: A context created by `elementary_test_context(...)` (or any
                `TestContext` implementation) that contains collected results.

        Returns:
            The parsed JSON response body returned by the Elementary ingest endpoint.
            If the request failed, an elementary_error_code will be returned in the response body.
        """
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
