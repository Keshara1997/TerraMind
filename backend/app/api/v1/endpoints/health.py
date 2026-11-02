
from fastapi import APIRouter, HTTPException, status

from app.core.redis import check_redis_connection
from app.database.session import check_database_connection


router = APIRouter(
    tags=["Health"],
)


@router.get("/health")
def application_health():
    """
    Check application availability.
    """

    return {
        "status": "healthy",
        "application": "TerraMind Next",
        "environment": "development",
    }


@router.get("/health/database")
def database_health():
    """
    Check PostgreSQL connectivity.
    """

    if not check_database_connection():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "service": "postgresql",
            },
        )

    return {
        "status": "healthy",
        "service": "postgresql",
        "database": "connected",
    }


@router.get("/health/redis")
def redis_health():
    """
    Check Redis connectivity.
    """

    if not check_redis_connection():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "service": "redis",
            },
        )

    return {
        "status": "healthy",
        "service": "redis",
        "connection": "connected",
    }
