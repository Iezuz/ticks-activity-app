from db.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry
from sqlalchemy import Boolean, String
from typing import List


class Region(Base):

    __tablename__ = "regions"

    name: Mapped[str] = mapped_column(String(255), unique=True)
    description: Mapped[str | None]

    boundary: Mapped[str] = mapped_column(
        Geometry(geometry_type="MULTIPOLYGON", srid=4326)
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    clusters: Mapped[List["Cluster"] | None] = relationship(
        "Cluster",
        back_populates="region",
        cascade="all, delete-orphan"
    )
