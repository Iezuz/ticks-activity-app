from typing import Optional, Sequence, Dict, Any
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from models import ClusterData
from repositories import cluster_data_repo as repo


class ClusterDataService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        *,
        cluster_id: int,
        cluster_date: date,
        avg_elevation: Optional[float] = None,
        avg_snow_depth: Optional[float] = None,
    ) -> ClusterData:

        try:
            cd = await repo.create_cluster_data(
                self.db,
                cluster_id=cluster_id,
                cluster_date=cluster_date,
                avg_elevation=avg_elevation,
                avg_snow_depth=avg_snow_depth,
            )

            await self.db.commit()
            await self.db.refresh(cd)
            return cd

        except SQLAlchemyError:
            await self.db.rollback()
            raise

    async def get_by_id(self, cd_id: int) -> Optional[ClusterData]:
        return await repo.get_cluster_data(self.db, cd_id)

    async def list_for_cluster(
        self,
        cluster_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[ClusterData]:

        return await repo.list_cluster_data_for_cluster(self.db, cluster_id, skip, limit)

    async def update(self, cd_id: int, updates: Dict[str, Any]) -> Optional[ClusterData]:
        try:
            cd = await repo.update_cluster_data(self.db, cd_id, updates)

            if not cd:
                return None

            await self.db.commit()
            await self.db.refresh(cd)
            return cd

        except SQLAlchemyError:
            await self.db.rollback()
            raise

    async def delete(self, cd_id: int) -> bool:
        try:
            success = await repo.delete_cluster_data(self.db, cd_id)

            if not success:
                return False

            await self.db.commit()
            return True

        except SQLAlchemyError:
            await self.db.rollback()
            raise
