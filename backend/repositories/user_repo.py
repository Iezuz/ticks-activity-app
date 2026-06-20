from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from models.role import Role

from sqlalchemy import select
from typing import Optional, Dict, List, Sequence, Any

from repositories._apply_updates import _apply_updates


async def create_user(
        db: AsyncSession, username: str,
        password_hash: str,
        role_ids: Optional[List[int]] = None
) -> User:

    user = User(username=username, password_hash=password_hash)

    if role_ids:
        q = select(Role).where(Role.id.in_(role_ids))
        result = await db.execute(q)
        roles = result.scalars().all()
        user.roles = roles

    db.add(user)
    await db.flush()
    return user


async def get_user(db: AsyncSession, user_id: int) -> Optional[User]:
    q = select(User).where(User.id == user_id)
    result = await db.execute(q)
    return result.scalars().first()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    q = select(User).where(User.username == username)
    result = await db.execute(q)
    return result.scalars().first()


async def list_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> Sequence[User]:
    q = select(User).offset(skip).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


async def update_user(db: AsyncSession, user_id: int, updates: Dict[str, Any]) -> Optional[User]:
    user = await get_user(db, user_id)
    if not user:
        return None

    if "role_ids" in updates:
        role_ids = updates.pop("role_ids")
        q = select(Role).where(Role.id.in_(role_ids))
        result = await db.execute(q)
        roles = result.scalars().all() if role_ids else []
        user.roles = roles

    _apply_updates(user, updates, exclude=["id", "username"])
    db.add(user)
    return user


async def delete_user(db: AsyncSession, user_id: int) -> Optional[User]:
    user = await get_user(db, user_id)
    if not user:
        return None
    await db.delete(user)
    return user
