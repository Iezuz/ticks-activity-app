from typing import Optional, Sequence, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from geoalchemy2 import WKTElement

from models import Cluster
from models.bite import Bite
from repositories._apply_updates import _apply_updates


async def create_bite(
    db: AsyncSession,
    *,
    date_of_bite,
    point_wkt: str,
    location_description: Optional[str] = None,
    elevation: Optional[float] = None,
    snow_depth: Optional[float] = None,
) -> Bite:

    geom = WKTElement(point_wkt, srid=4326)

    query_to_find_cluster = (
        select(Cluster.id)
        .where(func.ST_Contains(Cluster.geometry, geom))
        .limit(1)
    )
    result = await db.execute(query_to_find_cluster)
    cluster_id = result.scalar_one_or_none()
    if cluster_id is None:
        raise ValueError("Для заданных координат кластер не найден")

    bite = Bite(
        date_of_bite=date_of_bite,
        point_of_bite=geom,
        location_description=location_description,
        elevation=elevation,
        snow_depth=snow_depth,
        cluster_id=cluster_id,
    )

    db.add(bite)
    await db.flush()
    return bite


async def get_bite(db: AsyncSession, bite_id: int) -> Optional[Bite]:
    result = await db.execute(select(Bite).where(Bite.id == bite_id))
    return result.scalars().first()


async def list_bites(db: AsyncSession, skip: int = 0, limit: int = 100) -> Sequence[Bite]:
    q = select(Bite).offset(skip).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


async def update_bite(db: AsyncSession, bite_id: int, updates: Dict[str, Any]) -> Optional[Bite]:
    bite = await get_bite(db, bite_id)
    if not bite:
        return None

    if "point_wkt" in updates and updates["point_wkt"] is not None:
        bite.point_of_bite = WKTElement(updates.pop("point_wkt"), srid=4326)

    _apply_updates(bite, updates, exclude=["id"])

    db.add(bite)
    await db.flush()
    return bite


async def delete_bite(db: AsyncSession, bite_id: int) -> Optional[Bite]:
    bite = await get_bite(db, bite_id)
    if not bite:
        return None

    await db.delete(bite)
    await db.flush()
    return bite




