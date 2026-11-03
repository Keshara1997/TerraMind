
import uuid

from sqlalchemy.orm import Session

from app.models.project import Project
from app.repositories.project_repository import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    def __init__(self, db: Session):
        self.repository = ProjectRepository(db)

    def list_projects(self, owner_id: uuid.UUID) -> list[Project]:
        return self.repository.get_all(owner_id)

    def get_project(
        self,
        project_id: uuid.UUID,
        owner_id: uuid.UUID,
    ) -> Project | None:
        return self.repository.get_by_id(project_id, owner_id)

    def create_project(
        self,
        owner_id: uuid.UUID,
        data: ProjectCreate,
    ) -> Project:
        return self.repository.create(
            owner_id=owner_id,
            name=data.name,
            description=data.description,
        )

    def update_project(
        self,
        project: Project,
        data: ProjectUpdate,
    ) -> Project:
        changes = data.model_dump(exclude_unset=True)
        return self.repository.update(project, changes)

    def delete_project(self, project: Project) -> None:
        self.repository.delete(project)
