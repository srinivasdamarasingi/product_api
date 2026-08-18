import time
import httpx


def fetch_data(
    url: str,
    retries: int = 3,
    base_delay: float = 1.0
):

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

            delay = base_delay * (2 ** attempt)

            time.sleep(delay)