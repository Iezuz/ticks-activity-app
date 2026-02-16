from sqlalchemy.ext.asyncio import AsyncSession
from models.role import Role

from sqlalchemy import select
from typing import Optional, Sequence


async def create_role(db: AsyncSession, name: str) -> Role:
    role = Role(name=name)
    db.add(role)
    await db.flush()
    return role


async def get_role(db: AsyncSession, role_id: int) -> Optional[Role]:
    q = select(Role).where(Role.id == role_id)
    result = await db.execute(q)
    return result.scalars().first()


async def get_role_by_name(db: AsyncSession, name: str) -> Optional[Role]:
    q = select(Role).where(Role.name == name)
    result = await db.execute(q)
    return result.scalars().first()


async def list_roles(db: AsyncSession) -> Sequence[Role]:
    q = select(Role)
    result = await db.execute(q)
    return result.scalars().all()


async def delete_role(db: AsyncSession, role_id: int) -> Optional[Role]:
    role = await get_role(db, role_id)
    if not role:
        return None
    await db.delete(role)
    return role
