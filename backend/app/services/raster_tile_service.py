
from pathlib import Path

import httpx

from app.core.config import settings


def get_safe_raster_path(storage_path: str) -> Path:
    storage_root = Path(settings.DATASET_STORAGE_DIR).resolve()
    file_path = Path(storage_path).resolve()

    if not file_path.is_relative_to(storage_root):
        raise ValueError("Invalid raster storage path.")

    if not file_path.is_file():
        raise FileNotFoundError("Raster file not found.")

    return file_path


async def get_raster_tile(
    storage_path: str,
    z: int,
    x: int,
    y: int,
    colormap_name: str = "rdylgn",
) -> tuple[bytes, str]:
    file_path = get_safe_raster_path(storage_path)

    if not 0 <= z <= 22:
        raise ValueError("Invalid zoom level.")

    tile_limit = 2**z

    if not (0 <= x < tile_limit and 0 <= y < tile_limit):
        raise ValueError("Invalid tile coordinates.")

    url = (
        f"{settings.TITILER_INTERNAL_URL.rstrip('/')}"
        f"/cog/tiles/WebMercatorQuad/{z}/{x}/{y}.png"
    )

    params = {
        "url": str(file_path),
        "bidx": 1,
        "rescale": "-1,1",
        "colormap_name": colormap_name,
        "return_mask": "true",
    }

    async with httpx.AsyncClient(timeout=45.0) as client:
        response = await client.get(url, params=params)

    if response.status_code == 404:
        raise FileNotFoundError("Raster tile is not available.")

    response.raise_for_status()

    return response.content, response.headers.get(
        "content-type",
        "image/png",
    )
