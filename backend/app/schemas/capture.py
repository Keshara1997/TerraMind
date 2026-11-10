from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from datetime import date
from pydantic import field_validator, model_validator


class CaptureCreate(BaseModel):
    area_id: UUID
    data_source_id: UUID | None = None
    config: dict[str, Any] = Field(
        default_factory=lambda: {
            "provider": "geojson",
            "capture_type": "area_boundary",
        }
    )
    start_date: date | None = None
    end_date: date | None = None
    max_cloud_cover: float = Field(default=30, ge=0, le=100)    


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



@model_validator(mode="after")
def validate_stac_options(self):
    provider = self.config.get("provider", "geojson")

    if provider == "stac":
        if self.start_date is None or self.end_date is None:
            raise ValueError(
                "start_date and end_date are required for STAC captures."
            )

        if self.start_date > self.end_date:
            raise ValueError(
                "start_date must not be later than end_date."
            )

    return self