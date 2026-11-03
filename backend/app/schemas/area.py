
import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AreaCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    description: str | None = Field(default=None, max_length=5000)
    geometry: dict[str, Any]

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()

        if len(value) < 2:
            raise ValueError("Area name must contain at least 2 characters")

        return value


class AreaUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    description: str | None = Field(default=None, max_length=5000)
    geometry: dict[str, Any] | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            raise ValueError("Area name cannot be null")

        value = value.strip()

        if len(value) < 2:
            raise ValueError("Area name must contain at least 2 characters")

        return value


class AreaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    name: str
    description: str | None
    geometry: dict[str, Any]
    area_sq_m: float
    area_sq_km: float
    perimeter_m: float
    created_at: datetime


class SpatialQuery(BaseModel):
    geometry: dict[str, Any]
