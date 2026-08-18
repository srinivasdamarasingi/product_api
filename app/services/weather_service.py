import httpx


def get_weather(city: str):

    response = httpx.get(
        f"https://api.example.com/weather/{city}",
        timeout=5.0
    )

    response.raise_for_status()

    return response.json()