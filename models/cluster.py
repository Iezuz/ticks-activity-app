from db.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry
from sqlalchemy import ForeignKey, BigInteger


class Cluster(Base):

    __tablename__ = 'clusters'

    geometry: Mapped[str] = mapped_column(Geometry(geometry_type="POLYGON", srid=4326))

    cluster_data: Mapped[list["ClusterData"]] = relationship(
        "ClusterData",
        back_populates="cluster",
        cascade="all, delete-orphan"
    )

    bites: Mapped[list["Bite"]] = relationship(
        "Bite",
        back_populates="cluster",
        cascade="all, delete-orphan"
    )

    region_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("regions.id"),
        nullable=False
    )

    region: Mapped["Region"] = relationship(
        "Region",
        back_populates="clusters"
    )

