from db.database import Base
from sqlalchemy.orm import Mapped


class Advertisement(Base):
    __tablename__ = 'advertisements'

    target_URL: Mapped[str | None]

    banner_URL: Mapped[str | None]

    amount_of_clicks: Mapped[int]
