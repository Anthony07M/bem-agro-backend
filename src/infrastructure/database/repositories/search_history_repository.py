from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.repositories.search_history_repository import SearchHistoryRepository
from src.infrastructure.database.models.search_history import SearchHistory


class SqlAlchemySearchHistoryRepository(SearchHistoryRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save_search_history(
        self,
        city_name: str,
        latitude: float,
        longitude: float,
    ) -> SearchHistory:
        record = SearchHistory(
            city_name=city_name,
            latitude=latitude,
            longitude=longitude,
        )
        self._session.add(record)
        await self._session.commit()
        await self._session.refresh(record)
        return record

    async def get_recent_history(self, limit: int = 10) -> Sequence[SearchHistory]:
        stmt = (
            select(SearchHistory)
            .order_by(SearchHistory.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()
