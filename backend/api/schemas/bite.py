from datetime import date
from pydantic import BaseModel, Field
from typing import Optional


class BiteCreate(BaseModel):
    date_of_bite: date
    point_wkt: str
    location_description: Optional[str] = None


class BiteUpdate(BaseModel):
    date_of_bite: Optional[date] = None
    point_wkt: Optional[str] = None
    location_description: Optional[str] = None


class BiteRead(BaseModel):
    id: int
    date_of_bite: date
    location_description: Optional[str]
    cluster_id: Optional[int]
    point_of_bite: dict

    class Config:
        from_attributes = True
