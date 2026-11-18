from uuid import UUID

from pydantic import BaseModel, Field


class NDVIChangeRequest(BaseModel):
    before_dataset_id: UUID
    after_dataset_id: UUID
    threshold: float = Field(default=0.1, gt=0, le=1)


class NDVIChangeResponse(BaseModel):
    dataset_id: UUID
    status: str
    message: str