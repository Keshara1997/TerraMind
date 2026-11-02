
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.database.base import Base


class DataSource(Base):
    __tablename__ = "data_sources"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    provider: Mapped[str] = mapped_column(String(100), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    base_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_metadata: Mapped[dict] = mapped_column(
        JSON, default=dict, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    datasets: Mapped[list["Dataset"]] = relationship(back_populates="data_source")
