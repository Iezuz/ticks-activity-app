from pydantic import BaseModel
from typing import Optional


class RegionCreate(BaseModel):
    name: str
    boundary_wkt: str
    description: Optional[str] = None


class RegionRead(BaseModel):
    id: int
    name: str
    description: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True
