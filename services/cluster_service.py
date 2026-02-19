from typing import Optional, Sequence, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from models.cluster import Cluster
from repositories.cluster_repo import (create_cluster, get_cluster, list_clusters,
                                       update_cluster, delete_cluster, list_clusters_in_bbox, get_clusters_by_region)


class ClusterService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list(self, skip: int = 0, limit: int = 100) -> Sequence[dict[str, Any]]:
        return await list_clusters(self.db, skip, limit)

    async def create(self, polygon_wkt: str) -> Cluster:
        try:
            cluster = await create_cluster(self.db, polygon_wkt)
            await self.db.commit()
            await self.db.refresh(cluster)
            return cluster
        except SQLAlchemyError:
            await self.db.rollback()
            raise

    async def get_by_id(self, cluster_id: int) -> Optional[Cluster]:
        return await get_cluster(self.db, cluster_id)

    async def update(self, cluster_id: int, updates: Dict[str, Any]) -> Optional[Cluster]:
        try:
            cluster = await update_cluster(self.db, cluster_id, updates)
            if not cluster:
                await self.db.rollback()
                return None
            await self.db.commit()
            await self.db.refresh(cluster)
            return cluster
        except SQLAlchemyError:
            await self.db.rollback()
            raise

    async def delete(self, cluster_id: int) -> bool:
        try:
            cluster = await delete_cluster(self.db, cluster_id)
            if not cluster:
                await self.db.rollback()
                return False
            await self.db.commit()
            return True
        except SQLAlchemyError:
            await self.db.rollback()
            raise

    async def list_clusters_in_bbox(
            self,
            min_lon: float,
            min_lat: float,
            max_lon: float,
            max_lat: float
    ) -> Sequence[Cluster]:

        return await list_clusters_in_bbox(self.db, min_lon=min_lon, min_lat=min_lat, max_lon=max_lon, max_lat=max_lat)

    async def get_by_region(self, region_id: int) -> Sequence[dict[str, Any]]:
        return await get_clusters_by_region(self.db, region_id=region_id)
