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

    from pathlib import Path
    from uuid import uuid4

    from app.core.config import settings
    from app.models.dataset import Dataset
    from app.workers.change_tasks import process_ndvi_change

    def load_ndvi_dataset(dataset_id: UUID) -> Dataset:
        record = (
            db.query(Dataset)
            .filter(
                Dataset.id == dataset_id,
                Dataset.project_id == project_id,
                Dataset.processing_status == "completed",
            )
            .first()
        )

        if record is None or not record.storage_path:
            raise HTTPException(
                status_code=404,
                detail="NDVI dataset not found or not ready.",
            )

        metadata = record.dataset_metadata or {}
        if metadata.get("analysis_type") != "ndvi" and metadata.get("analysis") != "ndvi":
            raise HTTPException(
                status_code=422,
                detail="Dataset is not a completed NDVI raster.",
            )

        return record

    before = load_ndvi_dataset(payload.before_dataset_id)
    after = load_ndvi_dataset(payload.after_dataset_id)

    output_dir = Path(settings.DATASET_STORAGE_DIR) / str(project_id) / "change"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"ndvi-change-{uuid4()}.tif"

    output_dataset = Dataset(
        project_id=project_id,
        capture_id=before.capture_id,
        name=f"NDVI change ({str(before.id)[:8]} → {str(after.id)[:8]})",
        dataset_type="geotiff",
        processing_status="pending",
        storage_path=str(output_path),
        dataset_metadata={
            "analysis": "ndvi_change",
            "analysis_type": "ndvi_change",
            "before_dataset_id": str(before.id),
            "after_dataset_id": str(after.id),
            "threshold": payload.threshold,
        },
    )

    db.add(output_dataset)
    db.commit()
    db.refresh(output_dataset)

    try:
        process_ndvi_change.delay(str(output_dataset.id), payload.threshold)
    except Exception as exc:
        output_dataset.processing_status = "failed"
        output_dataset.dataset_metadata = {
            **(output_dataset.dataset_metadata or {}),
            "processing_error": "Unable to enqueue change-detection task.",
        }
        db.commit()

        raise HTTPException(
            status_code=503,
            detail="Change-detection worker is unavailable.",
        ) from exc

    return NDVIChangeResponse(
        dataset_id=output_dataset.id,
        status=output_dataset.processing_status,
        message="NDVI change detection has been queued.",
    )