import time
import httpx


class CircuitBreakerOpenException(Exception):
    pass


class CircuitBreaker:

    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout: int = 10
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout

        self.failure_count = 0
        self.state = "CLOSED"
        self.last_failure_time = None


    def call(self, url: str):

        if self.state == "OPEN":

            if self.last_failure_time is None:
                raise CircuitBreakerOpenException(
                    "Circuit breaker is open"
                )

            elapsed = (
                time.time()
                - self.last_failure_time
            )

            if elapsed < self.recovery_timeout:
                raise CircuitBreakerOpenException(
                    "Circuit breaker is open"
                )

            self.state = "HALF_OPEN"

        try:

            response = httpx.get(
                url,
                timeout=5
            )

            response.raise_for_status()

            self.failure_count = 0
            self.state = "CLOSED"

            return response.json()

        except (
            httpx.TimeoutException,
            httpx.HTTPError
        ):

            self.failure_count += 1

            self.last_failure_time = time.time()

            if (
                self.failure_count
                >= self.failure_threshold
            ):
                self.state = "OPEN"

            raise