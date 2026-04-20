from typing import Any

from pydantic import BaseModel, model_validator


class WeatherDTO(BaseModel):
    temperature: float
    feels_like: float
    humidity: int
    wind_speed: float
    description: str
    latitude: float
    longitude: float

    @model_validator(mode="before")
    @classmethod
    def _flatten_openweather_payload(cls, data: Any) -> Any:
        if not isinstance(data, dict) or "temperature" in data:
            return data

        main = data.get("main") or {}
        wind = data.get("wind") or {}
        weather_list = data.get("weather") or [{}]
        coord = data.get("coord") or {}

        return {
            "temperature": main.get("temp"),
            "feels_like": main.get("feels_like"),
            "humidity": main.get("humidity"),
            "wind_speed": wind.get("speed"),
            "description": weather_list[0].get("description", ""),
            "latitude": coord.get("lat"),
            "longitude": coord.get("lon"),
        }
