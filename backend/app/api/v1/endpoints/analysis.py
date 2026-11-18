from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.change_detection import NDVIChangeRequest, NDVIChangeResponse
from app.schemas.time_series import (
    NDVITimeSeriesPoint,
    NDVITimeSeriesResponse,
)
from app.services.time_series_service import get_ndvi_time_series

router = APIRouter(prefix="/analysis", tags=["Analysis"])


@router.get(
    "/projects/{project_id}/ndvi-time-series",
    response_model=NDVITimeSeriesResponse,
)
def read_ndvi_time_series(
    project_id: UUID,
    area_id: UUID | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="start_date must be before or equal to end_date",
        )

    # Replace this with the project-access function already used
    # by your projects, captures and areas endpoints.
    from app.services.project_service import ProjectService

    project_service = ProjectService(db)
    project_service.get_project(project_id, current_user.id)

    points = get_ndvi_time_series(
        db=db,
        project_id=project_id,
        area_id=area_id,
        start_date=start_date,
        end_date=end_date,
    )

    return NDVITimeSeriesResponse(
        project_id=project_id,
        area_id=area_id,
        start_date=start_date,
        end_date=end_date,
        total_observations=len(points),
        points=[
            NDVITimeSeriesPoint(**point)
            for point in points
        ],
    )


@router.post(
    "/projects/{project_id}/ndvi-change",
    response_model=NDVIChangeResponse,
    status_code=202,
)
def create_ndvi_change(
    project_id: UUID,
    payload: NDVIChangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    from app.services.project_service import ProjectService

    ProjectService(db).get_project(project_id, current_user.id)

    if payload.before_dataset_id == payload.after_dataset_id:
        raise HTTPException(
            status_code=400,
            detail="Select two different NDVI datasets",
        )

    # Implement dataset ownership and status checks here before dispatch.
    # Both datasets must belong to this project and be completed NDVI outputs.
    #
    # Create the output Dataset record and commit it before dispatching.
    # Dispatch the Celery task with the output dataset ID and threshold.
    #
    # Return the new output dataset ID and its processing status.

    raise HTTPException(
        status_code=501,
        detail="Connect this endpoint to your change-detection task",
    )