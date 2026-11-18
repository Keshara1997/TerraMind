from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class NDVITimeSeriesPoint(BaseModel):
    dataset_id: UUID
    capture_id: UUID
    acquisition_date: date

    mean: float | None = None
    minimum: float | None = None
    maximum: float | None = None
    median: float | None = None
    valid_pixels: int | None = None


class NDVITimeSeriesResponse(BaseModel):
    project_id: UUID
    area_id: UUID | None = None
    start_date: date | None = None
    end_date: date | None = None
    total_observations: int
    points: list[NDVITimeSeriesPoint]

    model_config = ConfigDict(from_attributes=True)