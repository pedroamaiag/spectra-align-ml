import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import rasterio


def normalize_rgb(rgb):
    result = np.zeros(rgb.shape, dtype=np.float32)

    for index in range(3):
        channel = rgb[..., index]
        values = channel.compressed()

        if values.size == 0:
            continue

        low, high = np.percentile(values, [2, 98])

        if high > low:
            result[..., index] = np.clip(
                (channel - low) / (high - low),
                0,
                1,
            ).filled(0)

    return result


def create_preview(input_path, output_path):
    with rasterio.open(input_path) as dataset:
        rgb = dataset.read([3, 2, 1], masked=True)
        rgb = np.moveaxis(rgb, 0, -1)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    plt.imsave(
        output_path,
        normalize_rgb(rgb),
    )


parser = argparse.ArgumentParser()
parser.add_argument("input_path", type=Path)
parser.add_argument("output_path", type=Path)

args = parser.parse_args()

create_preview(
    args.input_path,
    args.output_path,
)

print(f"Saved preview: {args.output_path}")