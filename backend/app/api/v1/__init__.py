
from fastapi import APIRouter
from app.api.v1.endpoints import captures

from app.api.v1.endpoints import areas, auth, projects


api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(projects.router)
api_router.include_router(areas.router)
api_router.include_router(captures.router)