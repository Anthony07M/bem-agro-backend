from fastapi import APIRouter, Depends

from src.infrastructure.database.repositories.search_history_repository import (
    SqlAlchemySearchHistoryRepository,
)
from src.presentation.dependencies import get_search_history_repository
from src.presentation.schemas.history import HistoryItemResponse

router = APIRouter(tags=["history"])


@router.get("/history", response_model=list[HistoryItemResponse])
async def get_history(
    repo: SqlAlchemySearchHistoryRepository = Depends(get_search_history_repository),
) -> list[HistoryItemResponse]:
    records = await repo.get_recent_history(limit=10)
    return [HistoryItemResponse.model_validate(record) for record in records]
