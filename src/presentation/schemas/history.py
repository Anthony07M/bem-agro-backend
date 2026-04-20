from datetime import datetime

from pydantic import BaseModel, ConfigDict


class HistoryItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    city_name: str
    latitude: float
    longitude: float
    created_at: datetime
