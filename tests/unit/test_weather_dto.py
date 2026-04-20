from src.infrastructure.services.dtos.weather import WeatherDTO

RAW_OPENWEATHER_PAYLOAD = {
    "coord": {"lon": -46.6333, "lat": -23.5505},
    "weather": [
        {"id": 800, "main": "Clear", "description": "céu limpo", "icon": "01d"},
    ],
    "main": {
        "temp": 22.15,
        "feels_like": 22.04,
        "temp_min": 21.0,
        "temp_max": 23.0,
        "pressure": 1015,
        "humidity": 62,
    },
    "wind": {"speed": 3.08, "deg": 90},
    "name": "São Paulo",
}


class TestWeatherDTOParsing:
    def test_flattens_nested_openweather_payload(self) -> None:
        dto = WeatherDTO.model_validate(RAW_OPENWEATHER_PAYLOAD)

        assert dto.temperature == 22.15
        assert dto.feels_like == 22.04
        assert dto.humidity == 62
        assert dto.wind_speed == 3.08
        assert dto.description == "céu limpo"
        assert dto.latitude == -23.5505
        assert dto.longitude == -46.6333

    def test_accepts_already_flat_payload(self) -> None:
        dto = WeatherDTO.model_validate(
            {
                "temperature": 20.0,
                "feels_like": 19.5,
                "humidity": 55,
                "wind_speed": 2.0,
                "description": "nublado",
                "latitude": 0.0,
                "longitude": 0.0,
            },
        )

        assert dto.temperature == 20.0
        assert dto.description == "nublado"
