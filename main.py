from fastapi import FastAPI
import httpx
from pydantic import BaseModel, Field

from dotenv import load_dotenv
import os

class WeatherResponse(BaseModel):
    city: str = Field(max_length=30)
    weather: str = Field(max_length=30)
    temperature: float= Field(ge=-90.0)
    feels_temperature: float= Field(le=200.0)
app = FastAPI()

load_dotenv()
owm_api = os.getenv("OPENWEATHERMAP_API")
@app.get("/health")
async def health():
    return {"status": "OK"}


async def direct_geocoding(city_name: str, limit: int=1) -> tuple:
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit={limit}&appid={owm_api}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response = response.json()

    result = (response[0].get("lat"), response[0].get("lon"))
    return result

@app.get("/{city_name}")
async def get_weather(city_name: str):
    lat, lon = await direct_geocoding(city_name)
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={owm_api}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response = response.json()

    result = WeatherResponse(
        city=city_name,
        weather=response.get("weather")[0].get("main"),
        temperature=round(float(response.get("main").get("temp")) - 273.15, 2),
        feels_temperature=round(float(response.get("main").get("feels_like")) - 273.15, 2)
    )

    return result