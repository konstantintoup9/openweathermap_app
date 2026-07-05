import httpx

from fastapi import HTTPException
import logging
from app.schemas import WeatherResponse

from config import Config
import time

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

async def connect_to_weather_server(url: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()  # The response contains the status returned by the server
            data = response.json()
        except httpx.TimeoutException as te:
            logging.error(f"Timeout error")
            raise HTTPException(status_code=504, detail=f"Timeout error")
        except httpx.RequestError as re: # Запрос НЕ ДОШЕЛ до сервера
            logging.error(f"Network error {type(re).__name__}")
            raise HTTPException(status_code=500, detail="Network error")
        except httpx.HTTPStatusError as exc: # The server responded with an error code
            status = exc.response.status_code
            logging.error(f"External API error: {status}")
            match status:
                case 404: raise HTTPException(status_code=404, detail="Not found")
                case 401 | 403: raise HTTPException(status_code=500, detail="Service configuration error")
                case _: raise HTTPException(status_code=502, detail="Upstream service error")

    if not data:
        raise HTTPException(status_code=404, detail="City not found")

    return data

async def direct_geocoding(city_name: str, limit: int=1) -> tuple:
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit={limit}&appid={Config.load().owm.WEATHERMAP_API.get_secret_value()}"

    data = await connect_to_weather_server(url=url)
    result = (data[0].get("lat"), data[0].get("lon"))
    return result


async def get_weather(city_name: str):
    lat, lon = await direct_geocoding(city_name)

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={Config.load().owm.WEATHERMAP_API.get_secret_value()}&lang=ru"

    time.sleep(5)
    data = await connect_to_weather_server(url=url)

    result = WeatherResponse(
        city=city_name,
        weather=data.get("weather")[0].get("main"),
        temperature=data.get("main").get("temp"),
        feels_temperature=data.get("main").get("feels_like")
    )

    return result.model_dump_json()