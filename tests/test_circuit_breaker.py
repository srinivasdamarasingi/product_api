import httpx

from unittest.mock import patch

from app.routers.circuit import breaker


def reset_breaker():

    breaker.failure_count = 0
    breaker.state = "CLOSED"
    breaker.last_failure_time = None


def test_circuit_breaker_success(client):

    reset_breaker()

    fake_response = {
        "status": "success"
    }

    with patch(
        "app.services.circuit_breaker.httpx.get"
    ) as mock_get:

        mock_get.return_value.raise_for_status.return_value = None

        mock_get.return_value.json.return_value = (
            fake_response
        )

        response = client.get(
            "/circuit/"
        )

    assert response.status_code == 200

    assert response.json() == fake_response

    assert breaker.state == "CLOSED"

    assert breaker.failure_count == 0

def test_circuit_breaker_opens_after_three_failures(
    error_client
):

    reset_breaker()

    with patch(
        "app.services.circuit_breaker.httpx.get",
        side_effect=httpx.TimeoutException(
            "External API timed out"
        )
    ) as mock_get:

        for _ in range(3):

            response = error_client.get(
                "/circuit/"
            )

            assert response.status_code == 500

        assert breaker.state == "OPEN"

        assert breaker.failure_count == 3

        assert mock_get.call_count == 3

def test_open_circuit_blocks_request(client):

    breaker.failure_count = 3
    breaker.state = "OPEN"
    breaker.last_failure_time = 9999999999

    with patch(
        "app.services.circuit_breaker.httpx.get"
    ) as mock_get:

        response = client.get(
            "/circuit/"
        )

    assert response.status_code == 503

    assert mock_get.call_count == 0

def test_half_open_recovers_on_success(client):

    reset_breaker()

    breaker.failure_count = 3
    breaker.state = "OPEN"
    breaker.last_failure_time = 100

    fake_response = {
        "status": "recovered"
    }

    with patch(
        "app.services.circuit_breaker.time.time",
        return_value=111
    ), patch(
        "app.services.circuit_breaker.httpx.get"
    ) as mock_get:

        mock_get.return_value.raise_for_status.return_value = None

        mock_get.return_value.json.return_value = fake_response

        response = client.get("/circuit/")

    assert response.status_code == 200

    assert response.json() == fake_response

    assert breaker.state == "CLOSED"

    assert breaker.failure_count == 0

    assert mock_get.call_count == 1

def test_half_open_failure_reopens_circuit(error_client):

    reset_breaker()

    breaker.failure_count = 3
    breaker.state = "OPEN"
    breaker.last_failure_time = 100

    with patch(
        "app.services.circuit_breaker.time.time",
        return_value=111
    ), patch(
        "app.services.circuit_breaker.httpx.get",
        side_effect=httpx.TimeoutException(
            "Service still unavailable"
        )
    ) as mock_get:

        response = error_client.get("/circuit/")

    assert response.status_code == 500

    assert breaker.state == "OPEN"

    assert mock_get.call_count == 1