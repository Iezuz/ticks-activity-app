from sqlalchemy import select, func

from enums.bite_status_enum import WeatherStatus
from models import ClusterData
from services.сluster_data_weather_service import ClusterDataWeatherService
from db.database import async_session_maker
from models.cluster import Cluster


async def run_fetching():

    batch_size = 1000

    async with async_session_maker() as db:

        weather_service = ClusterDataWeatherService()

        while True:
            print("перед запросом")
            result = await db.execute(
                select(
                    ClusterData.id,
                    ClusterData.date,
                    ClusterData.cluster_id,
                    func.ST_Y(Cluster.centroid).label("lat"),
                    func.ST_X(Cluster.centroid).label("lon"),
                )
                .join(Cluster, Cluster.id == ClusterData.cluster_id)
                .where(ClusterData.weather_status == WeatherStatus.PENDING)
                .order_by(ClusterData.id)
                .limit(batch_size)
            )

            cluster_datas = result.all()

            if not cluster_datas:
                print("Нет cluster_data с незаполненной погодой")
                break

            await weather_service.process_batch(db, cluster_datas)
            print("получены данные о погоде")
            await db.commit()

            print("Dirty objects:", db.dirty)
            #print("Is modified:", db.is_modified(cluster_datas[0]))

            print(f"Обновлено {len(cluster_datas)} cluster_data")

    