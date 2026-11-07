from datetime import datetime, timezone
from uuid import UUID

from geoalchemy2.shape import to_shape

from app.database.session import SessionLocal
from app.models.area import Area
from app.models.capture import Capture
from app.models.dataset import Dataset
from app.providers.registry import get_capture_provider
from app.workers.celery_app import celery_app


@celery_app.task(
    name="captures.process",
    bind=True,
    max_retries=2,
    default_retry_delay=10,
)
def process_capture(self, capture_id: str):
    db = SessionLocal()

    try:
        capture = (
            db.query(Capture)
            .filter(Capture.id == UUID(capture_id))
            .first()
        )

        if capture is None:
            return {"status": "not_found", "capture_id": capture_id}

        # Avoid processing an already completed capture again.
        if capture.status == "completed":
            return {"status": "completed", "capture_id": capture_id}

        capture.status = "running"
        capture.started_at = datetime.now(timezone.utc)
        capture.error_message = None
        db.commit()

        area = (
            db.query(Area)
            .filter(
                Area.id == capture.area_id,
                Area.project_id == capture.project_id,
            )
            .first()
        )

        if area is None:
            raise ValueError("The selected project area could not be found.")

        geometry = to_shape(area.geometry)
        geojson_geometry = geometry.__geo_interface__

        config = capture.config or {}
        provider_name = config.get("provider", "geojson")

        provider = get_capture_provider(provider_name)
        output = provider.capture(geojson_geometry, config)

        dataset = Dataset(
            project_id=capture.project_id,
            capture_id=capture.id,
            name=f"{area.name} capture",
            format="geojson",
            metadata={
                "provider": provider_name,
                "feature_count": len(output["features"]),
                "capture_type": config.get(
                    "capture_type",
                    "area_boundary",
                ),
                "output": output,
            },
        )

        db.add(dataset)

        capture.status = "completed"
        capture.completed_at = datetime.now(timezone.utc)

        db.commit()

        return {
            "status": "completed",
            "capture_id": capture_id,
            "dataset_id": str(dataset.id),
        }

    except Exception as exc:
        db.rollback()

        capture = (
            db.query(Capture)
            .filter(Capture.id == UUID(capture_id))
            .first()
        )

        if capture is not None:
            capture.status = "failed"
            capture.error_message = str(exc)[:2000]
            capture.completed_at = datetime.now(timezone.utc)
            db.commit()

        raise

    finally:
        db.close()

         