from sqlalchemy import select

from enums.bite_status_enum import WeatherStatus
from models import ClusterData
from services.сluster_data_weather_service import ClusterDataWeatherService
from db.database import async_session_maker
from sqlalchemy.orm import selectinload


async def run_fetching():

    batch_size = 1000

    async with async_session_maker() as db:

        weather_service = ClusterDataWeatherService()

        while True:

            result = await db.execute(
                select(ClusterData)
                .options(selectinload(ClusterData.cluster))
                .where(ClusterData.weather_status == WeatherStatus.PENDING)
                .order_by(ClusterData.id)
                .limit(batch_size)
            )

            cd = result.scalars().all()

            if not cd:
                print("Нет cluster_data с незаполненной погодой")
                break

            await weather_service.get_weather_data_by_coors(cd)

            print("Dirty objects:", db.dirty)
            print("Is modified:", db.is_modified(cd[0]))

            await db.commit()

            print(f"Обновлено {len(cd)} cluster_data")

    