import time

import requests

TIMEOUT = 30


def fetch(url, attempts=5):
    """Retry a flaky upstream call."""
    last = None
    for _ in range(attempts):
        try:
            return requests.get(url, timeout=TIMEOUT)
        except requests.RequestException as e:
            last = e
            time.sleep(1)
    raise last
