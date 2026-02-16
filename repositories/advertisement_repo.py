from sqlalchemy.ext.asyncio import AsyncSession
from models.advertisement import Advertisement
from sqlalchemy import select, delete
from typing import Any, Dict, Optional, List, Sequence
from repositories._apply_updates import _apply_updates


async def create_advertisement(
    db: AsyncSession,
    *,
    target_url: Optional[str] = None,
    banner_url: Optional[str] = None,
    clicks_amount: int = 0,
) -> Advertisement:

    ad = Advertisement(
        target_URL=target_url,
        banner_URL=banner_url,
        amount_of_clicks=clicks_amount,
    )
    db.add(ad)
    return ad


async def get_advertisement(db: AsyncSession, ad_id: int) -> Optional[Advertisement]:

    result = await db.execute(select(Advertisement).where(Advertisement.id == ad_id))
    return result.scalars().first()


async def list_advertisements(db: AsyncSession, skip: int = 0, limit: int = 100) -> Sequence[Advertisement]:

    q = select(Advertisement).offset(skip).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


# async def update_advertisement(db: AsyncSession, ad_id: int, updates: Dict[str, Any]) -> Optional[Advertisement]:
#
#     ad = await get_advertisement(db, ad_id)
#     if not ad:
#         return None
#
#     _apply_updates(ad, updates, exclude=["id"])
#     db.add(ad)
#     await db.commit()
#     await db.refresh(ad)
#     return ad


async def delete_advertisement_by_id(db: AsyncSession, ad_id: int) -> Optional[Advertisement]:

    result = await db.execute(select(Advertisement.id).where(Advertisement.id == ad_id))
    found = result.scalars().first()
    if not found:
        return None
    await db.delete(found)
    return found


