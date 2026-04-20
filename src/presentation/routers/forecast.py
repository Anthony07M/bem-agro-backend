from fastapi import APIRouter, Depends, Query, Request

from src.infrastructure.services.dtos.forecast import ForecastResponseDTO
from src.infrastructure.services.open_weather_client import OpenWeatherClient
from src.presentation.dependencies import get_open_weather_client
from src.presentation.rate_limiter import limiter

router = APIRouter(tags=["forecast"])


@router.get("/forecast", response_model=ForecastResponseDTO)
@limiter.limit("10/minute")
async def get_forecast(
    request: Request,
    city: str = Query(
        ...,
        min_length=1,
        max_length=100,
        description="Nome da cidade a consultar",
    ),
    client: OpenWeatherClient = Depends(get_open_weather_client),
) -> ForecastResponseDTO:
    return await client.get_hourly_forecast(city)
