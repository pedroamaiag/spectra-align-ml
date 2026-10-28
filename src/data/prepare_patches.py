from pathlib import Path

import numpy as np
import rasterio


project_dir = Path(__file__).resolve().parents[2]
raw_dir = project_dir / "data/raw"
processed_dir = project_dir / "data/processed"

patch_size = 64
scale_factor = 10000.0


def load_pair(l1c_path, l2a_path):
    with rasterio.open(l1c_path) as l1c_ds, rasterio.open(l2a_path) as l2a_ds:
        if l1c_ds.count != 4 or l2a_ds.count != 4:
            raise ValueError("Expected four spectral bands")

        if (
            l1c_ds.width != l2a_ds.width
            or l1c_ds.height != l2a_ds.height
            or l1c_ds.crs != l2a_ds.crs
            or l1c_ds.transform != l2a_ds.transform
        ):
            raise ValueError("Rasters are not aligned")

        l1c = l1c_ds.read(masked=True)
        l2a = l2a_ds.read(masked=True)

    l1c_mask = np.ma.getmaskarray(l1c)
    l2a_mask = np.ma.getmaskarray(l2a)

    if not np.array_equal(l1c_mask, l2a_mask):
        raise ValueError("Masks are different")

    valid_pixels = ~np.any(l1c_mask, axis=0)

    return l1c.data, l2a.data, valid_pixels


def extract_patches(l1c, l2a, valid_pixels):
    x_patches = []
    y_patches = []
    positions = []

    height, width = valid_pixels.shape
    total = 0

    for row in range(0, height - patch_size + 1, patch_size):
        for col in range(0, width - patch_size + 1, patch_size):
            total += 1

            area = np.s_[row:row + patch_size, col:col + patch_size]

            if not valid_pixels[area].all():
                continue

            x = l1c[:, area[0], area[1]].astype(np.float32)
            y = l2a[:, area[0], area[1]].astype(np.float32)

            if not np.isfinite(x).all() or not np.isfinite(y).all():
                continue

            x_patches.append(x / scale_factor)
            y_patches.append(y / scale_factor)
            positions.append((row, col))

    return x_patches, y_patches, positions, total


def process_pair(region_id, season, l1c_path, l2a_path):
    l1c, l2a, valid_pixels = load_pair(l1c_path, l2a_path)

    x, y, positions, total = extract_patches(
        l1c, l2a, valid_pixels
    )

    print(f"\n{region_id} / {season}")
    print(f"Candidate patches: {total}")
    print(f"Valid patches: {len(x)}")
    print(f"Discarded patches: {total - len(x)}")

    if not x:
        print("No valid patches found")
        return

    output_dir = processed_dir / region_id
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{season}.npz"

    np.savez_compressed(
        output_path,
        l1c=np.stack(x),
        l2a=np.stack(y),
        positions=np.array(positions, dtype=np.int32)
    )

    print(f"Saved: {output_path}")


def main():
    for region_dir in sorted(raw_dir.glob("region_*_masked")):
        region_id = region_dir.name.removesuffix("_masked")

        for season in ("rainy", "dry"):
            l1c_path = region_dir / f"l1c_{region_id}_{season}_masked.tif"
            l2a_path = region_dir / f"l2a_{region_id}_{season}_masked.tif"

            if not l1c_path.exists() and not l2a_path.exists():
                continue

            if not l1c_path.exists() or not l2a_path.exists():
                raise FileNotFoundError(
                    f"Incomplete pair: {region_id}/{season}"
                )

            process_pair(region_id, season, l1c_path, l2a_path)


main()