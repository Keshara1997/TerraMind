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

    if payload.config.get("provider", "geojson") != "geojson":
        raise HTTPException(
            status_code=422,
            detail="Only the geojson provider is currently supported.",
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