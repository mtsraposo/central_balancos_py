import logging
from unittest.mock import patch

import pytest
import requests

from central_balancos_py.src.client.http import HttpClient
from central_balancos_py.src.client.error_handler import ErrorHandler

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


class MockResponse(requests.Response):
    def __init__(self, status_code):
        super().__init__()
        self.status_code = status_code


def mocked_requests_get(status_code):
    return MockResponse(status_code)


@pytest.mark.parametrize(
    "status_code, expected_result",
    [
        (200, True),
        (400, False),
        (500, False),
    ]
)
def test_get(caplog, status_code, expected_result):
    with caplog.at_level(logging.ERROR):
        with patch('central_balancos_py.src.client.http.requests.get') as mock_get:
            mock_get.return_value = mocked_requests_get(status_code)

            client = HttpClient(error_handler=ErrorHandler(logger=logger))
            client.get('https://example.com')
            if status_code != 200:
                assert f"HTTP error with status code {status_code}:" in caplog.text
