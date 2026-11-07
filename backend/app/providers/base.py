from abc import ABC, abstractmethod
from typing import Any


class BaseCaptureProvider(ABC):
    @abstractmethod
    def capture(
        self,
        geometry: dict[str, Any],
        config: dict[str, Any],
    ) -> dict[str, Any]:
        """Process an area and return a GeoJSON FeatureCollection."""
        raise NotImplementedError