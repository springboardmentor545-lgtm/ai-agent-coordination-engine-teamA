import pytest

from app.tools.weather import get_weather


def test_weather_returns_data():
    result = get_weather("Hyderabad")

    assert isinstance(result, dict)
    assert result["city"]
    assert "temperature" in result
    assert "humidity" in result
    assert "wind_speed" in result


def test_empty_city():
    with pytest.raises(ValueError, match="City name cannot be empty"):
        get_weather("")


def test_unknown_city():
    with pytest.raises(ValueError, match="was not found"):
        get_weather("ThisCityDefinitelyDoesNotExist123456")