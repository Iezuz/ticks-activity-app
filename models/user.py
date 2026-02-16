from db.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship


from models.user_roles import user_roles


class User(Base):

    __tablename__ = 'users'
    
    username: Mapped[str] = mapped_column(unique=True)

    password_hash: Mapped[str]

    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary=user_roles,
        back_populates="users"
    )
