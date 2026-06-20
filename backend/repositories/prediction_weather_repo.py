from datetime import date
from datetime import timedelta

from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from backend.models.cluster_data import ClusterData
from backend.models.cluster import Cluster



async def get_short_term_cluster_data(db):
    today = date.today()
    end_date = today + timedelta(days=7)

    result = await db.execute(
        select(ClusterData)
        .join(Cluster)
        .options(
            selectinload(
                ClusterData.cluster
            )
        )
        .where(ClusterData.date >= today, ClusterData.date <= end_date)
    )

    return result.scalars().all()


async def bulk_update_forecast_weather(db, updates):
    for item in updates:
        await db.execute(
            update(ClusterData)
            .where(ClusterData.id == item["id"])
            .values(
                temperature=item["temperature"],
                precipitation=item["precipitation"],
                cloudiness=item["cloudiness"],
                weather_status="SUCCESS",
            )
        )