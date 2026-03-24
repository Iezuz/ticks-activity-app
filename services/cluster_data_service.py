from typing import Optional, Sequence, Dict, Any, List
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from models import ClusterData
from repositories import cluster_data_repo as repo
from repositories.cluster_data_repo import get_grouped_bites, get_cluster_data_by_cluster_and_date, \
    update_cluster_data_from_bites, create_cluster_data_from_bites, get_all_cluster_ids, mark_bites_as_processed


class ClusterDataService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def process_bites(self, batch_size: int = 1000) -> list[dict]:
        """
        Создаёт или обновляет ClusterData на основе реальных укусов
        """
        created_or_updated = []

        while True:
            batch = await get_grouped_bites(self.db, batch_size=batch_size)
            print(f'Получено для создания cluster_data {batch_size} записей об укусах')
            if not batch:
                break

            for item in batch:
                cluster_id = item["cluster_id"]
                cluster_date = item["date"]
                bite_count = item["bite_count"]

                cd = await get_cluster_data_by_cluster_and_date(self.db, cluster_id, cluster_date)
                if cd:
                    cd = await update_cluster_data_from_bites(self.db, cd, bite_count)
                else:
                    cd = await create_cluster_data_from_bites(self.db, cluster_id, cluster_date, bite_count)

                await mark_bites_as_processed(self.db, cluster_id, cluster_date)

                created_or_updated.append({
                    "cluster_id": cd.cluster_id,
                    "date": cd.date,
                    "amount_of_bites": cd.amount_of_bites
                })

            try:
                await self.db.commit()
            except SQLAlchemyError:
                await self.db.rollback()
                raise

        return created_or_updated

    async def create_future_dates(self, future_dates: list[date]) -> list[dict]:
        """
        Создаёт ClusterData для будущих дат
        """
        created = []

        cluster_ids = await get_all_cluster_ids(self.db)

        for future_date in future_dates:
            for cluster_id in cluster_ids:
                cd = await get_cluster_data_by_cluster_and_date(self.db, cluster_id, future_date)
                if not cd:
                    cd = ClusterData(
                        cluster_id=cluster_id,
                        date=future_date,
                        amount_of_bites=0,
                        predicted_amount_of_bites=0,
                        avg_snow_depth=None,
                        weather_status="PENDING"
                    )
                    self.db.add(cd)
                    await self.db.flush()
                    created.append({
                        "cluster_id": cluster_id,
                        "date": future_date,
                        "amount_of_bites": 0
                    })

        try:
            await self.db.commit()
        except SQLAlchemyError:
            await self.db.rollback()
            raise

        return created

    async def get_by_id(self, cd_id: int) -> Optional[ClusterData]:
        return await repo.get_cluster_data(self.db, cd_id)

    async def list_for_cluster(
        self,
        cluster_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[ClusterData]:

        return await repo.list_cluster_data_for_cluster(self.db, cluster_id, skip, limit)

    async def update(self, cd_id: int, updates: Dict[str, Any]) -> Optional[ClusterData]:
        try:
            cd = await repo.update_cluster_data(self.db, cd_id, updates)

            if not cd:
                return None

            await self.db.commit()
            await self.db.refresh(cd)
            return cd

        except SQLAlchemyError:
            await self.db.rollback()
            raise

    async def delete(self, cd_id: int) -> bool:
        try:
            success = await repo.delete_cluster_data(self.db, cd_id)

            if not success:
                return False

            await self.db.commit()
            return True

        except SQLAlchemyError:
            await self.db.rollback()
            raise



