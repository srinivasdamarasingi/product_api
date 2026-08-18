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