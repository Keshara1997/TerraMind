
import uuid
from typing import Any

from geoalchemy2 import Geography
from geoalchemy2.shape import from_shape
from shapely.geometry import MultiPolygon
from sqlalchemy import cast, func, select
from sqlalchemy.orm import Session

from app.models.area import Area


class AreaRepository:
    def __init__(self, db: Session):
        self.db = db

    def _measurements(self):
        geography = cast(
            Area.geometry,
            Geography(srid=4326),
        )

        return (
            func.ST_Area(geography).label("area_sq_m"),
            func.ST_Perimeter(geography).label("perimeter_m"),
        )

    def get_all(self, project_id: uuid.UUID):
        area_sq_m, perimeter_m = self._measurements()

        statement = (
            select(Area, area_sq_m, perimeter_m)
            .where(Area.project_id == project_id)
            .order_by(Area.created_at.desc())
        )

        return self.db.execute(statement).all()

    def get_by_id(
        self,
        project_id: uuid.UUID,
        area_id: uuid.UUID,
    ):
        area_sq_m, perimeter_m = self._measurements()

        statement = (
            select(Area, area_sq_m, perimeter_m)
            .where(
                Area.project_id == project_id,
                Area.id == area_id,
            )
        )

        return self.db.execute(statement).first()

    def create(
        self,
        project_id: uuid.UUID,
        name: str,
        description: str | None,
        geometry: MultiPolygon,
    ) -> Area:
        area = Area(
            project_id=project_id,
            name=name,
            description=description,
            geometry=from_shape(geometry, srid=4326),
        )

        self.db.add(area)
        self.db.commit()
        self.db.refresh(area)

        return area

    def update(self, area: Area, changes: dict[str, Any]) -> Area:
        for field, value in changes.items():
            if field == "geometry":
                value = from_shape(value, srid=4326)

            setattr(area, field, value)

        self.db.commit()
        self.db.refresh(area)

        return area

    def delete(self, area: Area) -> None:
        self.db.delete(area)
        self.db.commit()

    def find_intersections(
        self,
        project_id: uuid.UUID,
        geometry: MultiPolygon,
    ):
        query_geometry = from_shape(geometry, srid=4326)

        area_sq_m, perimeter_m = self._measurements()

        statement = (
            select(Area, area_sq_m, perimeter_m)
            .where(
                Area.project_id == project_id,
                func.ST_Intersects(
                    Area.geometry,
                    query_geometry,
                ),
            )
            .order_by(Area.created_at.desc())
        )

        return self.db.execute(statement).all()
