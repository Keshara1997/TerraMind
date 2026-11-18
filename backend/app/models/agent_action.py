import uuid

from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.base import Base


class AgentAction(Base):
    __tablename__ = "agent_actions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id"),
        nullable=False,
        index=True,
    )

    action_type = Column(
        String(100),
        nullable=False,
    )

    parameters = Column(
        JSON,
        nullable=False,
    )

    status = Column(
        String(30),
        nullable=False,
        default="pending_approval",
        index=True,
    )

    celery_task_id = Column(
        String(255),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    approved_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )