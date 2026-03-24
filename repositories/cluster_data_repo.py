from typing import Any, Dict, Optional, List, Sequence
from datetime import date

from enums.bite_status_enum import WeatherStatus
from models import Bite, Cluster
from models.cluster_data import ClusterData
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update

from repositories._apply_updates import _apply_updates

BATCH_SIZE = 500


async def get_cluster_data_by_cluster_and_date(
        db: AsyncSession, cluster_id: int, cluster_date: date
) -> ClusterData | None:
    result = await db.execute(
        select(ClusterData)
        .where(ClusterData.cluster_id == cluster_id, ClusterData.date == cluster_date)
    )
    return result.scalars().first()


async def create_cluster_data_from_bites(
        db: AsyncSession,
        cluster_id: int,
        cluster_date: date,
        bite_count: int
) -> ClusterData:
    cd = ClusterData(
        cluster_id=cluster_id,
        date=cluster_date,
        amount_of_bites=bite_count,
        predicted_amount_of_bites=0,
        avg_snow_depth=None,
        temperature=None
    )
    db.add(cd)
    await db.flush()
    return cd


async def update_cluster_data_from_bites(
        db: AsyncSession, cluster_data: ClusterData, bite_count: int
) -> ClusterData:
    cluster_data.amount_of_bites = bite_count
    db.add(cluster_data)
    await db.flush()
    return cluster_data


async def get_grouped_bites(db: AsyncSession, batch_size: int = BATCH_SIZE) -> List[Dict]:
    """
    Получает сгруппированные по cluster_id и date_of_bite укусы
    """
    result = await db.execute(
        select(
            Bite.cluster_id,
            Bite.date_of_bite.label("date"),
            func.count(Bite.id).label("bite_count")
        )
        .where(Bite.processed_for_cluster_data == False)
        .group_by(Bite.cluster_id, Bite.date_of_bite)
        .limit(batch_size)
    )
    rows = result.all()
    return [{"cluster_id": r.cluster_id, "date": r.date, "bite_count": r.bite_count} for r in rows]


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


async def get_all_cluster_ids(db: AsyncSession) -> List[int]:
    result = await db.execute(select(ClusterData.cluster_id).distinct())
    return [r[0] for r in result.all()]


async def mark_bites_as_processed(
        db: AsyncSession,
        cluster_id: int,
        cluster_date: date
):
    await db.execute(
        update(Bite)
        .where(
            Bite.cluster_id == cluster_id,
            Bite.date_of_bite == cluster_date,
            Bite.processed_for_cluster_data == False
        )
        .values(processed_for_cluster_data=True)
    )


async def get_cluster_data_pending_weather(
    db: AsyncSession, batch_size: int = 1000
) -> List[ClusterData]:
    """
    Получает пакет ClusterData, у которых weather_status = PENDING.
    """
    q = (
        select(
            ClusterData.id,
            ClusterData.cluster_id,
            ClusterData.date,
            ClusterData.temperature,
            ClusterData.avg_snow_depth,
            ClusterData.weather_status,
            func.ST_AsText(func.ST_Centroid(Cluster.geometry)).label("centroid_wkt")
        )
        .join(Cluster, Cluster.id == ClusterData.cluster_id)
        .where(ClusterData.weather_status == WeatherStatus.PENDING)
        .limit(batch_size)
    )
    result = await db.execute(q)
    rows = result.all()
    return rows
