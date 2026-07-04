from fastapi import FastAPI

from app.clients.weather_client import get_weather
app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "OK"}

@app.get("/weather/{city_name}")
async def get_weather_owm(city_name: str):
    return await get_weather(city_name)