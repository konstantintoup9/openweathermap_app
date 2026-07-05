import httpx
from pydantic import BaseModel, Field
from fastapi import HTTPException
import logging

from config import Config

logging.basicConfig(level=logging.INFO)

class WeatherResponse(BaseModel):
    city: str = Field(max_length=30)
    weather: str = Field(max_length=30)
    temperature: float= Field(ge=-90.0)
    feels_temperature: float= Field(le=200.0)

async def connect_to_weather_server(url: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()  # В теле ответа есть возвращаемый сервером статус
            data = response.json()
        except httpx.TimeoutException as te:
            logging.error(f"Timeout error")
            raise HTTPException(status_code=504, detail=f"Timeout error")
        except httpx.RequestError as re: # Запрос НЕ ДОШЕЛ до сервера
            logging.error(f"Network error {type(re).__name__}")
            raise HTTPException(status_code=500, detail="Network error")
        except httpx.HTTPStatusError as exc: # Сервер ответил с плохим кодом
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

    data = await connect_to_weather_server(url=url)

    result = WeatherResponse(
        city=city_name,
        weather=data.get("weather")[0].get("main"),
        temperature=data.get("main").get("temp"),
        feels_temperature=data.get("main").get("feels_like")
    )

    return result