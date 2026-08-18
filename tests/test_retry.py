from unittest.mock import patch
import httpx

def test_retry_success(client):

    fake_response = {
        "status": "success"
    }

    with patch(
        "app.services.retry_service.httpx.get"
    ) as mock_get:

        mock_get.return_value.json.return_value = (
            fake_response
        )

        mock_get.return_value.raise_for_status.return_value = None

        response = client.get(
            "/retry/"
        )

    assert response.status_code == 200

    assert response.json() == fake_response

    import httpx


def test_retry_after_timeout(client):

    fake_response = {
        "status": "success"
    }

    with patch(
        "app.services.retry_service.httpx.get"
    ) as mock_get:

        mock_get.side_effect = [

            httpx.TimeoutException("Request timed out"),

            httpx.TimeoutException("Request timed out"),

            mock_get.return_value
        ]

        mock_get.return_value.json.return_value = (
            fake_response
        )

        mock_get.return_value.raise_for_status.return_value = None

        response = client.get(
            "/retry/"
        )

    assert response.status_code == 200

    assert mock_get.call_count == 3

def test_exponential_backoff(client):

    fake_response = {
        "status": "success"
    }

    with patch(
        "app.services.retry_service.httpx.get"
    ) as mock_get, patch(
        "app.services.retry_service.time.sleep"
    ) as mock_sleep:

        mock_get.side_effect = [
            httpx.TimeoutException(
                "Attempt 1 timed out"
            ),

            httpx.TimeoutException(
                "Attempt 2 timed out"
            ),

            mock_get.return_value
        ]

        mock_get.return_value.raise_for_status.return_value = None

        mock_get.return_value.json.return_value = (
            fake_response
        )

        response = client.get("/retry/")

    assert response.status_code == 200

    assert response.json() == fake_response

    assert mock_get.call_count == 3

def test_retry_exhausted(error_client):

    with patch(
        "app.services.retry_service.httpx.get",
        side_effect=httpx.TimeoutException(
            "External API unavailable"
        )
    ) as mock_get, patch(
        "app.services.retry_service.time.sleep"
    ) as mock_sleep:

        response = error_client.get("/retry/")

    assert response.status_code == 500

    assert mock_get.call_count == 3

    assert mock_sleep.call_count == 2

    mock_sleep.assert_any_call(1.0)
    mock_sleep.assert_any_call(2.0)