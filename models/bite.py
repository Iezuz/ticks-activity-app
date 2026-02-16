from db.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date
from sqlalchemy import BigInteger
from geoalchemy2 import Geometry
from sqlalchemy import ForeignKey


class Bite(Base):

    __tablename__ = 'bites'

    date_of_bite: Mapped[date]

    location_description: Mapped[str | None]

    temperature: Mapped[float | None]

    elevation: Mapped[float | None]

    snow_depth: Mapped[float | None]

    point_of_bite: Mapped[str] = mapped_column(Geometry('POINT', srid=4326))

    cluster_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey('clusters.id'))

    cluster: Mapped["Cluster"] = relationship(
        "Cluster",
        back_populates="bites"
    )
