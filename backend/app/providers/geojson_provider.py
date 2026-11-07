from typing import Any

from app.providers.base import BaseCaptureProvider


class GeoJSONProvider(BaseCaptureProvider):
    def capture(
        self,
        geometry: dict[str, Any],
        config: dict[str, Any],
    ) -> dict[str, Any]:
        feature = {
            "type": "Feature",
            "geometry": geometry,
            "properties": {
                "provider": "geojson",
                "capture_type": config.get("capture_type", "area_boundary"),
            },
        }

        return {
            "type": "FeatureCollection",
            "features": [feature],
        }