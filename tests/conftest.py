from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from src.infrastructure.database.base import Base
from src.infrastructure.database.session import get_db_session
from src.infrastructure.services.dtos.weather import WeatherDTO
from src.main import app
from src.presentation.dependencies import get_open_weather_client, get_redis
from src.presentation.rate_limiter import limiter


@pytest_asyncio.fixture
async def test_engine():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def test_session_factory(test_engine):
    return async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture
def sample_weather_dto() -> WeatherDTO:
    return WeatherDTO(
        temperature=22.15,
        feels_like=22.04,
        humidity=62,
        wind_speed=3.08,
        description="céu limpo",
        latitude=-23.5505,
        longitude=-46.6333,
    )


@pytest.fixture
def mock_open_weather_client(sample_weather_dto: WeatherDTO) -> AsyncMock:
    mock = AsyncMock()
    mock.get_weather_by_city.return_value = sample_weather_dto
    return mock


@pytest.fixture
def mock_redis() -> AsyncMock:
    mock = AsyncMock()
    mock.get.return_value = None
    mock.setex.return_value = True
    mock.ping.return_value = True
    return mock


@pytest.fixture
def test_client(test_session_factory, mock_open_weather_client, mock_redis):
    async def override_db() -> AsyncGenerator[AsyncSession, None]:
        async with test_session_factory() as session:
            yield session

    app.dependency_overrides[get_db_session] = override_db
    app.dependency_overrides[get_open_weather_client] = lambda: mock_open_weather_client
    app.dependency_overrides[get_redis] = lambda: mock_redis

    limiter.reset()

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
    limiter.reset()
