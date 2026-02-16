from typing import Optional, Sequence, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from models.cluster import Cluster
from repositories.cluster_repo import (create_cluster, get_cluster, list_clusters,
                                       update_cluster, delete_cluster, list_clusters_in_bbox)


class ClusterService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, polygon_wkt: str) -> Cluster:
        try:
            cluster = await create_cluster(self.db, polygon_wkt)
            await self.db.commit()
            await self.db.refresh(cluster)
            return cluster
        except SQLAlchemyError:
            await self.db.rollback()
            raise

    async def get_by_id(self, cluster_id: int, load_relations: bool = True) -> Optional[Cluster]:
        return await get_cluster(self.db, cluster_id, load_relations)

    async def list(self, skip: int = 0, limit: int = 100) -> Sequence[Cluster]:
        return await list_clusters(self.db, skip, limit)

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

    async def list_clusters_in_bbox_service(
            self,
            min_lon:float,
            min_lat: float,
            max_lon: float,
            max_lat: float
    ) -> Sequence[Cluster]:

        return await list_clusters_in_bbox(self.db, min_lon, min_lat, max_lon, max_lat)
