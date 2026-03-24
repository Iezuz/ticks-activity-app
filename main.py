from fastapi import FastAPI
from api.routers import regions
from api.routers import clusters
from api.routers import bites
from api.routers import weather
from api.routers import cluster_data
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(regions.router)
app.include_router(clusters.router)
app.include_router(bites.router)
app.include_router(weather.router)
app.include_router(cluster_data.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)