from datetime import date, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.dataset import Dataset
from app.models.capture import Capture


def get_ndvi_time_series(
    db: Session,
    project_id: UUID,
    area_id: UUID | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
):
    statement = (
        select(Dataset, Capture)
        .join(Capture, Dataset.capture_id == Capture.id)
        .where(
            Capture.project_id == project_id,
            Dataset.format == "geotiff",
            Dataset.processing_status == "completed",
        )
        .order_by(Capture.created_at.asc())
    )

    if area_id is not None:
        statement = statement.where(Capture.area_id == area_id)

    records = db.execute(statement).all()
    points = []

    for dataset, capture in records:
        metadata = dataset.metadata_json or {}

        if metadata.get("analysis_type") != "ndvi":
            continue

        acquisition_datetime = metadata.get("acquisition_datetime")

        if not acquisition_datetime:
            continue

        if isinstance(acquisition_datetime, str):
            acquisition_datetime = datetime.fromisoformat(
                acquisition_datetime.replace("Z", "+00:00")
            )

        acquisition_date = acquisition_datetime.date()

        if start_date and acquisition_date < start_date:
            continue

        if end_date and acquisition_date > end_date:
            continue

        stats = metadata.get("statistics", {})

        points.append({
            "dataset_id": dataset.id,
            "capture_id": capture.id,
            "acquisition_date": acquisition_date,
            "mean": stats.get("mean"),
            "minimum": stats.get("min"),
            "maximum": stats.get("max"),
            "median": stats.get("median"),
            "valid_pixels": stats.get("valid_pixels"),
        })

    points.sort(key=lambda point: point["acquisition_date"])

    return points