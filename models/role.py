from db.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enums.roles_enum import RoleEnum
from models.user_roles import user_roles
from sqlalchemy import Enum as SqlEnum


class Role(Base):

    __tablename__ = 'roles'

    name: Mapped[RoleEnum] = mapped_column(
        SqlEnum(RoleEnum, name="role_enum"),
        nullable=False,
        default=RoleEnum.USER)

    users = relationship(
        "User",
        secondary=user_roles,
        back_populates="roles"
    )
