from db.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship, column_property
from datetime import date
from sqlalchemy import ForeignKey, BigInteger

from enums.bite_status_enum import WeatherStatus
from sqlalchemy import Enum as SqlEnum

from sqlalchemy.orm import column_property
from sqlalchemy import select, func

from models import Cluster


class ClusterData(Base):

    __tablename__ = 'cluster_data'

    date: Mapped[date]

    temperature: Mapped[float | None]

    avg_snow_depth: Mapped[float | None]

    amount_of_bites: Mapped[int]

    predicted_amount_of_bites: Mapped[int]

    cluster_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('clusters.id')
    )

    cluster: Mapped["Cluster"] = relationship(
        "Cluster",
        back_populates="cluster_data"
    )

    weather_status: Mapped[WeatherStatus] = mapped_column(
        SqlEnum(WeatherStatus, name="bites_status_enum"),
        default=WeatherStatus.PENDING,
        server_default=WeatherStatus.PENDING.value,
        nullable=False
    )


