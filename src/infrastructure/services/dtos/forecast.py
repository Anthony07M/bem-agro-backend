from typing import Any

from pydantic import BaseModel, model_validator

FORECAST_ITEMS_LIMIT = 8


class ForecastItemDTO(BaseModel):
    time: str
    temperature: float
    icon: str
    description: str
    pop: int

    @model_validator(mode="before")
    @classmethod
    def _flatten_openweather_item(cls, data: Any) -> Any:
        if not isinstance(data, dict) or "time" in data:
            return data

        main = data.get("main") or {}
        weather_list = data.get("weather") or [{}]
        weather = weather_list[0] if weather_list else {}
        pop = data.get("pop") or 0

        return {
            "time": data.get("dt_txt"),
            "temperature": main.get("temp"),
            "icon": weather.get("icon", ""),
            "description": weather.get("description", ""),
            "pop": int(round(float(pop) * 100)),
        }


class ForecastResponseDTO(BaseModel):
    forecast: list[ForecastItemDTO]

    @model_validator(mode="before")
    @classmethod
    def _flatten_openweather_payload(cls, data: Any) -> Any:
        if not isinstance(data, dict) or "forecast" in data:
            return data

        raw_list = data.get("list") or []
        return {"forecast": raw_list[:FORECAST_ITEMS_LIMIT]}
