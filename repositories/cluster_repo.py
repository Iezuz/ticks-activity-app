from datetime import date

from geoalchemy2.functions import ST_AsGeoJSON
from sqlalchemy.ext.asyncio import AsyncSession

from models import ClusterData
from models.cluster import Cluster
from geoalchemy2 import WKTElement
from sqlalchemy import select, case, update
from typing import Any, Dict, Optional, Sequence
from repositories._apply_updates import _apply_updates
from sqlalchemy import func, text
from sqlalchemy import delete, exists
import json

GRID_CELL_SIZE_METERS = 5000


# async def generate_clusters_for_region(
#     db: AsyncSession,
#     *,
#     region_id: int,
#     cell_size: int = GRID_CELL_SIZE_METERS,
# ) -> None:
#     """
#     Генерирует сетку квадратов (кластеров) для региона.
#     Использует ST_SquareGrid в EPSG:3857.
#     """
#
#     region_exists = await get_region(db, region_id)
#     if not region_exists:
#         raise ValueError(f"Регион с id={region_id} не найден")
#
#     query = text(
#         """
#         WITH region_3857 AS (
#             SELECT ST_Transform(boundary, 3857) AS geom
#             FROM regions
#             WHERE id = :region_id
#         ),
#         grid AS (
#             SELECT (ST_SquareGrid(:cell_size, geom)).geom AS cell
#             FROM region_3857
#         )
#         INSERT INTO clusters (geometry, region_id)
#         SELECT ST_Transform(ST_Intersection(cell, region_3857.geom), 4326), :region_id
#         FROM grid, region_3857
#         WHERE ST_Intersects(cell, region_3857.geom);
#         """
#     ))
#
#     result = await db.execute(query, {"region_id": region_id, "cell_size": cell_size})


async def create_cluster(
    db: AsyncSession,
    polygon_wkt: str,
    region_id: int
) -> Cluster:

    geom = WKTElement(polygon_wkt, srid=4326)

    cluster = Cluster(
        geometry=geom,
        centroid=func.ST_PointOnSurface(geom),
        elevation=0,
        region_id=region_id
    )

    db.add(cluster)

    await db.flush()

    return cluster


async def get_cluster(db: AsyncSession, cluster_id: int) -> Optional[Dict[str, Any]]:

    q = (
        select(
            Cluster.id,
            Cluster.region_id,
            Cluster.elevation,
            Cluster.centroid,
            func.ST_AsGeoJSON(Cluster.geometry).label("geometry")
        )
        .where(Cluster.id == cluster_id)
    )

    result = await db.execute(q)
    row = result.first()

    if not row:
        return None

    return {
        "id": row.id,
        "region_id": row.region_id,
        "elevation": row.elevation,
        "point_for_weather_fetching": row.point_for_weather_fetching,
        "geometry": json.loads(row.geometry) if row.geometry else None
    }


async def list_clusters(db: AsyncSession, skip: int = 0, limit: int = 1500) -> Sequence[Dict[str, Any]]:

    q = (
        select(
            Cluster.id,
            Cluster.region_id,
            Cluster.elevation,
            Cluster.centroid,
            func.ST_AsGeoJSON(Cluster.geometry).label("geometry")
        )
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(q)
    rows = result.all()

    return [
        {
            "id": row.id,
            "region_id": row.region_id,
            "elevation": row.elevation,
            "point_for_weather_fetching": row.point_for_weather_fetching,
            "geometry": json.loads(row.geometry) if row.geometry else None
        }
        for row in rows
    ]


async def update_cluster(db: AsyncSession, cluster_id: int, updates: Dict[str, Any]) -> Optional[Cluster]:
    c = await get_cluster(db, cluster_id)
    if not c:
        return None
    if "polygon_wkt" in updates and updates["polygon_wkt"] is not None:
        c.geometry = WKTElement(updates.pop("polygon_wkt"), srid=4326)
    _apply_updates(c, updates, exclude=["id"])
    db.add(c)
    return c


async def get_clusters_by_region(db: AsyncSession, *, region_id: int) -> Sequence[Dict[str, Any]]:

    q = (
        select(
            Cluster.id,
            Cluster.region_id,
            Cluster.elevation,
            Cluster.centroid,
            func.ST_AsGeoJSON(Cluster.geometry).label("geometry")
        )
        .where(Cluster.region_id == region_id)
    )

    result = await db.execute(q)
    rows = result.all()

    return [
        {
            "id": row.id,
            "region_id": row.region_id,
            "elevation": row.elevation,
            "point_for_weather_fetching": row.point_for_weather_fetching,
            "geometry": json.loads(row.geometry) if row.geometry else None
        }
        for row in rows
    ]


async def list_clusters_in_bbox(
    db: AsyncSession,
    *,
    min_lon: float,
    min_lat: float,
    max_lon: float,
    max_lat: float,
    region_id: int | None = None,
) -> Sequence[Cluster]:

    envelope = func.ST_MakeEnvelope(min_lon, min_lat, max_lon, max_lat, 4326)

    q = (
        select(
            Cluster.id,
            Cluster.elevation,
            func.ST_AsGeoJSON(Cluster.geometry).label("geometry"),
        )
        .where(func.ST_Intersects(Cluster.geometry, envelope))
    )
    if region_id is not None:
        q = q.where(Cluster.region_id == region_id)

    result = await db.execute(q)
    rows = result.all()

    clusters = [
        {
            "id": row.id,
            "elevation": row.elevation,
            "geometry": None if row.geometry is None else json.loads(row.geometry),
        }
        for row in rows
    ]

    return clusters


async def delete_clusters_by_region(db: AsyncSession, *, region_id: int) -> int:
    q = (
        delete(Cluster)
        .where(Cluster.region_id == region_id)
        .returning(Cluster.id)
    )

    result = await db.execute(q)
    deleted_ids = result.scalars().all()

    return len(deleted_ids)


async def delete_cluster(db: AsyncSession, cluster_id: int) -> bool:
    q = delete(Cluster).where(Cluster.id == cluster_id)
    result = await db.execute(q)
    return result.rowcount > 0


async def get_clusters_activity_by_region(db: AsyncSession, region_id: int, target_date: date):
    subq = (
        select(
            ClusterData.cluster_id,
            ClusterData.amount_of_bites,
            ClusterData.predicted_amount_of_bites
        )
        .where(ClusterData.date == target_date)
        .subquery()
    )

    q = (
        select(
            Cluster.id.label("cluster_id"),
            ST_AsGeoJSON(Cluster.geometry).label("geometry"),
            case(
                (target_date <= func.current_date(), subq.c.amount_of_bites),
                else_=subq.c.predicted_amount_of_bites
            ).label("amount")
        )
        .join(subq, subq.c.cluster_id == Cluster.id)
        .where(Cluster.region_id == region_id)
    )

    result = await db.execute(q)

    return result.mappings().all()


async def clusters_exist(db: AsyncSession, region_id: int) -> bool:

    query = select(
        exists().where(Cluster.region_id == region_id)
    )

    result = await db.execute(query)

    return result.scalar()


async def get_cluster_centroids(db: AsyncSession, region_id: int):
    result = await db.execute(
        select(
            Cluster.id,
            func.ST_Y(Cluster.centroid).label("lat"),
            func.ST_X(Cluster.centroid).label("lon")
        ).where(Cluster.region_id == region_id)
    )

    return result.all()


async def bulk_update_cluster_elevation(db: AsyncSession, elevation_map: dict[int, float]):

    if not elevation_map:
        return

    stmt = (
        update(Cluster)
        .where(Cluster.id.in_(elevation_map.keys()))
        .values(
            elevation=case(
                elevation_map,
                value=Cluster.id
            )
        )
    )

    await db.execute(stmt)
