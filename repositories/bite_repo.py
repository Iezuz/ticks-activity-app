import json
from datetime import date
from typing import Optional, Sequence, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from geoalchemy2 import WKTElement

from models import Cluster, Region
from models.bite import Bite
from repositories._apply_updates import _apply_updates


from typing import Optional
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2.elements import WKTElement


async def create_bite(
    db: AsyncSession,
    *,
    date_of_bite,
    point_wkt: str,
    location_description: Optional[str] = None
) -> Bite | None:

    geom = WKTElement(point_wkt, srid=4326)

    region_query = select(Region.id).where(
        func.ST_Contains(Region.boundary, geom)
    ).limit(1)

    result = await db.execute(region_query)
    region_id = result.scalar_one_or_none()

    if region_id is None:
        return None

    bite = Bite(
        date_of_bite=date_of_bite,
        point_of_bite=geom,
        location_description=location_description,
        region_id=region_id,
        cluster_id=None,
        processed_for_cluster_data=False
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


async def get_filtered(
    db: AsyncSession,
    start_date: date | None,
    end_date: date | None,
    region_id: int | None
):
    query = select(
        Bite.id,
        Bite.date_of_bite,
        Bite.location_description,
        Bite.cluster_id,
        func.ST_AsGeoJSON(Bite.point_of_bite).label("point_of_bite")
    )

    if start_date:
        query = query.where(Bite.date_of_bite >= start_date)

    if end_date:
        query = query.where(Bite.date_of_bite <= end_date)

    if region_id:
        query = query.join(
            Region,
            func.ST_Contains(Region.boundary, Bite.point_of_bite)
        ).where(Region.id == region_id)

    result = await db.execute(query)

    return result.all()


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


async def add_bite_from_excel(
    db: AsyncSession,
    date_of_bite,
    x: float,
    y: float,
    location: str | None
):

    point_wkt = f"POINT({x} {y})"
    print(point_wkt)
    return await create_bite(
        db,
        date_of_bite=date_of_bite,
        point_wkt=point_wkt,
        location_description=location
    )


async def get_bites_for_region(db: AsyncSession, region_id: int):
    query = select(Bite).where(Bite.region_id == region_id)

    result = await db.execute(query)
    return result.scalars().all()


async def reset_clusters(db: AsyncSession, region_id: int):
    query = (
        update(Bite)
        .where(Bite.region_id == region_id)
        .values(cluster_id=None)
    )

    await db.execute(query)


async def assign_cluster_to_bites(db: AsyncSession, cluster_id: int, bite_ids: list[int]):
    if not bite_ids:
        return

    query = (
        update(Bite)
        .where(Bite.id.in_(bite_ids))
        .values(cluster_id=cluster_id)
    )

    await db.execute(query)

