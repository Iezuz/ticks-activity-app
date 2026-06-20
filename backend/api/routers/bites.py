import json
import os
from datetime import date
import tempfile
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from typing import List

from api.schemas.bite import BiteCreate, BiteRead, BiteUpdate
from services.bite_service import BiteService
from deps import get_bite_service
from repositories.bite_repo import get_bite, list_bites
from sqlalchemy import func, select
from models.bite import Bite


router = APIRouter(prefix="/bites", tags=["Bites"])


@router.post("/", response_model=BiteRead)
async def create_bite(
    data: BiteCreate,
    service: BiteService = Depends(get_bite_service),
):
    try:
        bite = await service.create(**data.dict())
        if bite is None:
            raise HTTPException(status_code=400, detail="Не найден регион для точки")
        return await _serialize_bite(service, bite.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{bite_id}", response_model=BiteRead)
async def get_one_bite(
    bite_id: int,
    service: BiteService = Depends(get_bite_service),
):
    bite = await _serialize_bite(service, bite_id)
    if not bite:
        raise HTTPException(status_code=404, detail="Bite not found")
    return bite


@router.get("/", response_model=List[BiteRead])
async def get_bites(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    region_id: int | None = Query(None),
    service: BiteService = Depends(get_bite_service),
):
    bites = await service.get_filtered(start_date, end_date, region_id)
    return bites


# @router.patch("/{bite_id}", response_model=BiteRead)
# async def update_bite(
#     bite_id: int,
#     data: BiteUpdate,
#     service: BiteService = Depends(get_bite_service),
# ):
#     bite = await service.update(bite_id, data.dict(exclude_unset=True))
#     if not bite:
#         raise HTTPException(status_code=404, detail="Bite not found")
#
#     return await _serialize_bite(service, bite.id)


@router.delete("/{bite_id}")
async def delete_bite(
    bite_id: int,
    service: BiteService = Depends(get_bite_service),
):
    success = await service.delete(bite_id)
    if not success:
        raise HTTPException(status_code=404, detail="Bite not found")

    return {"status": "deleted"}


@router.post("/import")
async def import_bites(file: UploadFile = File(...), service: BiteService = Depends(get_bite_service)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        tmp_path = tmp.name
        tmp.write(await file.read())

    try:
        count = await service.import_bites_from_excel(tmp_path)
    finally:
        os.remove(tmp_path)


async def _serialize_bite(service: BiteService, bite_id: int):
    query = select(
        Bite.id,
        Bite.date_of_bite,
        Bite.location_description,
        Bite.cluster_id,
        func.ST_AsGeoJSON(Bite.point_of_bite).label("point_of_bite"),
    ).where(Bite.id == bite_id)

    result = await service.db.execute(query)
    row = result.first()

    if not row:
        return None

    return {
        "id": row.id,
        "date_of_bite": row.date_of_bite,
        "location_description": row.location_description,
        "cluster_id": row.cluster_id,
        "point_of_bite": json.loads(row.point_of_bite)
        if row.point_of_bite
        else None,
    }


