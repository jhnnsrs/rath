import requests
from requests.exceptions import ConnectionError
import time


class RetryExceededError(Exception):
    pass


def wait_for_http_response(url, status_code=200, retry=0, max_retries=10):
    if retry > max_retries:
        raise RetryExceededError("Max retries exceeded")
    time.sleep(retry * retry * 0.5)
    try:
        response = requests.get(url)
        assert response.status_code == status_code, "Did not get expected response code"
        return response
    except (ConnectionResetError, AssertionError, ConnectionError) as c:
        return wait_for_http_response(
            url, status_code, retry + 1, max_retries=max_retries
        )
