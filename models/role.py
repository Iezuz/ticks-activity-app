from db.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enums.roles_enum import RoleEnum
from models.user_roles import user_roles


class Role(Base):

    __tablename__ = 'roles'

    name: Mapped[str] = mapped_column(default=RoleEnum.USER)

    users = relationship(
        "User",
        secondary=user_roles,
        back_populates="roles"
    )
