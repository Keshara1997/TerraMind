from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.database.session import get_db
from app.models.area import Area
from app.models.capture import Capture
from app.models.data_source import DataSource
from app.models.dataset import Dataset
from app.models.project import Project
from app.models.user import User
from app.schemas.capture import (
    CaptureCreate,
    CaptureRead,
    DatasetRead,
)
from app.workers.capture_tasks import process_capture

from app.workers.raster_tasks import process_ndvi


from app.core.config import settings

router = APIRouter(
    prefix="/projects/{project_id}/captures",
    tags=["Geospatial Captures"],
)


def check_project_access(
    db: Session,
    project_id: UUID,
    user_id: UUID,
) -> Project:
    project = (
        db.query(Project)
        .filter(
            Project.id == project_id,
            Project.owner_id == user_id,
        )
        .first()
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )

    return project


@router.post(
    "/",
    response_model=CaptureRead,
    status_code=status.HTTP_202_ACCEPTED,
)
def create_capture(
    project_id: UUID,
    payload: CaptureCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    check_project_access(db, project_id, current_user.id)

    area = (
        db.query(Area)
        .filter(
            Area.id == payload.area_id,
            Area.project_id == project_id,
        )
        .first()
    )

    if area is None:
        raise HTTPException(
            status_code=404,
            detail="Area not found in this project.",
        )

    provider_name = payload.config.get("provider", "geojson")

    if provider_name not in {"geojson", "stac"}:
        raise HTTPException(
        status_code=422,
        detail="Unsupported capture provider.",
    )

    if payload.data_source_id is not None:
        data_source = (
            db.query(DataSource)
            .filter(
                DataSource.id == payload.data_source_id,
                DataSource.is_active.is_(True),
            )
            .first()
        )

        if data_source is None:
            raise HTTPException(
                status_code=404,
                detail="Active data source not found.",
            )

        capture_config = dict(payload.config)

    if provider_name == "stac":         
        capture_config.update({
        "start_date": payload.start_date.isoformat(),
        "end_date": payload.end_date.isoformat(),
        "max_cloud_cover": payload.max_cloud_cover,
    })

    capture = Capture(
        project_id=project_id,
        area_id=payload.area_id,
        data_source_id=payload.data_source_id,
        created_by=current_user.id,
        status="pending",
        config=payload.config,
    )

    db.add(capture)
    db.commit()
    db.refresh(capture)

    try:
        process_capture.delay(str(capture.id))
    except Exception as exc:
        capture.status = "failed"
        capture.error_message = (
            "Unable to enqueue capture task. Please retry."
        )
        db.commit()

        raise HTTPException(
            status_code=503,
            detail="Capture worker is currently unavailable.",
        ) from exc

    return capture


@router.get("/", response_model=list[CaptureRead])
def list_captures(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    check_project_access(db, project_id, current_user.id)

    return (
        db.query(Capture)
        .filter(Capture.project_id == project_id)
        .order_by(Capture.created_at.desc())
        .all()
    )


@router.get("/{capture_id}", response_model=CaptureRead)
def get_capture(
    project_id: UUID,
    capture_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    check_project_access(db, project_id, current_user.id)

    capture = (
        db.query(Capture)
        .filter(
            Capture.id == capture_id,
            Capture.project_id == project_id,
        )
        .first()
    )

    if capture is None:
        raise HTTPException(status_code=404, detail="Capture not found.")

    return capture


@router.get(
    "/{capture_id}/datasets",
    response_model=list[DatasetRead],
)
def list_capture_datasets(
    project_id: UUID,
    capture_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    check_project_access(db, project_id, current_user.id)

    capture = (
        db.query(Capture)
        .filter(
            Capture.id == capture_id,
            Capture.project_id == project_id,
        )
        .first()
    )

    if capture is None:
        raise HTTPException(status_code=404, detail="Capture not found.")

    return (
        db.query(Dataset)
        .filter(
            Dataset.capture_id == capture_id,
            Dataset.project_id == project_id,
        )
        .order_by(Dataset.created_at.desc())
        .all()
    )



from pydantic import BaseModel, Field


from pydantic import BaseModel, Field


class NDVIRequest(BaseModel):
    source_dataset_id: UUID
    item_id: str = Field(min_length=1, max_length=512)


@router.post(
    "/{capture_id}/ndvi",
    status_code=status.HTTP_202_ACCEPTED,
)
def start_ndvi_processing(
    project_id: UUID,
    capture_id: UUID,
    payload: NDVIRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    check_project_access(db, project_id, current_user.id)

    capture = (
        db.query(Capture)
        .filter(
            Capture.id == capture_id,
            Capture.project_id == project_id,
        )
        .first()
    )

    if capture is None:
        raise HTTPException(status_code=404, detail="Capture not found.")

    source_dataset = (
        db.query(Dataset)
        .filter(
            Dataset.id == payload.source_dataset_id,
            Dataset.capture_id == capture_id,
            Dataset.project_id == project_id,
            Dataset.format == "stac-json",
        )
        .first()
    )

    if source_dataset is None:
        raise HTTPException(
            status_code=404,
            detail="STAC search dataset not found.",
        )

    features = (
        source_dataset.metadata_json or {}
    ).get("output", {}).get("features", [])

    selected_item = next(
        (
            feature
            for feature in features
            if feature.get("id") == payload.item_id
        ),
        None,
    )

    if selected_item is None:
        raise HTTPException(
            status_code=404,
            detail="Selected satellite scene not found.",
        )

    assets = selected_item.get("assets", {})

    if not assets.get("red") or not assets.get("nir"):
        raise HTTPException(
            status_code=422,
            detail="Selected scene does not have the required red and NIR bands.",
        )

    output_dataset = Dataset(
        project_id=project_id,
        capture_id=capture_id,
        name=f"NDVI - {payload.item_id}",
        format="geotiff",
        processing_status="pending",
        metadata_json={
            "analysis": "ndvi",
            "source_dataset_id": str(source_dataset.id),
            "source_item_id": payload.item_id,
        },
    )

    db.add(output_dataset)
    db.commit()
    db.refresh(output_dataset)

    try:
        process_ndvi.delay(str(output_dataset.id))
    except Exception as exc:
        output_dataset.processing_status = "failed"
        output_dataset.metadata_json = {
            **(output_dataset.metadata_json or {}),
            "processing_error": "Unable to enqueue raster processing.",
        }
        db.commit()

        raise HTTPException(
            status_code=503,
            detail="Raster processing worker is unavailable.",
        ) from exc

    return {
        "dataset_id": str(output_dataset.id),
        "status": output_dataset.processing_status,
        "message": "NDVI processing has been queued.",
    }



from pathlib import Path

from fastapi.responses import FileResponse



@router.get("/{capture_id}/datasets/{dataset_id}/download")
def download_dataset(
    project_id: UUID,
    capture_id: UUID,
    dataset_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    check_project_access(db, project_id, current_user.id)

    dataset = (
        db.query(Dataset)
        .filter(
            Dataset.id == dataset_id,
            Dataset.capture_id == capture_id,
            Dataset.project_id == project_id,
        )
        .first()
    )

    if dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    if dataset.processing_status != "completed":
        raise HTTPException(
            status_code=409,
            detail="Dataset processing is not completed.",
        )

    if not dataset.storage_path:
        raise HTTPException(
            status_code=404,
            detail="Dataset file is not available.",
        )

    storage_root = Path(settings.DATASET_STORAGE_DIR).resolve()
    file_path = Path(dataset.storage_path).resolve()

    if not file_path.is_relative_to(storage_root):
        raise HTTPException(
            status_code=403,
            detail="Invalid dataset storage location.",
        )

    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Dataset file does not exist.",
        )

    return FileResponse(
        path=file_path,
        media_type=dataset.content_type or "application/octet-stream",
        filename=f"{dataset.id}.tif",
    )
