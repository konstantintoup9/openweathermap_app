import pytest
import pytest_asyncio
import fakeredis

import httpx
from main import app

@pytest.fixture
async def async_client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def fake_redis():
    client = fakeredis.FakeAsyncRedis(decode_responses=True)
    yield client
    # Clean up and close connections after the test finishes
    await client.aclose()
