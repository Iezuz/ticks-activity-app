from pydantic import BaseModel
from typing import Any
from dataclasses import dataclass


class ClusterRead(BaseModel):
    id: int
    name: str | None = None
    geometry: dict | None = None
    elevation: int | None = None

    class Config:
        from_attributes = True


class ClusterActivityRead(BaseModel):
    cluster_id: int
    geometry: Any
    amount: int


@dataclass
class ClusterResult:
    polygon_wkt: str
    bite_ids: list[int]
