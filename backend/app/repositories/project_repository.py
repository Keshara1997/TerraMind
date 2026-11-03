
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project


class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, owner_id: uuid.UUID) -> list[Project]:
        statement = (
            select(Project)
            .where(Project.owner_id == owner_id)
            .order_by(Project.created_at.desc())
        )
        return list(self.db.scalars(statement).all())

    def get_by_id(
        self,
        project_id: uuid.UUID,
        owner_id: uuid.UUID,
    ) -> Project | None:
        statement = select(Project).where(
            Project.id == project_id,
            Project.owner_id == owner_id,
        )
        return self.db.scalar(statement)

    def create(
        self,
        owner_id: uuid.UUID,
        name: str,
        description: str | None,
    ) -> Project:
        project = Project(
            owner_id=owner_id,
            name=name,
            description=description,
            status="active",
        )

        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)

        return project

    def update(self, project: Project, changes: dict) -> Project:
        for field, value in changes.items():
            setattr(project, field, value)

        self.db.commit()
        self.db.refresh(project)

        return project

    def delete(self, project: Project) -> None:
        self.db.delete(project)
        self.db.commit()
