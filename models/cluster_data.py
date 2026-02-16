from db.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date
from sqlalchemy import ForeignKey, BigInteger


class ClusterData(Base):

    __tablename__ = 'cluster_data'

    date: Mapped[date]

    temperature: Mapped[float | None]

    avg_elevation: Mapped[float | None]

    avg_snow_depth: Mapped[float | None]

    amount_of_bites: Mapped[int]

    predicted_amount_of_bites: Mapped[int]

    cluster_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('clusters.id'))

    cluster:  Mapped["Cluster"] = relationship(
        "Cluster",
        back_populates="cluster_data"
    )
