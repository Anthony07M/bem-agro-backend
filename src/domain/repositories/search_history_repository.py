from abc import ABC, abstractmethod
from collections.abc import Sequence

from src.infrastructure.database.models.search_history import SearchHistory


class SearchHistoryRepository(ABC):
    @abstractmethod
    async def save_search_history(
        self,
        city_name: str,
        latitude: float,
        longitude: float,
    ) -> SearchHistory: ...

    @abstractmethod
    async def get_recent_history(self, limit: int = 10) -> Sequence[SearchHistory]: ...
