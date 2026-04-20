from fastapi import APIRouter, Depends, Query, Request
from redis.asyncio import Redis

from src.infrastructure.cache.weather_cache import cached_weather
from src.infrastructure.database.repositories.search_history_repository import (
    SqlAlchemySearchHistoryRepository,
)
from src.infrastructure.services.dtos.weather import WeatherDTO
from src.infrastructure.services.open_weather_client import OpenWeatherClient
from src.presentation.dependencies import (
    get_open_weather_client,
    get_redis,
    get_search_history_repository,
)
from src.presentation.rate_limiter import limiter

router = APIRouter(tags=["weather"])


@cached_weather()
async def _fetch_weather(
    *,
    client: OpenWeatherClient,
    city: str,
    redis: Redis,
) -> WeatherDTO:
    return await client.get_weather_by_city(city)


@router.get("/weather", response_model=WeatherDTO)
@limiter.limit("10/minute")
async def get_weather(
    request: Request,
    city: str = Query(
        ...,
        min_length=1,
        max_length=100,
        description="Nome da cidade a consultar",
    ),
    client: OpenWeatherClient = Depends(get_open_weather_client),
    repo: SqlAlchemySearchHistoryRepository = Depends(get_search_history_repository),
    redis: Redis = Depends(get_redis),
) -> WeatherDTO:
    dto = await _fetch_weather(client=client, city=city, redis=redis)
    await repo.save_search_history(
        city_name=city,
        latitude=dto.latitude,
        longitude=dto.longitude,
    )
    return dto
