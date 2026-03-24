from pydantic import BaseModel
from typing import Optional, Dict, Any


class RegionCreate(BaseModel):
    name: str
    boundary_wkt: str
    description: Optional[str] = None


class RegionListRead(BaseModel):
    id: int
    name: str
    description: Optional[str]
    is_active: bool


class RegionDetailRead(RegionListRead):
    boundary: Dict[str, Any]

    class Config:
        from_attributes = True
