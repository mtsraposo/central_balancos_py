import logging

import pytest
from requests.models import Response
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException

from central_balancos_py.src.client.error_handler import ErrorHandler

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


def raise_error(error):
    raise error


def test_handle_http_errors(caplog):
    error_handler = ErrorHandler(logger=logger)

    with caplog.at_level(logging.ERROR):
        response = Response()
        response.status_code = 404
        error_handler(lambda: raise_error(HTTPError(response=response)))()
        assert 'error' in caplog.text


@pytest.mark.parametrize(
    "error",
    [ConnectionError, Timeout, RequestException, Exception]
)
def test_handle_errors(caplog, error):
    error_handler = ErrorHandler(logger=logger)

    with caplog.at_level(logging.ERROR):
        error_handler(lambda: raise_error(error))()
        assert 'error' in caplog.text
