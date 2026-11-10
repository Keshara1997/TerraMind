from datetime import datetime, timezone
from uuid import UUID

from geoalchemy2.shape import to_shape

from app.database.session import SessionLocal
from app.models.area import Area
from app.models.capture import Capture
from app.models.dataset import Dataset
from app.providers.registry import get_capture_provider
from app.workers.celery_app import celery_app
from app.providers.stac_provider import STACProvider

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

        if provider_name == "geojson":
            provider = get_capture_provider("geojson")
            output = provider.capture(geojson_geometry, config)

        elif provider_name == "stac":
            provider = STACProvider()

            output = provider.search(
                geometry=geojson_geometry,
                start_date=config["start_date"],
                end_date=config["end_date"],
                max_cloud_cover=float(
                    config.get("max_cloud_cover", 30)
                ),
            )

        else:
            raise ValueError(
                f"Unsupported capture provider: {provider_name}"
            )

        is_stac = provider_name == "stac"

        dataset = Dataset(
            project_id=capture.project_id,
            capture_id=capture.id,
            name=(
                f"{area.name} - Sentinel-2 search"
                if is_stac
                else f"{area.name} capture"
            ),
            format="stac-json" if is_stac else "geojson",
            metadata={
                "provider": provider_name,
                "feature_count": len(output["features"]),
                "collection": output.get("collection"),
                "number_returned": output.get("number_returned"),
                "number_before_cloud_filter": output.get(
                "number_before_cloud_filter"
                ),
                "search_parameters": {
                    "start_date": config.get("start_date"),
                    "end_date": config.get("end_date"),
                    "max_cloud_cover": config.get("max_cloud_cover"),
                },
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

         