
import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    JSON,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.database.base import Base


class Capture(Base):
    __tablename__ = "captures"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    area_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("areas.id", ondelete="SET NULL"),
        nullable=True,
    )

    capture_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(
        String(30), default="pending", nullable=False
    )
    configuration: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    project: Mapped["Project"] = relationship(back_populates="captures")
    area: Mapped["Area | None"] = relationship(back_populates="captures")
    datasets: Mapped[list["Dataset"]] = relationship(back_populates="capture")
