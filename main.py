from fastapi import FastAPI, APIRouter

# from app.clients.weather_client import get_weather
from app.services.cache import get_cached
from app.schemas import WeatherResponse
app = FastAPI()

weather_router = APIRouter(prefix="/weather", tags=["weather"])

@app.get("/health")
async def health():
    return {"status": "OK"}

@weather_router.get("/{city_name}", response_model=WeatherResponse)
async def get_weather_owm(city_name: str):
    cached = await get_cached(city_name)
    return cached
app.include_router(weather_router)