from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from src.infrastructure.services.dtos.weather import WeatherDTO
from src.infrastructure.services.exceptions import CityNotFoundError


class TestGetWeatherHappyPath:
    def test_returns_weather_dto(
        self,
        test_client: TestClient,
        sample_weather_dto: WeatherDTO,
    ) -> None:
        response = test_client.get("/api/weather", params={"city": "São Paulo"})

        assert response.status_code == 200
        assert response.json() == sample_weather_dto.model_dump()

    def test_persists_search_history_on_cache_miss(
        self,
        test_client: TestClient,
        sample_weather_dto: WeatherDTO,
    ) -> None:
        test_client.get("/api/weather", params={"city": "Recife"})

        history = test_client.get("/api/history").json()
        assert len(history) == 1
        assert history[0]["city_name"] == "Recife"
        assert history[0]["latitude"] == sample_weather_dto.latitude
        assert history[0]["longitude"] == sample_weather_dto.longitude


class TestGetWeatherCache:
    def test_cache_hit_skips_openweather_call(
        self,
        test_client: TestClient,
        mock_open_weather_client: AsyncMock,
        mock_redis: AsyncMock,
        sample_weather_dto: WeatherDTO,
    ) -> None:
        mock_redis.get.return_value = sample_weather_dto.model_dump_json().encode()

        response = test_client.get("/api/weather", params={"city": "Recife"})

        assert response.status_code == 200
        mock_open_weather_client.get_weather_by_city.assert_not_called()

    def test_cache_hit_still_saves_history(
        self,
        test_client: TestClient,
        mock_redis: AsyncMock,
        sample_weather_dto: WeatherDTO,
    ) -> None:
        mock_redis.get.return_value = sample_weather_dto.model_dump_json().encode()

        test_client.get("/api/weather", params={"city": "Recife"})

        history = test_client.get("/api/history").json()
        assert len(history) == 1
        assert history[0]["city_name"] == "Recife"

    def test_cache_miss_writes_to_redis(
        self,
        test_client: TestClient,
        mock_redis: AsyncMock,
    ) -> None:
        test_client.get("/api/weather", params={"city": "Recife"})

        mock_redis.setex.assert_called_once()
        args, _ = mock_redis.setex.call_args
        assert args[0] == "weather:recife"
        assert args[1] == 15 * 60


class TestGetWeatherErrors:
    def test_city_not_found_returns_404(
        self,
        test_client: TestClient,
        mock_open_weather_client: AsyncMock,
    ) -> None:
        mock_open_weather_client.get_weather_by_city.side_effect = CityNotFoundError("Foo")

        response = test_client.get("/api/weather", params={"city": "Foo"})

        assert response.status_code == 404
        assert "Foo" in response.json()["detail"]

    def test_empty_city_returns_422(self, test_client: TestClient) -> None:
        response = test_client.get("/api/weather", params={"city": ""})

        assert response.status_code == 422


class TestGetWeatherRateLimit:
    def test_rate_limit_blocks_after_10_requests_per_minute(
        self,
        test_client: TestClient,
    ) -> None:
        for _ in range(10):
            response = test_client.get("/api/weather", params={"city": "Belem"})
            assert response.status_code == 200

        response = test_client.get("/api/weather", params={"city": "Belem"})
        assert response.status_code == 429
