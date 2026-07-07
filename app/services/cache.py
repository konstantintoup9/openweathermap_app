import redis.asyncio as aioredis # Separately aioredis not needed
from redis.exceptions import ConnectionError, TimeoutError
from typing import Any
import json
from app.clients.weather_client import get_weather
import logging

from config import Config

redis_client = aioredis.Redis(
    host=Config.load().redis.HOST.get_secret_value(),
    port=6379, # default Redis-port, checked in terminal
    db=0,
    decode_responses=True, # return str, not bytes
)

async def get_cached(city_name: str) -> Any | None:
    try:
        cached = await redis_client.get(f"weather:{city_name}")
        if cached:
            logging.info(f"Cache HIT {city_name}")
            return json.loads(cached)
    except (ConnectionError, TimeoutError) as e:
        logging.error(f"Redis unavailable {type(e).__name__}. Falling back to database")


    logging.info(f"Cache MISS {city_name}")
    weather = await get_weather(city_name)
    try:
        await redis_client.set(f"weather:{city_name}", weather, ex=600)
    except (ConnectionError, TimeoutError) as e:
        pass # Ignore error during write back
    return json.loads(weather)
