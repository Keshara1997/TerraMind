from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CaptureCreate(BaseModel):
    area_id: UUID
    data_source_id: UUID | None = None
    config: dict[str, Any] = Field(
        default_factory=lambda: {
            "provider": "geojson",
            "capture_type": "area_boundary",
        }
    )


class CaptureRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    area_id: UUID
    data_source_id: UUID | None = None
    created_by: UUID
    status: str
    config: dict[str, Any]
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime


class DatasetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    capture_id: UUID
    name: str
    format: str
    metadata: dict[str, Any]
    created_at: datetime