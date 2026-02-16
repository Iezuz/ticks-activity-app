from fastapi import FastAPI
from api.routers import regions
import models

app = FastAPI()

app.include_router(regions.router)

