from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from models.role import Role
from repositories.role_repo import create_role, get_role, get_role_by_name, list_roles, delete_role


class RoleService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, name: str) -> Role:
        try:
            role = await create_role(self.db, name)
            await self.db.commit()
            await self.db.refresh(role)
            return role
        except SQLAlchemyError:
            await self.db.rollback()
            raise

    async def get_by_id(self, role_id: int) -> Optional[Role]:
        return await get_role(self.db, role_id)

    async def get_by_name(self, name: str) -> Optional[Role]:
        return await get_role_by_name(self.db, name)

    async def list(self) -> Sequence[Role]:
        return await list_roles(self.db)

    async def delete(self, role_id: int) -> bool:
        try:
            role = await delete_role(self.db, role_id)
            if not role:
                await self.db.rollback()
                return False
            await self.db.commit()
            return True
        except SQLAlchemyError:
            await self.db.rollback()
            raise
