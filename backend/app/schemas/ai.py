from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field


class AIQuestionRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    start_date: date | None = None
    end_date: date | None = None
    area_id: UUID | None = None


class AIQuestionResponse(BaseModel):
    project_id: UUID
    question: str
    answer: str
    observations_used: int
    model: str