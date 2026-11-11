
from pathlib import Path
from uuid import UUID

from app.core.config import settings
from app.database.session import SessionLocal
from app.geospatial.raster_processor import calculate_ndvi
from app.models.area import Area
from app.models.capture import Capture
from app.models.dataset import Dataset
from app.workers.celery_app import celery_app

from geoalchemy2.shape import to_shape


@celery_app.task(
    name="raster.process_ndvi",
    bind=True,
    max_retries=1,
    default_retry_delay=30,
)
def process_ndvi(self, dataset_id: str):
    db = SessionLocal()
    output_path = None

    try:
        dataset = (
            db.query(Dataset)
            .filter(Dataset.id == UUID(dataset_id))
            .first()
        )

        if dataset is None:
            return {
                "status": "not_found",
                "dataset_id": dataset_id,
            }

        if dataset.processing_status == "completed":
            return {
                "status": "completed",
                "dataset_id": dataset_id,
            }

        dataset.processing_status = "running"
        db.commit()

        source_dataset_id = dataset.metadata_json["source_dataset_id"]
        item_id = dataset.metadata_json["source_item_id"]

        source_dataset = (
            db.query(Dataset)
            .filter(
                Dataset.id == UUID(source_dataset_id),
                Dataset.project_id == dataset.project_id,
                Dataset.capture_id == dataset.capture_id,
            )
            .first()
        )

        if source_dataset is None:
            raise ValueError("Source STAC dataset not found.")

        capture = (
            db.query(Capture)
            .filter(
                Capture.id == dataset.capture_id,
                Capture.project_id == dataset.project_id,
            )
            .first()
        )

        if capture is None:
            raise ValueError("Source capture not found.")

        area = (
            db.query(Area)
            .filter(
                Area.id == capture.area_id,
                Area.project_id == capture.project_id,
            )
            .first()
        )

        if area is None:
            raise ValueError("Capture area not found.")

        # Read the STAC FeatureCollection.
        stac_output = source_dataset.metadata_json["output"]

        item = next(
            (
                feature
                for feature in stac_output.get("features", [])
                if feature.get("id") == item_id
            ),
            None,
        )

        if item is None:
            raise ValueError("Selected STAC item was not found.")

        assets = item.get("assets", {})

        red_asset = assets.get("red")
        nir_asset = assets.get("nir")

        if not red_asset or not nir_asset:
            raise ValueError(
                "The selected STAC item does not contain both "
                "red and NIR assets."
            )

        red_url = red_asset.get("href")
        nir_url = nir_asset.get("href")

        if not red_url or not nir_url:
            raise ValueError("Satellite raster asset URL is missing.")

        result = calculate_ndvi(
            red_url=red_url,
            nir_url=nir_url,
            geometry=to_shape(area.geometry).__geo_interface__,
        )

        output_path = Path(result["path"])

        dataset.storage_path = result["path"]
        dataset.content_type = "image/tiff"
        dataset.file_size_bytes = result["file_size_bytes"]
        dataset.crs = result["crs"]
        dataset.bounds = result["bounds"]
        dataset.statistics = result["statistics"]
        dataset.processing_status = "completed"

        dataset.metadata_json = {
            **(dataset.metadata_json or {}),
            "analysis": "ndvi",
            "formula": "(NIR - RED) / (NIR + RED)",
            "source_item_id": item_id,
            "red_asset": "red",
            "nir_asset": "nir",
            "statistics": result["statistics"],
        }

        db.commit()

        return {
            "status": "completed",
            "dataset_id": dataset_id,
            "file_size_bytes": result["file_size_bytes"],
        }

    except Exception as exc:
        db.rollback()

        dataset = (
            db.query(Dataset)
            .filter(Dataset.id == UUID(dataset_id))
            .first()
        )

        if dataset is not None:
            dataset.processing_status = "failed"
            dataset.metadata_json = {
                **(dataset.metadata_json or {}),
                "processing_error": str(exc)[:2000],
            }
            db.commit()

        if output_path and output_path.exists():
            output_path.unlink(missing_ok=True)

        raise

    finally:
        db.close()
