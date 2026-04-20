import httpx

from src.infrastructure.services.dtos.weather import WeatherDTO
from src.infrastructure.services.exceptions import (
    CityNotFoundError,
    WeatherApiAuthError,
    WeatherApiError,
    WeatherApiUnavailableError,
)


class OpenWeatherClient:
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

    def __init__(self, http_client: httpx.AsyncClient, api_key: str) -> None:
        self._http_client = http_client
        self._api_key = api_key

    async def get_weather_by_city(self, city: str) -> WeatherDTO:
        params = {
            "q": city,
            "appid": self._api_key,
            "units": "metric",
            "lang": "pt_br",
        }

        try:
            response = await self._http_client.get(self.BASE_URL, params=params)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            upstream_status = exc.response.status_code
            if upstream_status == httpx.codes.NOT_FOUND:
                raise CityNotFoundError(city) from exc
            if upstream_status == httpx.codes.UNAUTHORIZED:
                raise WeatherApiAuthError() from exc
            raise WeatherApiError(upstream_status) from exc
        except httpx.RequestError as exc:
            raise WeatherApiUnavailableError(str(exc) or type(exc).__name__) from exc

        return WeatherDTO.model_validate(response.json())
