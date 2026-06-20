from typing import Optional, Sequence, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from models.user import User
from repositories.user_repo import (create_user, get_user, get_user_by_username,
                                    list_users, update_user, delete_user)


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        username: str,
        password_hash: str,
        role_ids: Optional[List[int]] = None
    ) -> User:

        try:
            user = await create_user(self.db, username, password_hash, role_ids)
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except SQLAlchemyError:
            await self.db.rollback()
            raise

    async def get_by_id(self, user_id: int) -> Optional[User]:
        return await get_user(self.db, user_id)

    async def get_by_name(self, username: str) -> Optional[User]:
        return await get_user_by_username(self.db, username)

    async def list_users_service(self, skip: int = 0, limit: int = 100) -> Sequence[User]:
        return await list_users(self.db, skip, limit)

    async def update_user_service(self, user_id: int, updates: Dict[str, Any]) -> Optional[User]:
        try:
            user = await update_user(self.db, user_id, updates)
            if not user:
                await self.db.rollback()
                return None
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except SQLAlchemyError:
            await self.db.rollback()
            raise

    async def delete_user_service(self, user_id: int) -> bool:
        try:
            user = await delete_user(self.db, user_id)
            if not user:
                await self.db.rollback()
                return False
            await self.db.commit()
            return True
        except SQLAlchemyError:
            await self.db.rollback()
            raise
