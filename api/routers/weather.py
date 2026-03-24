from fastapi import APIRouter, BackgroundTasks
from tasks.weather_tasks import run_fetching

router = APIRouter(prefix="/bites", tags=["Weather"])


@router.post("/weather/enrich-missing")
async def enrich_missing_weather(background_tasks: BackgroundTasks):

    background_tasks.add_task(run_fetching)

    return {"status": "bulk enrichment started"}
