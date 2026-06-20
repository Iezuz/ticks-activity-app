import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from geoalchemy2 import WKTElement
from typing import Optional, Sequence

from models.region import Region


async def create_region(
        db: AsyncSession,
        *,
        name: str,
        boundary_wkt: str,
        description: Optional[str] = None,
) -> Region:
    geom = WKTElement(boundary_wkt, srid=4326)

    region = Region(
        name=name,
        description=description,
        boundary=geom,
    )

    db.add(region)
    await db.flush()
    return region


async def list_regions(db: AsyncSession) -> Sequence[Region]:
    q = select(Region).where(Region.is_active)
    result = await db.execute(q)
    return result.scalars().all()


async def get_region(db: AsyncSession, region_id: int):
    stmt = select(
        Region.id,
        Region.name,
        Region.description,
        Region.is_active,
        func.ST_AsGeoJSON(Region.boundary).label("boundary")
    ).where(Region.id == region_id)

    result = await db.execute(stmt)
    row = result.first()

    if not row:
        return None

    return {
        "id": row.id,
        "name": row.name,
        "description": row.description,
        "is_active": row.is_active,
        "boundary": json.loads(row.boundary)
    }
