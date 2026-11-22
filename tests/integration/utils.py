import time

import requests
from requests.exceptions import ConnectionError


class RetryExceededError(Exception):
    pass


def wait_for_http_response(
    url: str, status_code: int = 200, retry: int = 0, max_retries: int = 10
) -> requests.Response:
    if retry > max_retries:
        raise RetryExceededError("Max retries exceeded")
    time.sleep(retry * retry * 0.5)
    try:
        response = requests.get(url)
        assert response.status_code == status_code, "Did not get expected response code"
        return response
    except (ConnectionResetError, AssertionError, ConnectionError):
        return wait_for_http_response(
            url, status_code, retry + 1, max_retries=max_retries
        )
