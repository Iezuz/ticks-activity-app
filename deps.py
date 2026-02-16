from db.database import async_session_maker

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from services.region_service import RegionService


async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


def get_region_service(db: AsyncSession = Depends(get_db)) -> RegionService:
    return RegionService(db)
