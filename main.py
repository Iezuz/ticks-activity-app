from fastapi import FastAPI
from api.routers import regions
from api.routers import clusters
from api.routers import bites
import models

app = FastAPI()

app.include_router(regions.router)
app.include_router(clusters.router)
app.include_router(bites.router)

