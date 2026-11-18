from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from app.services.time_series_service import get_ndvi_time_series


def build_project_context(
    db: Session,
    project_id: UUID,
    start_date: date | None = None,
    end_date: date | None = None,
    area_id: UUID | None = None,
):
    points = get_ndvi_time_series(
        db=db,
        project_id=project_id,
        area_id=area_id,
        start_date=start_date,
        end_date=end_date,
    )

    observations = []

    for point in points:
        observations.append({
            "dataset_id": str(point["dataset_id"]),
            "capture_id": str(point["capture_id"]),
            "acquisition_date": point["acquisition_date"].isoformat(),
            "mean_ndvi": point["mean"],
            "median_ndvi": point["median"],
            "minimum_ndvi": point["minimum"],
            "maximum_ndvi": point["maximum"],
            "valid_pixels": point["valid_pixels"],
        })

    return {
        "project_id": str(project_id),
        "area_id": str(area_id) if area_id else None,
        "period": {
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
        },
        "total_observations": len(observations),
        "ndvi_observations": observations,
    }