
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.database.base import Base
from sqlalchemy import BigInteger, String, JSON
from sqlalchemy.orm import Mapped, mapped_column

class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    capture_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("captures.id", ondelete="SET NULL"),
        nullable=True,
    )
    data_source_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("data_sources.id", ondelete="SET NULL"),
        nullable=True,
    )

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    dataset_type: Mapped[str] = mapped_column(String(50), nullable=False)
    storage_uri: Mapped[str | None] = mapped_column(Text, nullable=True)
    dataset_metadata: Mapped[dict] = mapped_column(
        JSON, default=dict, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    project: Mapped["Project"] = relationship(back_populates="datasets")
    capture: Mapped["Capture | None"] = relationship(back_populates="datasets")
    data_source: Mapped["DataSource | None"] = relationship(back_populates="datasets")


    processing_status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False,
    )

    storage_path: Mapped[str | None] = mapped_column(
        String(1024),
        nullable=True,
    )

    content_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    file_size_bytes: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    crs: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    bounds: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    statistics: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )