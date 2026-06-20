import json
from datetime import date
from http.client import HTTPException
from typing import Optional
import pandas as pd

from sqlalchemy.ext.asyncio import AsyncSession

from repositories.bite_repo import create_bite, update_bite, delete_bite, get_filtered, add_bite_from_excel, \
    get_bites_for_region, reset_clusters, assign_cluster_to_bites
from models.bite import Bite


class BiteService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
            self,
            *,
            date_of_bite,
            point_wkt: str,
            location_description: Optional[str] = None
    ) -> Bite | None:

        try:
            bite = await create_bite(
                self.db,
                date_of_bite=date_of_bite,
                point_wkt=point_wkt,
                location_description=location_description,
            )

            if bite is None:
                await self.db.rollback()
                return None

            await self.db.commit()
            await self.db.refresh(bite)

            return bite

        except Exception:
            await self.db.rollback()
            raise

    async def update(self, bite_id: int, updates: dict) -> Optional[Bite]:
        try:
            bite = await update_bite(self.db, bite_id, updates)

            if not bite:
                return None

            await self.db.commit()
            await self.db.refresh(bite)

            return bite

        except Exception:
            await self.db.rollback()
            raise

    async def delete(self,  bite_id: int) -> bool:
        try:
            success = await delete_bite(self.db, bite_id)

            if not success:
                return False

            await self.db.commit()
            return True

        except Exception:
            await self.db.rollback()
            raise

    async def get_filtered(self, start_date: date | None, end_date: date | None, region_id: int | None):

        rows = await get_filtered(
            self.db,
            start_date=start_date,
            end_date=end_date,
            region_id=region_id
        )
        result = []

        for row in rows:
            result.append({
                "id": row.id,
                "date_of_bite": row.date_of_bite,
                "location_description": row.location_description,
                "cluster_id": row.cluster_id,
                "point_of_bite": json.loads(row.point_of_bite)
            })

        return result

    async def import_bites_from_excel(self, file_path: str) -> int:

        required_columns = ["date", "X_bite", "Y_bite", "location"]

        df = pd.read_excel(file_path, sheet_name=0)

        missing_cols = [c for c in required_columns if c not in df.columns]
        if missing_cols:
            raise HTTPException(
                status_code=400,
                detail=f"Отсутствуют столбцы: {', '.join(missing_cols)}"
            )

        df["X_bite"] = pd.to_numeric(df["X_bite"], errors="coerce")
        df["Y_bite"] = pd.to_numeric(df["Y_bite"], errors="coerce")
        df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")
        df = df.dropna(subset=["X_bite", "Y_bite", "date"])
        df["date"] = df["date"].dt.date

        added_count = 0

        try:
            for _, row in df.iterrows():

                bite = await add_bite_from_excel(
                    self.db,
                    date_of_bite=row.date,
                    x=float(row.X_bite),
                    y=float(row.Y_bite),
                    location=row.get("location")
                )

                if bite is not None:
                    added_count += 1

            await self.db.commit()

        except Exception:
            await self.db.rollback()
            raise

        return added_count

    async def get_bites_for_region(self, region_id: int):
        return await get_bites_for_region(self.db, region_id)

    async def reset_clusters(self, region_id: int):
        await reset_clusters(self.db, region_id)

    async def assign_cluster_to_bites(self, cluster_id: int, bite_ids: list[int]):
        await assign_cluster_to_bites(self.db, cluster_id, bite_ids)
