from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator


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


class CaptureRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    project_id: UUID
    area_id: UUID | None = None
    data_source_id: UUID | None = None
    created_by: UUID | None = None
    status: str
    config: dict[str, Any] = Field(
        validation_alias=AliasChoices("config", "configuration"),
        serialization_alias="config",
    )
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = Field(
        default=None,
        validation_alias=AliasChoices("completed_at", "finished_at"),
        serialization_alias="completed_at",
    )
    created_at: datetime


class DatasetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    project_id: UUID
    capture_id: UUID | None = None
    name: str
    format: str = Field(
        validation_alias=AliasChoices("format", "dataset_type"),
        serialization_alias="format",
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        validation_alias=AliasChoices("metadata_json", "metadata", "dataset_metadata"),
        serialization_alias="metadata",
    )

    processing_status: str = "pending"
    storage_path: str | None = None
    content_type: str | None = None
    file_size_bytes: int | None = None
    crs: str | None = None
    bounds: dict[str, Any] | None = None
    statistics: dict[str, Any] | None = None

    created_at: datetime