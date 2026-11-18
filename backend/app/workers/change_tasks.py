from pathlib import Path
from uuid import UUID

import rasterio

from app.database.session import SessionLocal
from app.geospatial.change_detector import detect_ndvi_change
from app.models.dataset import Dataset
from app.workers.celery_app import celery_app


@celery_app.task(
    name="change.process_ndvi_change",
    bind=True,
    max_retries=1,
    default_retry_delay=30,
)
def process_ndvi_change(self, dataset_id: str, threshold: float):
    db = SessionLocal()

    try:
        dataset = (
            db.query(Dataset)
            .filter(Dataset.id == UUID(dataset_id))
            .first()
        )

        if dataset is None:
            return {"status": "not_found", "dataset_id": dataset_id}

        metadata = dataset.dataset_metadata or {}
        before_id = metadata.get("before_dataset_id")
        after_id = metadata.get("after_dataset_id")

        if not before_id or not after_id:
            raise ValueError("Change-detection metadata is incomplete.")

        before = (
            db.query(Dataset)
            .filter(
                Dataset.id == UUID(before_id),
                Dataset.project_id == dataset.project_id,
            )
            .first()
        )
        after = (
            db.query(Dataset)
            .filter(
                Dataset.id == UUID(after_id),
                Dataset.project_id == dataset.project_id,
            )
            .first()
        )

        if before is None or after is None:
            raise ValueError("Before/after NDVI datasets were not found.")

        if not before.storage_path or not after.storage_path:
            raise ValueError("Both NDVI datasets must have storage_path set.")

        dataset.processing_status = "running"
        db.commit()

        output_path = Path(dataset.storage_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        summary = detect_ndvi_change(
            before_path=before.storage_path,
            after_path=after.storage_path,
            output_path=str(output_path),
            threshold=threshold,
        )

        with rasterio.open(output_path) as opened:
            bounds = [
                opened.bounds.left,
                opened.bounds.bottom,
                opened.bounds.right,
                opened.bounds.top,
            ]
            crs = str(opened.crs) if opened.crs else None

        dataset.processing_status = "completed"
        dataset.content_type = "image/tiff"
        dataset.file_size_bytes = output_path.stat().st_size
        dataset.crs = crs
        dataset.bounds = {
            "west": bounds[0],
            "south": bounds[1],
            "east": bounds[2],
            "north": bounds[3],
        }
        dataset.statistics = summary
        dataset.dataset_metadata = {
            **metadata,
            "change_summary": summary,
        }
        db.commit()

        return {
            "status": "completed",
            "dataset_id": dataset_id,
            "summary": summary,
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
            dataset.dataset_metadata = {
                **(dataset.dataset_metadata or {}),
                "processing_error": str(exc)[:2000],
            }
            db.commit()

        raise

    finally:
        db.close()