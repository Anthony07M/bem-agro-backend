from typing import Any
from unittest.mock import AsyncMock

import httpx
import pytest

from src.infrastructure.services.exceptions import (
    CityNotFoundError,
    WeatherApiAuthError,
    WeatherApiError,
    WeatherApiUnavailableError,
)
from src.infrastructure.services.open_weather_client import OpenWeatherClient


def _make_response(status_code: int, body: dict[str, Any] | None = None) -> httpx.Response:
    return httpx.Response(
        status_code=status_code,
        json=body or {},
        request=httpx.Request("GET", OpenWeatherClient.BASE_URL),
    )


@pytest.fixture
def mock_http_client() -> AsyncMock:
    return AsyncMock(spec=httpx.AsyncClient)


class TestOpenWeatherClientHappyPath:
    async def test_returns_dto_with_fields_mapped(self, mock_http_client: AsyncMock) -> None:
        mock_http_client.get.return_value = _make_response(
            200,
            {
                "coord": {"lon": -46.6, "lat": -23.5},
                "weather": [{"description": "céu limpo"}],
                "main": {"temp": 22.0, "feels_like": 21.5, "humidity": 60},
                "wind": {"speed": 3.0},
            },
        )

        client = OpenWeatherClient(mock_http_client, "fake_key")
        dto = await client.get_weather_by_city("São Paulo")

        assert dto.temperature == 22.0
        assert dto.feels_like == 21.5
        assert dto.humidity == 60
        assert dto.wind_speed == 3.0
        assert dto.description == "céu limpo"
        assert dto.latitude == -23.5
        assert dto.longitude == -46.6

    async def test_sends_required_query_params(self, mock_http_client: AsyncMock) -> None:
        mock_http_client.get.return_value = _make_response(
            200,
            {
                "coord": {"lon": 0, "lat": 0},
                "weather": [{"description": "ok"}],
                "main": {"temp": 0, "feels_like": 0, "humidity": 0},
                "wind": {"speed": 0},
            },
        )

        client = OpenWeatherClient(mock_http_client, "secret_key")
        await client.get_weather_by_city("Recife")

        _, kwargs = mock_http_client.get.call_args
        assert kwargs["params"] == {
            "q": "Recife",
            "appid": "secret_key",
            "units": "metric",
            "lang": "pt_br",
        }


class TestOpenWeatherClientErrors:
    async def test_404_raises_city_not_found(self, mock_http_client: AsyncMock) -> None:
        mock_http_client.get.return_value = _make_response(404, {"cod": "404"})
        client = OpenWeatherClient(mock_http_client, "fake_key")

        with pytest.raises(CityNotFoundError) as exc_info:
            await client.get_weather_by_city("CidadeInexistente")

        assert exc_info.value.status_code == 404
        assert "CidadeInexistente" in exc_info.value.detail

    async def test_401_raises_auth_error(self, mock_http_client: AsyncMock) -> None:
        mock_http_client.get.return_value = _make_response(401, {})
        client = OpenWeatherClient(mock_http_client, "wrong_key")

        with pytest.raises(WeatherApiAuthError) as exc_info:
            await client.get_weather_by_city("São Paulo")

        assert exc_info.value.status_code == 500

    async def test_other_http_error_raises_generic_api_error(
        self,
        mock_http_client: AsyncMock,
    ) -> None:
        mock_http_client.get.return_value = _make_response(503, {})
        client = OpenWeatherClient(mock_http_client, "fake_key")

        with pytest.raises(WeatherApiError) as exc_info:
            await client.get_weather_by_city("São Paulo")

        assert exc_info.value.status_code == 502

    async def test_network_error_raises_unavailable(self, mock_http_client: AsyncMock) -> None:
        mock_http_client.get.side_effect = httpx.ConnectError("connection refused")
        client = OpenWeatherClient(mock_http_client, "fake_key")

        with pytest.raises(WeatherApiUnavailableError) as exc_info:
            await client.get_weather_by_city("São Paulo")

        assert exc_info.value.status_code == 503
