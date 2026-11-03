
import uuid
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.geospatial.geometry import (
    postgis_to_geojson,
    validate_geojson,
)
from app.models.area import Area
from app.repositories.area_repository import AreaRepository
from app.schemas.area import AreaCreate, AreaUpdate


class AreaService:
    def __init__(self, db: Session):
        self.repository = AreaRepository(db)

    @staticmethod
    def serialize(row) -> dict[str, Any]:
        area, area_sq_m, perimeter_m = row

        return {
            "id": area.id,
            "project_id": area.project_id,
            "name": area.name,
            "description": area.description,
            "geometry": postgis_to_geojson(area.geometry),
            "area_sq_m": float(area_sq_m),
            "area_sq_km": float(area_sq_m) / 1_000_000,
            "perimeter_m": float(perimeter_m),
            "created_at": area.created_at,
        }

    @staticmethod
    def validate_geometry(geojson: dict) :
        try:
            return validate_geojson(geojson)
        except (ValueError, TypeError) as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            )

    def list_areas(self, project_id: uuid.UUID):
        rows = self.repository.get_all(project_id)
        return [self.serialize(row) for row in rows]

    def get_area(
        self,
        project_id: uuid.UUID,
        area_id: uuid.UUID,
    ):
        row = self.repository.get_by_id(project_id, area_id)

        if row is None:
            return None

        return self.serialize(row)

    def create_area(
        self,
        project_id: uuid.UUID,
        data: AreaCreate,
    ):
        geometry = self.validate_geometry(data.geometry)

        area = self.repository.create(
            project_id=project_id,
            name=data.name,
            description=data.description,
            geometry=geometry,
        )

        return self.get_area(project_id, area.id)

    def update_area(
        self,
        project_id: uuid.UUID,
        area_id: uuid.UUID,
        data: AreaUpdate,
    ):
        row = self.repository.get_by_id(project_id, area_id)

        if row is None:
            return None

        area: Area = row[0]
        changes = data.model_dump(exclude_unset=True)

        if "geometry" in changes:
            if changes["geometry"] is None:
                raise HTTPException(
                    status_code=422,
                    detail="Geometry cannot be null",
                )

            changes["geometry"] = self.validate_geometry(
                changes["geometry"]
            )

        self.repository.update(area, changes)

        return self.get_area(project_id, area_id)

    def delete_area(
        self,
        project_id: uuid.UUID,
        area_id: uuid.UUID,
    ) -> bool:
        row = self.repository.get_by_id(project_id, area_id)

        if row is None:
            return False

        self.repository.delete(row[0])
        return True

    def find_intersections(
        self,
        project_id: uuid.UUID,
        geometry_geojson: dict,
    ):
        geometry = self.validate_geometry(geometry_geojson)

        rows = self.repository.find_intersections(
            project_id,
            geometry,
        )

        return [self.serialize(row) for row in rows]
