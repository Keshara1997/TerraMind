
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


# ==========================================
# CORS Configuration
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# Root Endpoint
# ==========================================

@app.get("/", tags=["Root"])
def root():
    return {
        "application": settings.APP_NAME,
        "version": "0.1.0",
        "environment": settings.APP_ENV,
        "message": "Welcome to Aleph Next API",
        "documentation": "/docs",
    }


# ==========================================
# Health Endpoints
# ==========================================

app.include_router(health.router)


# ==========================================
# Versioned API
# ==========================================

app.include_router(
    api_router,
    prefix=settings.API_V1_PREFIX,
)


@app.get("/api/v1/", tags=["API"])
def api_version():
    return {
        "api": "Aleph Next",
        "version": "v1",
        "status": "available",
    }
