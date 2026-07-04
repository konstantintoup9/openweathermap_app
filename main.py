from fastapi import FastAPI, APIRouter

from app.clients.weather_client import get_weather
app = FastAPI()

weather_router = APIRouter(prefix="/weather", tags=["weather"])

@app.get("/health")
async def health():
    return {"status": "OK"}

@weather_router.get("/{city_name}")
async def get_weather_owm(city_name: str):
    return await get_weather(city_name)
app.include_router(weather_router)