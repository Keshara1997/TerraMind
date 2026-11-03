
import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.area import (
    AreaCreate,
    AreaRead,
    AreaUpdate,
    SpatialQuery,
)
from app.services.area_service import AreaService
from app.services.project_service import ProjectService


router = APIRouter(
    prefix="/projects/{project_id}/areas",
    tags=["Geospatial Areas"],
)


def verify_project_access(
    project_id: uuid.UUID,
    db: Session,
    current_user: User,
):
    project = ProjectService(db).get_project(
        project_id,
        current_user.id,
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return project


@router.post(
    "/",
    response_model=AreaRead,
    status_code=status.HTTP_201_CREATED,
)
def create_area(
    project_id: uuid.UUID,
    data: AreaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    verify_project_access(project_id, db, current_user)

    return AreaService(db).create_area(project_id, data)


@router.get("/", response_model=list[AreaRead])
def list_areas(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    verify_project_access(project_id, db, current_user)

    return AreaService(db).list_areas(project_id)


@router.post(
    "/intersections",
    response_model=list[AreaRead],
)
def find_intersections(
    project_id: uuid.UUID,
    data: SpatialQuery,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    verify_project_access(project_id, db, current_user)

    return AreaService(db).find_intersections(
        project_id,
        data.geometry,
    )


@router.get("/{area_id}", response_model=AreaRead)
def get_area(
    project_id: uuid.UUID,
    area_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    verify_project_access(project_id, db, current_user)

    area = AreaService(db).get_area(project_id, area_id)

    if area is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Area not found",
        )

    return area


@router.patch("/{area_id}", response_model=AreaRead)
def update_area(
    project_id: uuid.UUID,
    area_id: uuid.UUID,
    data: AreaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    verify_project_access(project_id, db, current_user)

    if not data.model_dump(exclude_unset=True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No update fields provided",
        )

    area = AreaService(db).update_area(
        project_id,
        area_id,
        data,
    )

    if area is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Area not found",
        )

    return area


@router.delete(
    "/{area_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_area(
    project_id: uuid.UUID,
    area_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    verify_project_access(project_id, db, current_user)

    deleted = AreaService(db).delete_area(
        project_id,
        area_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Area not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
