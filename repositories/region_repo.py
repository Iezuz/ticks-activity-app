from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
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


async def get_region(db: AsyncSession, region_id: int) -> Optional[Region]:
    q = select(Region).where(Region.id == region_id)
    result = await db.execute(q)
    return result.scalars().first()
