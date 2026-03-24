from fastapi import APIRouter, Depends, HTTPException
from typing import List

from deps import get_region_service
from api.schemas.region import RegionCreate, RegionListRead, RegionDetailRead
from services.region_service import RegionService

router = APIRouter(prefix="/regions", tags=["Regions"])


@router.get("/", response_model=List[RegionListRead])
async def get_regions(service: RegionService = Depends(get_region_service)):
    return await service.list()


@router.get("/{region_id}", response_model=RegionDetailRead)
async def get_region_by_id(region_id: int, service: RegionService = Depends(get_region_service)):
    region = await service.get_by_id(region_id)
    if not region:
        raise HTTPException(status_code=404, detail="Регион не найден")
    return region


# @router.post("/", response_model=RegionRead)
# async def create_new_region(data: RegionCreate, service: RegionService = Depends(get_region_service)):
#     return await service.create_region_with_grid(
#         name=data.name,
#         boundary_wkt=data.boundary_wkt,
#         description=data.description
#     )
