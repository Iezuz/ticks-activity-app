from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from repositories.bite_repo import create_bite, update_bite, delete_bite
from models.bite import Bite


class BiteService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        *,
        date_of_bite,
        point_wkt: str,
        location_description: Optional[str] = None,
        elevation: Optional[float] = None,
        snow_depth: Optional[float] = None,
    ) -> Bite:

        try:
            bite = await create_bite(
                self.db,
                date_of_bite=date_of_bite,
                point_wkt=point_wkt,
                location_description=location_description,
                elevation=elevation,
                snow_depth=snow_depth,
            )

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
