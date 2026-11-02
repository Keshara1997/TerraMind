
import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from app.services.project_service import ProjectService


router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("/", response_model=list[ProjectRead])
def list_projects(db: Session = Depends(get_db)):
    service = ProjectService(db)
    return service.list_projects()


@router.post(
    "/",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    data: ProjectCreate,
    db: Session = Depends(get_db),
):
    service = ProjectService(db)
    return service.create_project(data)


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    service = ProjectService(db)
    project = service.get_project(project_id)

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return project


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: uuid.UUID,
    data: ProjectUpdate,
    db: Session = Depends(get_db),
):
    service = ProjectService(db)
    project = service.get_project(project_id)

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if not data.model_dump(exclude_unset=True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No update fields provided",
        )

    return service.update_project(project, data)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_project(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    service = ProjectService(db)
    project = service.get_project(project_id)

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    service.delete_project(project)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
