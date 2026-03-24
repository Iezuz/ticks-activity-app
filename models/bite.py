from db.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date
from sqlalchemy import BigInteger, Boolean
from geoalchemy2 import Geometry, WKBElement
from sqlalchemy import ForeignKey


class Bite(Base):

    __tablename__ = "bites"

    date_of_bite: Mapped[date]

    location_description: Mapped[str | None]

    point_of_bite: Mapped[str] = mapped_column(
        Geometry("POINT", srid=4326)
    )

    region_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("regions.id"),
        nullable=True
    )

    region: Mapped["Region"] = relationship(
        "Region",
        back_populates="bites",
    )

    cluster_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("clusters.id"),
        nullable=True
    )

    cluster: Mapped["Cluster"] = relationship(
        "Cluster",
        back_populates="bites"
    )

    processed_for_cluster_data: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )


