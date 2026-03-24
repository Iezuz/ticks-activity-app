from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from typing import List

from deps import get_cluster_service
from services.cluster_service import ClusterService
from api.schemas.cluster import ClusterRead, ClusterActivityRead
from datetime import date

router = APIRouter(prefix="/clusters", tags=["Clusters"])


@router.get("/", response_model=List[ClusterRead])
async def list_clusters(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    service: ClusterService = Depends(get_cluster_service),
):
    return await service.list(skip=offset, limit=limit)


@router.get("/{cluster_id}", response_model=ClusterRead)
async def get_cluster_by_id(cluster_id: int, service: ClusterService = Depends(get_cluster_service)):
    cluster = await service.get_by_id(cluster_id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Кластер не найден")
    return cluster


@router.get("/region/{region_id}", response_model=List[ClusterRead])
async def get_clusters_by_region(
    region_id: int,
    service: ClusterService = Depends(get_cluster_service),
):
    clusters = await service.get_by_region(region_id)
    return clusters


@router.delete("/{cluster_id}")
async def delete_cluster(cluster_id: int, service: ClusterService = Depends(get_cluster_service)):
    deleted = await service.delete(cluster_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Кластер не найден")
    return {"detail": "Кластер удалён"}


# @router.get("/bbox/", response_model=List[ClusterRead])
# async def get_clusters_in_bbox(
#     min_lon: float = Query(..., description="Минимальная долгота"),
#     min_lat: float = Query(..., description="Минимальная широта"),
#     max_lon: float = Query(..., description="Максимальная долгота"),
#     max_lat: float = Query(..., description="Максимальная широта"),
#     service: ClusterService = Depends(get_cluster_service),
# ):
#     if min_lon >= max_lon or min_lat >= max_lat:
#         raise HTTPException(status_code=400, detail="Некорректный bounding box")
#
#     return await service.list_clusters_in_bbox(
#         min_lon=min_lon,
#         min_lat=min_lat,
#         max_lon=max_lon,
#         max_lat=max_lat,
#     )


@router.get("/region/{region_id}/activity", response_model=List[ClusterActivityRead])
async def get_cluster_activity(region_id: int, date_par: date = Query(...),
                               service: ClusterService = Depends(get_cluster_service)):
    return await service.get_cluster_activity(region_id, date_par)


@router.post("/rebuild/{region_id}")
async def rebuild_clusters(
    region_id: int,
    background_tasks: BackgroundTasks,
    service: ClusterService = Depends(get_cluster_service),
):

    background_tasks.add_task(service.build_clusters, region_id)

    return {
        "status": "started",
        "message": "Пересоздание кластеров началось"
    }
