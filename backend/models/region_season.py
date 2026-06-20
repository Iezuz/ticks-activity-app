from sqlalchemy import Column, BigInteger, ForeignKey, Integer, Date

from backend.db.database import Base


class RegionSeason(Base):
    __tablename__ = "region_season"

    region_id = Column(BigInteger, ForeignKey("regions.id"), primary_key=True)
    year = Column(Integer, primary_key=True)

    season_start_date = Column(Date, nullable=False)