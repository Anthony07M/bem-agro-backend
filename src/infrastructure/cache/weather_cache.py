import functools
from collections.abc import Awaitable, Callable
from typing import ParamSpec

from redis.asyncio import Redis
from redis.exceptions import RedisError

from src.infrastructure.services.dtos.weather import WeatherDTO

CACHE_PREFIX = "weather:"
CACHE_TTL_SECONDS = 15 * 60

P = ParamSpec("P")


def _normalize_city(city: str) -> str:
    return city.strip().lower()


def cached_weather(
    ttl_seconds: int = CACHE_TTL_SECONDS,
) -> Callable[[Callable[P, Awaitable[WeatherDTO]]], Callable[P, Awaitable[WeatherDTO]]]:
    def decorator(
        func: Callable[P, Awaitable[WeatherDTO]],
    ) -> Callable[P, Awaitable[WeatherDTO]]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> WeatherDTO:
            redis: Redis = kwargs["redis"]  # type: ignore[assignment]
            city: str = kwargs["city"]  # type: ignore[assignment]
            key = f"{CACHE_PREFIX}{_normalize_city(city)}"

            try:
                cached = await redis.get(key)
            except (RedisError, OSError):
                cached = None

            if cached is not None:
                return WeatherDTO.model_validate_json(cached)

            result = await func(*args, **kwargs)

            try:
                await redis.setex(key, ttl_seconds, result.model_dump_json())
            except (RedisError, OSError):
                pass

            return result

        return wrapper

    return decorator
