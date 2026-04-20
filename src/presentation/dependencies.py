from fastapi import Depends, Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.repositories.search_history_repository import (
    SqlAlchemySearchHistoryRepository,
)
from src.infrastructure.database.session import get_db_session
from src.infrastructure.services.open_weather_client import OpenWeatherClient


def get_search_history_repository(
    session: AsyncSession = Depends(get_db_session),
) -> SqlAlchemySearchHistoryRepository:
    return SqlAlchemySearchHistoryRepository(session)


def get_open_weather_client(request: Request) -> OpenWeatherClient:
    return request.app.state.open_weather_client


def get_redis(request: Request) -> Redis:
    return request.app.state.redis
