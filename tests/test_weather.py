import httpx
from unittest.mock import patch

def test_weather_api(client):

    fake_response = {
        "city": "Hyderabad",
        "temperature": 32
    }

    with patch(
        "app.services.weather_service.httpx.get"
    ) as mock_get:

        mock_get.return_value.json.return_value = (
            fake_response
        )

        response = client.get(
            "/weather/Hyderabad"
        )

    assert response.status_code == 200

    assert response.json() == fake_response

def test_weather_timeout(error_client):

    with patch(
        "app.services.weather_service.httpx.get",
        side_effect=httpx.TimeoutException(
            "Weather API timeout"
        )
    ):

        response = error_client.get(
            "/weather/Hyderabad"
        )

    assert response.status_code == 500

def test_weather_external_api_500(error_client):

    request = httpx.Request(
        "GET",
        "https://api.example.com/weather/Hyderabad"
    )

    external_response = httpx.Response(
        500,
        request=request
    )

    with patch(
        "app.services.weather_service.httpx.get",
        return_value=external_response
    ):

        response = error_client.get(
            "/weather/Hyderabad"
        )

    assert response.status_code == 500