from fastapi import APIRouter, BackgroundTasks, Depends
from typing import List, Dict

from datetime import date

from services.cluster_data_service import ClusterDataService
from deps import get_cluster_data_service


router = APIRouter(prefix="/cluster_data", tags=["ClusterData"])


@router.post("/from-bites")
async def create_cluster_data_from_bites(service: ClusterDataService = Depends(get_cluster_data_service)):
    created_or_updated = await service.process_bites()
    return {"status": "ok", "processed": len(created_or_updated)}


@router.post("/future-dates")
async def create_cluster_data_future_dates(
    future_dates: list[date],
    service: ClusterDataService = Depends(get_cluster_data_service)
):
    created = await service.create_future_dates(future_dates)
    return {"status": "ok", "created": len(created)}
