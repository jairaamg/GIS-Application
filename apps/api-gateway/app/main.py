from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import datasets, health, jobs, layers, projects, tiles
from app.config.settings import get_settings

settings = get_settings()

app = FastAPI(
    title="Open-Source 2D/3D GIS Platform API",
    version="0.1.0",
    description="API Gateway / BFF — modular domains for day-one development.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(projects.router, prefix="/api/v1")
app.include_router(datasets.router, prefix="/api/v1")
app.include_router(jobs.router, prefix="/api/v1")
app.include_router(layers.router, prefix="/api/v1")
app.include_router(tiles.router, prefix="/api/v1")


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "service": settings.service_name,
        "docs": "/docs",
        "health": "/health/live",
    }
