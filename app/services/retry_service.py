import httpx
import time


def fetch_data(url: str):

    retries = 3

    for attempt in range(retries):

        try:

            response = httpx.get(
                url,
                timeout=5
            )

            response.raise_for_status()

            return response.json()

        except httpx.TimeoutException:

            if attempt == retries - 1:
                raise

            time.sleep(1)