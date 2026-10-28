import argparse
from pathlib import Path

import numpy as np
import rasterio


BAND_NAMES = ("B2", "B3", "B4", "B8")


def band_statistics(dataset):
    statistics = []

    for band_number in range(1, dataset.count + 1):
        values = dataset.read(
            band_number,
            masked=True,
        ).compressed()

        if values.size:
            statistics.append(
                (
                    values.min(),
                    values.max(),
                    values.mean(),
                    values.std(),
                )
            )

    return statistics


def inspect_raster(path):
    with rasterio.open(path) as dataset:
        print(f"\n{path.name}")
        print(f"Number of bands: {dataset.count}")
        print(f"Dimensions: {dataset.width} x {dataset.height}")
        print(f"CRS: {dataset.crs}")
        print(f"Resolution: {dataset.res}")
        print(f"Bounds: {dataset.bounds}")
        print(f"Affine transform: {dataset.transform}")
        print(f"Data type: {', '.join(dataset.dtypes)}")

        statistics = band_statistics(dataset)

        for index, values in enumerate(statistics):
            minimum, maximum, mean, standard_deviation = values
            band_name = BAND_NAMES[index]

            print(
                f"Band {index + 1} ({band_name}): "
                f"min={minimum:.4f}, "
                f"max={maximum:.4f}, "
                f"mean={mean:.4f}, "
                f"std={standard_deviation:.4f}"
            )

        return {
            "band_count": dataset.count,
            "dimensions": (dataset.width, dataset.height),
            "crs": dataset.crs,
            "resolution": dataset.res,
            "bounds": dataset.bounds,
            "transform": dataset.transform,
        }


def check(name, condition):
    result = "PASS" if condition else "FAIL"
    print(f"{name}: {result}")


parser = argparse.ArgumentParser()
parser.add_argument("l1c_path", type=Path)
parser.add_argument("l2a_path", type=Path)

args = parser.parse_args()

l1c = inspect_raster(args.l1c_path)
l2a = inspect_raster(args.l2a_path)

print("\nValidation")

check("L1C has four bands", l1c["band_count"] == 4)
check("L2A has four bands", l2a["band_count"] == 4)
check("Same dimensions", l1c["dimensions"] == l2a["dimensions"])
check("Same CRS", l1c["crs"] == l2a["crs"])
check(
    "Same resolution",
    np.allclose(l1c["resolution"], l2a["resolution"]),
)
check(
    "Same bounds",
    np.allclose(l1c["bounds"], l2a["bounds"]),
)
check(
    "Same affine transform",
    np.allclose(
        tuple(l1c["transform"]),
        tuple(l2a["transform"]),
    ),
)