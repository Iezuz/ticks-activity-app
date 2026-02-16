from typing import Any, Dict, Optional, List, Sequence
from datetime import date
from models.cluster_data import ClusterData
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from repositories._apply_updates import _apply_updates


async def create_cluster_data(
        db: AsyncSession,
        cluster_id: int,
        cluster_date: date,
        avg_elevation: Optional[float] = None,
        avg_snow_depth: Optional[float] = None
) -> ClusterData:

    cd = ClusterData(
        cluster_id=cluster_id,
        amount_of_bites=0,
        predicted_amount_of_bites=0,
        date=cluster_date,
        avg_elevation=avg_elevation,
        avg_snow_depth=avg_snow_depth
    )

    db.add(cd)
    return cd


async def get_cluster_data(db: AsyncSession, cd_id: int) -> Optional[ClusterData]:
    result = await db.execute(select(ClusterData).where(ClusterData.id == cd_id))
    return result.scalars().first()


async def list_cluster_data_for_cluster(
    db: AsyncSession,
    cluster_id: int,
    skip: int = 0,
    limit: int = 100,
) -> Sequence[ClusterData]:

    q = (
        select(ClusterData)
        .where(ClusterData.cluster_id == cluster_id)
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(q)
    return result.scalars().all()


async def update_cluster_data(db: AsyncSession, cd_id: int, updates: Dict[str, Any]) -> Optional[ClusterData]:

    cd = await get_cluster_data(db, cd_id)
    if not cd:
        return None

    _apply_updates(cd, updates, exclude=["id", "cluster_id"])

    db.add(cd)
    return cd


async def delete_cluster_data(db: AsyncSession, cd_id: int) -> Optional[ClusterData]:
    cd = await get_cluster_data(db, cd_id)
    if not cd:
        return None
    await db.delete(cd)
    return cd
