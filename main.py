from fastapi import FastAPI, HTTPException
import httpx
from pydantic import BaseModel, Field

from config import Config

class WeatherResponse(BaseModel):
    city: str = Field(max_length=30)
    weather: str = Field(max_length=30)
    temperature: float= Field(ge=-90.0)
    feels_temperature: float= Field(le=200.0)
app = FastAPI()

owm_api = Config.load().owm.WEATHERMAP_API.get_secret_value()

@app.get("/health")
async def health():
    return {"status": "OK"}


async def direct_geocoding(city_name: str, limit: int=1) -> tuple:
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit={limit}&appid={owm_api}"


    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response = response.json()

    if len(response) == 0: return -1, -1
    result = (response[0].get("lat"), response[0].get("lon"))
    return result

@app.get("/weather/{city_name}")
async def get_weather(city_name: str):
    lat, lon = await direct_geocoding(city_name)
    if (lat, lon) == (-1, -1): raise HTTPException(status_code=404, detail="Вы ввели несуществующий город, повторите попытку")

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={owm_api}&lang=ru"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response = response.json()


    result = WeatherResponse(
        city=city_name,
        weather=response.get("weather")[0].get("main"),
        temperature=response.get("main").get("temp"),
        feels_temperature=response.get("main").get("feels_like")
    )

    return result