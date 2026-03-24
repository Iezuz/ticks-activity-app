from shapely import wkt
from shapely.geometry import shape
from db.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry, WKBElement
from sqlalchemy import ForeignKey, BigInteger


class Cluster(Base):

    __tablename__ = 'clusters'

    geometry: Mapped[WKBElement] = mapped_column(Geometry(geometry_type="POLYGON", srid=4326))

    cluster_data: Mapped[list["ClusterData"]] = relationship(
        "ClusterData",
        back_populates="cluster",
        cascade="all, delete-orphan"
    )

    elevation: Mapped[float | None]

    bites: Mapped[list["Bite"]] = relationship(
        "Bite",
        back_populates="cluster"
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

    centroid: Mapped[str] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326),
        nullable=False
    )

    # @property
    # def centroid_wkt(self) -> str:
    #     if self.geometry is None:
    #         return None
    #
    #     geom_wkt = None
    #     try:
    #         geom_wkt = self.geometry.desc
    #     except AttributeError:
    #         try:
    #             geom_wkt = str(self.geometry)
    #         except Exception:
    #             return None
    #
    #     return wkt.dumps(shape(wkt.loads(geom_wkt)).centroid)

