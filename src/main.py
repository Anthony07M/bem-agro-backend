from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from redis.asyncio import Redis
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from src.config import settings
from src.infrastructure.services.open_weather_client import OpenWeatherClient
from src.presentation.rate_limiter import limiter
from src.presentation.routers import history, status, weather

HTTP_CLIENT_TIMEOUT_SECONDS = 10.0


@asynccontextmanager
async def lifespan(app: FastAPI):
    http_client = httpx.AsyncClient(timeout=HTTP_CLIENT_TIMEOUT_SECONDS)
    redis_client: Redis = Redis.from_url(settings.redis_url)

    app.state.http_client = http_client
    app.state.redis = redis_client
    app.state.open_weather_client = OpenWeatherClient(
        http_client=http_client,
        api_key=settings.openweather_api_key,
    )
    try:
        yield
    finally:
        await http_client.aclose()
        await redis_client.aclose()


app = FastAPI(title="Bemagro Weather API", lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(weather.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.include_router(status.router, prefix="/api")
