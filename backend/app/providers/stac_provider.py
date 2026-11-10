
from typing import Any

import httpx

from app.core.config import settings


class STACProvider:
    def __init__(self) -> None:
        self.endpoint = f"{settings.STAC_API_URL.rstrip('/')}/search"

    def search(
        self,
        geometry: dict[str, Any],
        start_date: str,
        end_date: str,
        max_cloud_cover: float,
        limit: int | None = None,
    ) -> dict[str, Any]:
        payload = {
            "collections": [settings.STAC_COLLECTION],
            "intersects": geometry,
            "datetime": (
                f"{start_date}T00:00:00Z/"
                f"{end_date}T23:59:59Z"
            ),
            "limit": min(
                limit or settings.STAC_MAX_ITEMS,
                settings.STAC_MAX_ITEMS,
            ),
        }

        try:
            with httpx.Client(
                timeout=settings.STAC_REQUEST_TIMEOUT,
                follow_redirects=True,
            ) as client:
                response = client.post(
                    self.endpoint,
                    json=payload,
                    headers={"Accept": "application/geo+json"},
                )
                response.raise_for_status()
                result = response.json()

        except httpx.TimeoutException as exc:
            raise RuntimeError(
                "The satellite catalog request timed out."
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(
                f"Satellite catalog returned HTTP {exc.response.status_code}."
            ) from exc
        except httpx.RequestError as exc:
            raise RuntimeError(
                "Unable to connect to the satellite catalog."
            ) from exc
        except ValueError as exc:
            raise RuntimeError(
                "The satellite catalog returned invalid JSON."
            ) from exc

        features = result.get("features", [])

        filtered_features = []
        for item in features:
            properties = item.get("properties") or {}
            cloud_cover = properties.get("eo:cloud_cover")

            if cloud_cover is None or cloud_cover <= max_cloud_cover:
                filtered_features.append(item)

        return {
            "type": "FeatureCollection",
            "features": filtered_features,
            "number_returned": len(filtered_features),
            "number_before_cloud_filter": len(features),
            "collection": settings.STAC_COLLECTION,
            "provider": "earth-search",
        }
