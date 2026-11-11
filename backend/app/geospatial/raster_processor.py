
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from uuid import uuid4

import numpy as np
import rasterio
from pyproj import Transformer
from rasterio.enums import Resampling
from rasterio.mask import mask
from rasterio.vrt import WarpedVRT
from shapely.geometry import shape, mapping
from shapely.ops import transform as transform_geometry

from app.core.config import settings


ALLOWED_ASSET_HOSTS = (
    "amazonaws.com",
    "cloudfront.net",
)


def validate_asset_url(url: str) -> None:
    parsed = urlparse(url)

    if parsed.scheme != "https":
        raise ValueError("Raster asset must use HTTPS.")

    hostname = (parsed.hostname or "").lower()

    if not any(
        hostname == suffix or hostname.endswith("." + suffix)
        for suffix in ALLOWED_ASSET_HOSTS
    ):
        raise ValueError("Untrusted raster asset host.")


def calculate_ndvi(
    red_url: str,
    nir_url: str,
    geometry: dict[str, Any],
) -> dict[str, Any]:
    validate_asset_url(red_url)
    validate_asset_url(nir_url)

    output_dir = Path(settings.DATASET_STORAGE_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"ndvi-{uuid4()}.tif"

    area_geometry = shape(geometry)

    if area_geometry.is_empty or not area_geometry.is_valid:
        raise ValueError("Invalid project area geometry.")

    with rasterio.Env(
        GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
        CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif,.tiff",
    ):
        with rasterio.open(red_url) as red_src:
            if red_src.crs is None:
                raise ValueError("Red band has no CRS.")

            transformer = Transformer.from_crs(
                "EPSG:4326",
                red_src.crs,
                always_xy=True,
            )

            projected_geometry = transform_geometry(
                transformer.transform,
                area_geometry,
            )

            with rasterio.open(nir_url) as nir_src:
                if nir_src.crs is None:
                    raise ValueError("NIR band has no CRS.")

                with WarpedVRT(
                    nir_src,
                    crs=red_src.crs,
                    transform=red_src.transform,
                    width=red_src.width,
                    height=red_src.height,
                    resampling=Resampling.bilinear,
                ) as aligned_nir:

                    red_data, output_transform = mask(
                        red_src,
                        [mapping(projected_geometry)],
                        crop=True,
                        filled=False,
                    )

                    nir_data, _ = mask(
                        aligned_nir,
                        [mapping(projected_geometry)],
                        crop=True,
                        filled=False,
                    )

                    red = red_data[0].astype(np.float32)
                    nir = nir_data[0].astype(np.float32)

                    valid = (
                        ~np.ma.getmaskarray(red_data[0])
                        & ~np.ma.getmaskarray(nir_data[0])
                        & np.isfinite(red)
                        & np.isfinite(nir)
                    )

                    denominator = red + nir

                    valid &= np.abs(denominator) > 1e-10

                    if int(valid.sum()) < settings.NDVI_MIN_VALID_PIXELS:
                        raise ValueError(
                            "The selected area has too few valid raster pixels."
                        )

                    ndvi = np.full(
                        red.shape,
                        settings.NDVI_NODATA,
                        dtype=np.float32,
                    )

                    ndvi[valid] = (
                        (nir[valid] - red[valid])
                        / denominator[valid]
                    )

                    ndvi[valid] = np.clip(
                        ndvi[valid],
                        -1.0,
                        1.0,
                    )

                    profile = red_src.profile.copy()
                    profile.update(
                        driver="GTiff",
                        height=ndvi.shape[0],
                        width=ndvi.shape[1],
                        count=1,
                        dtype="float32",
                        transform=output_transform,
                        nodata=settings.NDVI_NODATA,
                        compress="deflate",
                        tiled=True,
                    )

                    with rasterio.open(
                        output_path,
                        "w",
                        **profile,
                    ) as destination:
                        destination.write(ndvi, 1)
                        destination.set_band_description(
                            1,
                            "NDVI",
                        )
                        destination.update_tags(
                            analysis="NDVI",
                            formula="(NIR - RED) / (NIR + RED)",
                            red_band="B04",
                            nir_band="B08",
                        )

                    valid_values = ndvi[valid]

                    bounds = rasterio.transform.array_bounds(
                        ndvi.shape[0],
                        ndvi.shape[1],
                        output_transform,
                    )

                    return {
                        "path": str(output_path),
                        "file_size_bytes": output_path.stat().st_size,
                        "crs": str(red_src.crs),
                        "bounds": {
                            "left": bounds[0],
                            "bottom": bounds[1],
                            "right": bounds[2],
                            "top": bounds[3],
                        },
                        "statistics": {
                            "min": float(valid_values.min()),
                            "max": float(valid_values.max()),
                            "mean": float(valid_values.mean()),
                            "median": float(
                                np.median(valid_values)
                            ),
                            "valid_pixels": int(valid.sum()),
                            "total_pixels": int(ndvi.size),
                        },
                    }
