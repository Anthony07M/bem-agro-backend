from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from redis.exceptions import RedisError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.session import get_db_session
from src.presentation.dependencies import get_redis
from src.presentation.schemas.status import StatusResponse

router = APIRouter(tags=["status"])


@router.get("/status", response_model=StatusResponse)
async def healthcheck(
    session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis),
) -> StatusResponse:
    try:
        await session.execute(text("SELECT 1"))
        database_ok = True
    except SQLAlchemyError:
        database_ok = False

    try:
        await redis.ping()
        redis_ok = True
    except (RedisError, OSError):
        redis_ok = False

    return StatusResponse(
        status="ok" if database_ok and redis_ok else "degraded",
        database=database_ok,
        redis=redis_ok,
    )
