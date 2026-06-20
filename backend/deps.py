from db.database import async_session_maker

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from services.bite_service import BiteService
from services.region_service import RegionService
from services.cluster_service import ClusterService
from services.cluster_data_service import ClusterDataService


async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


def get_region_service(db: AsyncSession = Depends(get_db)) -> RegionService:
    return RegionService(db)


async def get_cluster_service(db: AsyncSession = Depends(get_db)) -> ClusterService:
    return ClusterService(db)


async def get_bite_service(db: AsyncSession = Depends(get_db)) -> BiteService:
    return BiteService(db)


async def get_cluster_data_service(db: AsyncSession = Depends(get_db)) -> ClusterDataService:
    return ClusterDataService(db)
