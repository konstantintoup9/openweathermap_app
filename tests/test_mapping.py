from app.clients.weather_client import map_weather_response

def test_map_weather_response_happy_path():
    fake_data = {
        "weather": [{"main": "Clear"}],
        "main": {"temp": 20.0, "feels_like": 18.0}
    }

    result = map_weather_response("London", fake_data)

    assert result.city == "London"
    assert result.weather == "Clear"
    assert result.temperature == 20.0
    assert result.feels_temperature == 18.0