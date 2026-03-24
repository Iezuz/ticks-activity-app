from datetime import date, datetime
from typing import Optional, Sequence, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from models.cluster import Cluster
from repositories.bite_repo import get_bites_for_region, reset_clusters, assign_cluster_to_bites
from repositories.cluster_repo import (create_cluster, get_cluster, list_clusters, update_cluster, delete_cluster,
                                       list_clusters_in_bbox, get_clusters_by_region, get_clusters_activity_by_region,
                                       clusters_exist, get_cluster_centroids, bulk_update_cluster_elevation)
from services import elevation_service
from services.clustering.clusterizer import Clusterizer
from services.elevation_service import ElevationService


class ClusterService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.elevation_service = ElevationService()

    async def list(self, skip: int = 0, limit: int = 100) -> Sequence[dict[str, Any]]:
        return await list_clusters(self.db, skip, limit)

    # async def create(self, polygon_wkt: str) -> Cluster:
    #     try:
    #         cluster = await create_cluster(self.db, polygon_wkt)
    #         await self.db.commit()
    #         await self.db.refresh(cluster)
    #         return cluster
    #     except SQLAlchemyError:
    #         await self.db.rollback()
    #         raise

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

    # async def list_clusters_in_bbox(
    #         self,
    #         min_lon: float,
    #         min_lat: float,
    #         max_lon: float,
    #         max_lat: float
    # ) -> Sequence[Cluster]:
    #
    #     return await list_clusters_in_bbox(self.db, min_lon=min_lon, min_lat=min_lat, max_lon=max_lon, max_lat=max_lat)

    async def get_by_region(self, region_id: int) -> Sequence[dict[str, Any]]:
        return await get_clusters_by_region(self.db, region_id=region_id)

    async def get_cluster_activity(self, region_id, target_date):

        rows = await get_clusters_activity_by_region(
            self.db,
            region_id,
            target_date
        )

        return rows

    async def build_clusters(self, region_id: int):

        bites = await get_bites_for_region(self.db, region_id)

        clusterizer = Clusterizer()

        clusters = clusterizer.build_clusters(bites)

        if await clusters_exist(self.db, region_id):
            await reset_clusters(self.db, region_id)

        for cluster in clusters:
            cluster_obj = await create_cluster(
                self.db,
                polygon_wkt=cluster.polygon_wkt,
                region_id=region_id
            )

            await assign_cluster_to_bites(
                self.db,
                cluster_obj.id,
                cluster.bite_ids
            )

        await self.enrich_clusters_with_elevation(region_id)

    async def enrich_clusters_with_elevation(self, region_id: int):

        clusters = await get_cluster_centroids(self.db, region_id)

        if not clusters:
            return

        coord_to_ids = {}

        for c in clusters:
            key = (c.lat, c.lon)
            coord_to_ids.setdefault(key, []).append(c.id)

        coors = list(coord_to_ids.keys())

        elevations = await self.elevation_service.get_bulk_elevations(coors)

        elevation_map = {}

        for coord, cluster_ids in coord_to_ids.items():
            elevation = elevations.get(coord)

            if elevation is None:
                continue

            for cid in cluster_ids:
                elevation_map[cid] = elevation

        await bulk_update_cluster_elevation(self.db, elevation_map)
