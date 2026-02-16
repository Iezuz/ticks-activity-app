from typing import Optional, Sequence, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from repositories import advertisement_repo as repo
from models import Advertisement


class AdvertisementService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        *,
        target_url: Optional[str] = None,
        banner_url: Optional[str] = None,
        clicks_amount: int = 0,
    ) -> Advertisement:

        ad = await repo.create_advertisement(
            self.db,
            target_url=target_url,
            banner_url=banner_url,
            clicks_amount=clicks_amount,
        )

        await self.db.commit()
        await self.db.refresh(ad)
        return ad

    async def get_by_id(self, ad_id: int) -> Optional[Advertisement]:
        return await repo.get_advertisement(self.db, ad_id)

    async def list(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[Advertisement]:
        return await repo.list_advertisements(self.db, skip, limit)

    async def update(
        self,
        ad_id: int,
        updates: Dict[str, Any],
    ) -> Optional[Advertisement]:

        ad = await repo.get_advertisement(self.db, ad_id)
        if not ad:
            return None

        for key, value in updates.items():
            if key != "id":
                setattr(ad, key, value)

        await self.db.commit()
        await self.db.refresh(ad)
        return ad

    async def delete(self, ad_id: int) -> bool:
        deleted = await repo.delete_advertisement_by_id(self.db, ad_id)
        if not deleted:
            return False

        await self.db.commit()
        return True

