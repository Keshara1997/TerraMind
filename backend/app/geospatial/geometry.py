
from typing import Any

from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import MultiPolygon, Polygon, shape, mapping
from shapely.geometry.base import BaseGeometry


def validate_geojson(geojson: dict[str, Any]) -> MultiPolygon:
    if not isinstance(geojson, dict):
        raise ValueError("Geometry must be a GeoJSON object")

    geometry_type = geojson.get("type")

    if geometry_type not in ("Polygon", "MultiPolygon"):
        raise ValueError("Only Polygon and MultiPolygon are supported")

    try:
        geometry = shape(geojson)
    except Exception as exc:
        raise ValueError("Invalid GeoJSON geometry") from exc

    if geometry.is_empty:
        raise ValueError("Geometry cannot be empty")

    if not isinstance(geometry, (Polygon, MultiPolygon)):
        raise ValueError("Invalid polygon geometry")

    if not geometry.is_valid:
        raise ValueError("Polygon geometry is invalid or self-intersecting")

    min_x, min_y, max_x, max_y = geometry.bounds

    if not (
        -180 <= min_x <= 180
        and -180 <= max_x <= 180
        and -90 <= min_y <= 90
        and -90 <= max_y <= 90
    ):
        raise ValueError(
            "Coordinates must be longitude/latitude in EPSG:4326"
        )

    if isinstance(geometry, Polygon):
        geometry = MultiPolygon([geometry])

    return geometry


def geometry_to_postgis(geometry: MultiPolygon):
    return from_shape(geometry, srid=4326)


def postgis_to_geojson(geometry_element) -> dict[str, Any]:
    geometry = to_shape(geometry_element)
    return mapping(geometry)


def geometry_to_geojson(geometry: BaseGeometry) -> dict[str, Any]:
    return mapping(geometry)
