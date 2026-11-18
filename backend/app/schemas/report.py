from datetime import date
from uuid import UUID

from pydantic import BaseModel


class EnvironmentalReportRequest(BaseModel):
    start_date: date
    end_date: date
    area_id: UUID | None = None


class EnvironmentalReportResponse(BaseModel):
    project_id: UUID
    title: str
    period_start: date
    period_end: date
    observations_used: int
    report: str