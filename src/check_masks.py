from pathlib import Path

import numpy as np
import rasterio


data_dir = Path(__file__).resolve().parents[1] / "data/raw"


def check_pair(l1c_path, l2a_path):
    with rasterio.open(l1c_path) as l1c, rasterio.open(l2a_path) as l2a:
        if l1c.count != 4 or l2a.count != 4:
            raise ValueError("Expected four bands")

        if (
            l1c.width != l2a.width
            or l1c.height != l2a.height
            or l1c.crs != l2a.crs
            or l1c.transform != l2a.transform
        ):
            raise ValueError("Rasters are not aligned")

        if l1c.nodata != -9999 or l2a.nodata != -9999:
            raise ValueError("Unexpected NoData value")

        l1c_mask = l1c.read_masks()
        l2a_mask = l2a.read_masks()

        if not np.array_equal(l1c_mask, l2a_mask):
            raise ValueError("Masks are different")

        valid_pixels = np.all(l1c_mask > 0, axis=0)
        valid_count = np.count_nonzero(valid_pixels)
        total_pixels = valid_pixels.size

        print(f"Valid pixels: {valid_count}/{total_pixels}")
        print(f"Valid percentage: {100 * valid_count / total_pixels:.2f}%")
        print("Validation: PASS")


def main():
    total_pairs = 0

    for region_dir in sorted(data_dir.glob("region_*_masked")):
        print(f"\n{region_dir.name}")

        for season in ("rainy", "dry"):
            region_id = region_dir.name.removesuffix("_masked")

            l1c_path = region_dir / f"l1c_{region_id}_{season}_masked.tif"
            l2a_path = region_dir / f"l2a_{region_id}_{season}_masked.tif"

            if not l1c_path.exists() and not l2a_path.exists():
                continue

            if not l1c_path.exists() or not l2a_path.exists():
                raise FileNotFoundError(f"Incomplete pair: {region_dir.name}/{season}")

            print(f"\nSeason: {season}")
            check_pair(l1c_path, l2a_path)

            total_pairs += 1


    if total_pairs == 0:
        raise RuntimeError("No image pairs found")

    print(f"\nTotal validated pairs: {total_pairs}")


main()