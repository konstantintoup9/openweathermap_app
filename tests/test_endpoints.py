import respx
import httpx

import app.services.cache


async def test_health(async_client):
    response = await async_client.get("/health")

    assert response.status_code == 200

async def test_weather_happy_path(async_client, fake_redis, monkeypatch):
    monkeypatch.setattr("app.services.cache.redis_client", fake_redis)

    with respx.mock:
        respx.get(url__startswith="http://api.openweathermap.org/geo").mock(
            return_value = httpx.Response(200, json=[{"lat": 51.5, "lon": -0.1}])
        )
        respx.get(url__startswith="https://api.openweathermap.org/data").mock(
            return_value = httpx.Response(200, json={
                "weather": [{"main": "Clear"}],
                "main": {"temp": 20.0, "feels_like": 18.0}
            })
        )

        response = await async_client.get("/weather/London")

        assert response.status_code == 200
        assert response.json()["city"] == "London"
        assert response.json()["temperature"] == 20.0


async def test_weather_city_not_found(async_client, fake_redis, monkeypatch):
    monkeypatch.setattr("app.services.cache.redis_client", fake_redis)

    with respx.mock:
        respx.get(url__startswith="http://api.openweathermap.org/geo").mock(
            return_value = httpx.Response(status_code=200, json=[])
        )

        response = await async_client.get("/weather/UnexistingCity")

        assert response.status_code == 404

async def test_weather_timeout(async_client, fake_redis, monkeypatch):
    monkeypatch.setattr("app.services.cache.redis_client", fake_redis)

    with respx.mock:
        respx.get(url__startswith="http://api.openweathermap.org/geo").mock(
            side_effect = httpx.TimeoutException("Timeout error")
        )

        response = await async_client.get("/weather/London")
        assert response.status_code == 504

async def test_weather_upstream_error(async_client, fake_redis, monkeypatch):
    monkeypatch.setattr("app.services.cache.redis_client", fake_redis)

    with respx.mock:
        respx.get(url__startswith="http://api.openweathermap.org/geo").mock(
            return_value=httpx.Response(200, json=[{"lat": 51.5, "lon": -0.1}])
        )

        respx.get(url__startswith="https://api.openweathermap.org/data").mock(
            return_value = httpx.Response(status_code=500)
        )

        response = await async_client.get("/weather/London")
        assert response.status_code == 502