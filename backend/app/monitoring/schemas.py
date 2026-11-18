from datetime import datetime
from pydantic import BaseModel


class EnvironmentalAlertRead(BaseModel):
    id: str
    project_id: str
    alert_type: str
    severity: str
    message: str
    observed_value: float | None = None
    threshold_value: float | None = None
    created_at: datetime
    is_read: bool