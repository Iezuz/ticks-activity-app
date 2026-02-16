from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from models.cluster import Cluster
from geoalchemy2 import WKTElement
from sqlalchemy import select
from typing import Any, Dict, Optional, Sequence
from repositories._apply_updates import _apply_updates
from sqlalchemy import func, text
from repositories.region_repo import get_region
from sqlalchemy import delete

GRID_CELL_SIZE_METERS = 5000


async def generate_clusters_for_region(
    db: AsyncSession,
    *,
    region_id: int,
    cell_size: int = GRID_CELL_SIZE_METERS,
) -> None:
    """
    Генерирует сетку квадратов (кластеров) для региона.
    Использует ST_SquareGrid в EPSG:3857.
    """

    region_exists = await get_region(db, region_id)
    if not region_exists:
        raise ValueError(f"Регион с id={region_id} не найден")




    query = text(
        """
        WITH region_3857 AS (
            SELECT ST_Transform(boundary, 3857) AS geom
            FROM regions
            WHERE id = :region_id
        ),
        grid AS (
            SELECT (ST_SquareGrid(:cell_size, geom)).geom AS cell
            FROM region_3857
        )
        INSERT INTO clusters (geometry, region_id)
        SELECT ST_Transform(ST_Intersection(cell, region_3857.geom), 4326), :region_id
        FROM grid, region_3857
        WHERE ST_Intersects(cell, region_3857.geom);
        """
    )

    result = await db.execute(query, {"region_id": region_id, "cell_size": cell_size})


async def create_cluster(db: AsyncSession, polygon_wkt: str) -> Cluster:
    geom = WKTElement(polygon_wkt, srid=4326)
    c = Cluster(geometry=geom)
    db.add(c)
    await db.flush()
    return c


async def get_cluster(db: AsyncSession, cluster_id: int, load_relations: bool = True) -> Optional[Cluster]:
    if load_relations:
        q = (
                select(Cluster)
                .options(selectinload(Cluster.bites), selectinload(Cluster.cluster_data))
                .where(Cluster.id == cluster_id)
            )
    else:
        q = select(Cluster).where(Cluster.id == cluster_id)
    result = await db.execute(q)
    return result.scalars().first()


async def list_clusters(db: AsyncSession, skip: int = 0, limit: int = 100) -> Sequence[Cluster]:
    q = select(Cluster).offset(skip).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


async def update_cluster(db: AsyncSession, cluster_id: int, updates: Dict[str, Any]) -> Optional[Cluster]:
    c = await get_cluster(db, cluster_id, load_relations=False)
    if not c:
        return None
    if "polygon_wkt" in updates and updates["polygon_wkt"] is not None:
        c.geometry = WKTElement(updates.pop("polygon_wkt"), srid=4326)
    _apply_updates(c, updates, exclude=["id"])
    db.add(c)
    return c


async def get_clusters_by_region(db: AsyncSession, *, region_id: int) -> Sequence[Cluster]:
    q = select(Cluster).where(Cluster.region_id == region_id)
    result = await db.execute(q)
    return result.scalars().all()


async def list_clusters_in_bbox(
    db: AsyncSession,
    min_lon: float,
    min_lat: float,
    max_lon: float,
    max_lat: float,
) -> Sequence[Cluster]:

    envelope = func.ST_MakeEnvelope(min_lon, min_lat, max_lon, max_lat, 4326)

    q = select(Cluster).where(func.ST_Intersects(Cluster.geometry, envelope))

    result = await db.execute(q)
    return result.scalars().all()


async def delete_clusters_by_region(db: AsyncSession, *, region_id: int) -> int:
    q = (
        delete(Cluster)
        .where(Cluster.region_id == region_id)
        .returning(Cluster.id)
    )

    result = await db.execute(q)
    deleted_ids = result.scalars().all()

    return len(deleted_ids)

