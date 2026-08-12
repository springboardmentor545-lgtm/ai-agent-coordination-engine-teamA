import httpx
from langchain_core.tools import tool


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


def get_weather(city: str) -> dict:
    """Fetch current weather for a city using Open-Meteo."""

    if not city or not city.strip():
        raise ValueError("City name cannot be empty.")

    city = city.strip()

    try:
        with httpx.Client(timeout=10.0) as client:
            geo_response = client.get(
                GEOCODING_URL,
                params={
                    "name": city,
                    "count": 1,
                    "language": "en",
                    "format": "json",
                },
            )

            geo_response.raise_for_status()
            geo_data = geo_response.json()

            results = geo_data.get("results")

            if not results:
                raise ValueError(f"City '{city}' was not found.")

            location = results[0]

            weather_response = client.get(
                WEATHER_URL,
                params={
                    "latitude": location["latitude"],
                    "longitude": location["longitude"],
                    "current": (
                        "temperature_2m,"
                        "relative_humidity_2m,"
                        "wind_speed_10m"
                    ),
                },
            )

            weather_response.raise_for_status()
            weather_data = weather_response.json()

        current = weather_data.get("current")

        if not current:
            raise RuntimeError(
                "Weather data was not returned by the API."
            )

        return {
            "city": location["name"],
            "country": location.get("country"),
            "temperature": current["temperature_2m"],
            "humidity": current["relative_humidity_2m"],
            "wind_speed": current["wind_speed_10m"],
            "unit": weather_data["current_units"]["temperature_2m"],
        }

    except httpx.HTTPError as exc:
        raise RuntimeError(
            "Weather service is currently unavailable."
        ) from exc


@tool
def weather_tool(city: str) -> str:
    """Get the current weather for a city."""

    try:
        weather = get_weather(city)

        return (
            f"Weather in {weather['city']}, "
            f"{weather['country']}: "
            f"{weather['temperature']}{weather['unit']}, "
            f"humidity {weather['humidity']}%, "
            f"wind speed {weather['wind_speed']} km/h."
        )

    except (ValueError, RuntimeError) as exc:
        return f"Weather error: {exc}"