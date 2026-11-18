import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.warp import reproject


def detect_ndvi_change(
    before_path: str,
    after_path: str,
    output_path: str,
    threshold: float = 0.1,
):
    if threshold <= 0 or threshold > 1:
        raise ValueError("threshold must be greater than 0 and at most 1")

    with rasterio.open(before_path) as before:
        before_data = before.read(1).astype("float32")
        before_valid = before.read_masks(1) > 0

        profile = before.profile.copy()

        after_aligned = np.full(
            (before.height, before.width),
            np.nan,
            dtype="float32",
        )

        with rasterio.open(after_path) as after:
            reproject(
                source=rasterio.band(after, 1),
                destination=after_aligned,
                src_transform=after.transform,
                src_crs=after.crs,
                dst_transform=before.transform,
                dst_crs=before.crs,
                dst_nodata=np.nan,
                resampling=Resampling.bilinear,
            )

            after_valid = np.isfinite(after_aligned)

        valid = (
            before_valid
            & np.isfinite(before_data)
            & after_valid
            & (before_data >= -1)
            & (before_data <= 1)
            & (after_aligned >= -1)
            & (after_aligned <= 1)
        )

        delta = np.full(
            before_data.shape,
            np.nan,
            dtype="float32",
        )

        delta[valid] = after_aligned[valid] - before_data[valid]

        # Classification:
        # 0 = NoData
        # 1 = Vegetation loss
        # 2 = Stable
        # 3 = Vegetation gain
        classes = np.zeros(
            before_data.shape,
            dtype="uint8",
        )

        classes[valid & (delta < -threshold)] = 1
        classes[valid & (delta >= -threshold) & (delta <= threshold)] = 2
        classes[valid & (delta > threshold)] = 3

        profile.update(
            driver="GTiff",
            count=2,
            dtype="float32",
            nodata=-9999.0,
            compress="deflate",
            tiled=True,
        )

        delta_output = np.where(valid, delta, -9999.0)

        # Store delta as band 1 and class codes as band 2.
        with rasterio.open(output_path, "w", **profile) as output:
            output.write(delta_output.astype("float32"), 1)
            output.write(classes.astype("float32"), 2)

            output.set_band_description(1, "NDVI difference")
            output.set_band_description(2, "Change classification")

        if not np.any(valid):
            raise ValueError(
                "The two rasters have no overlapping valid pixels"
            )

        valid_delta = delta[valid]

        return {
            "threshold": threshold,
            "valid_pixels": int(valid.sum()),
            "mean_change": float(np.mean(valid_delta)),
            "minimum_change": float(np.min(valid_delta)),
            "maximum_change": float(np.max(valid_delta)),
            "vegetation_loss_pixels": int(np.sum(classes == 1)),
            "stable_pixels": int(np.sum(classes == 2)),
            "vegetation_gain_pixels": int(np.sum(classes == 3)),
            "vegetation_loss_percentage": float(
                np.sum(classes == 1) / valid.sum() * 100
            ),
            "stable_percentage": float(
                np.sum(classes == 2) / valid.sum() * 100
            ),
            "vegetation_gain_percentage": float(
                np.sum(classes == 3) / valid.sum() * 100
            ),
        }