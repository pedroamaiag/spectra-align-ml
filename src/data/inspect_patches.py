from pathlib import Path

import numpy as np
import rasterio
from rasterio.windows import Window


project_dir = Path(__file__).resolve().parents[2]
raw_dir = project_dir / "data/raw"
processed_dir = project_dir / "data/processed"

patch_size = 64
scale_factor = 10000.0


def validate_patches(region_id, season):
    patch_path = processed_dir / region_id / f"{season}.npz"
    source_dir = raw_dir / f"{region_id}_masked"

    l1c_path = source_dir / f"l1c_{region_id}_{season}_masked.tif"
    l2a_path = source_dir / f"l2a_{region_id}_{season}_masked.tif"

    with np.load(patch_path) as data:
        l1c = data["l1c"]
        l2a = data["l2a"]
        positions = data["positions"]

    if l1c.shape != l2a.shape:
        raise ValueError("Different patch dimensions")

    if l1c.ndim != 4 or l1c.shape[1:] != (4, patch_size, patch_size):
        raise ValueError("Invalid patch dimensions")

    if positions.shape != (len(l1c), 2):
        raise ValueError("Invalid positions")

    if len(np.unique(positions, axis=0)) != len(positions):
        raise ValueError("Duplicate positions")

    if not np.isfinite(l1c).all() or not np.isfinite(l2a).all():
        raise ValueError("Invalid numerical values")

    with rasterio.open(l1c_path) as source_l1c, rasterio.open(l2a_path) as source_l2a:
        for index, (row, col) in enumerate(positions):
            if (
                row < 0 or col < 0
                or row + patch_size > source_l1c.height
                or col + patch_size > source_l1c.width
                or row + patch_size > source_l2a.height
                or col + patch_size > source_l2a.width
            ):
                raise ValueError("Patch outside image bounds")

            window = Window(int(col), int(row), patch_size, patch_size)

            for source, patches in (
                (source_l1c, l1c),
                (source_l2a, l2a)
            ):
                original = source.read(window=window, masked=True)

                if np.ma.getmaskarray(original).any():
                    raise ValueError("Patch contains masked pixels")

                expected = original.data / scale_factor

                if not np.allclose(
                    patches[index], expected, rtol=0, atol=1e-6
                ):
                    raise ValueError("Patch does not match GeoTIFF")

    print(f"{region_id} / {season}: {len(l1c)} patches — PASS")
    return len(l1c)


def main():
    total = 0

    for region_dir in sorted(processed_dir.glob("region_*")):
        if not region_dir.is_dir():
            continue

        for season in ("rainy", "dry"):
            patch_path = region_dir / f"{season}.npz"

            if patch_path.exists():
                total += validate_patches(region_dir.name, season)

    if total == 0:
        raise RuntimeError("No patches found")

    print(f"\nTotal validated patches: {total}")


main()