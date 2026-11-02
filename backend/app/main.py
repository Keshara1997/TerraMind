
from fastapi import FastAPI

from app.api.v1 import api_router
from app.api.v1.endpoints import health
from app.core.config import settings


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Geospatial exploration, data collection, "
        "processing and AI-assisted analysis platform."
    ),
    version="0.1.0",
    debug=settings.APP_DEBUG,
)


@app.get("/", tags=["Root"])
def root():
    return {
        "application": settings.APP_NAME,
        "version": "0.1.0",
        "environment": settings.APP_ENV,
        "message": "Welcome to TerraMind Next API",
        "documentation": "/docs",
    }


# Infrastructure health endpoints
app.include_router(health.router)


# Versioned business API
app.include_router(
    api_router,
    prefix=settings.API_V1_PREFIX,
)


@app.get("/api/v1/", tags=["API"])
def api_version():
    return {
        "api": "TerraMind Next",
        "version": "v1",
        "status": "available",
    }
