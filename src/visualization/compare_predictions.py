import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import torch

from src.models.residual_cnn import ResidualCNN


project_dir = Path(__file__).resolve().parents[2]
model_path = project_dir / "outputs/models/residual_cnn.pt"
manifest_path = project_dir / "data/splits.json"
output_path = project_dir / "outputs/previews/comparison_test.png"

samples_per_season = 2


def to_rgb(image):
    return image[[2, 1, 0]].transpose(1, 2, 0)


def load_model():
    model = ResidualCNN()

    model.load_state_dict(
        torch.load(model_path, map_location="cpu", weights_only=True)
    )

    model.eval()
    return model


def load_samples(model):
    with manifest_path.open(encoding="utf-8") as file:
        entries = json.load(file)["test"]

    samples = []

    for entry in entries:
        with np.load(project_dir / entry["path"]) as data:
            inputs = data["l1c"]
            targets = data["l2a"]
            positions = data["positions"]

            count = min(samples_per_season, len(inputs))

            for index in np.linspace(
                0, len(inputs) - 1, count, dtype=int
            ):
                l1c = inputs[index]
                l2a = targets[index]

                tensor = torch.from_numpy(l1c).unsqueeze(0)

                with torch.inference_mode():
                    prediction = model(tensor)[0].numpy()

                samples.append({
                    "region": entry["region"],
                    "season": entry["season"],
                    "position": positions[index],
                    "l1c": l1c,
                    "cnn": prediction,
                    "l2a": l2a,
                    "baseline_error": np.abs(l1c - l2a).mean(axis=0),
                    "cnn_error": np.abs(prediction - l2a).mean(axis=0)
                })

    return samples


def plot_comparison(samples):
    rows = len(samples)

    figure = plt.figure(
        figsize=(17, 3.6 * rows),
        layout="constrained"
    )

    grid = figure.add_gridspec(
        rows * 2,
        5,
        height_ratios=[0.15, 1] * rows
    )

    all_errors = np.stack([
        sample[key]
        for sample in samples
        for key in ("baseline_error", "cnn_error")
    ])

    error_max = max(np.percentile(all_errors, 98), 1e-6)
    heatmap_axes = []

    titles = (
        "L1C",
        "CNN",
        "L2A",
        "Baseline error",
        "CNN error"
    )

    for row, sample in enumerate(samples):
        header = figure.add_subplot(grid[row * 2, :])
        header.axis("off")

        position = sample["position"]

        header.text(
            0, 0.5,
            f'{sample["region"]} | {sample["season"]} | '
            f'row={position[0]}, col={position[1]}',
            fontsize=11,
            weight="bold",
            va="center"
        )

        axes = [
            figure.add_subplot(grid[row * 2 + 1, col])
            for col in range(5)
        ]

        rgb_images = [
            to_rgb(sample[key])
            for key in ("l1c", "cnn", "l2a")
        ]

        combined = np.stack(rgb_images)
        low = np.percentile(combined, 2, axis=(0, 1, 2))
        high = np.percentile(combined, 98, axis=(0, 1, 2))

        for col, image in enumerate(rgb_images):
            rgb = np.clip(
                (image - low) / np.maximum(high - low, 1e-6),
                0, 1
            )

            axes[col].imshow(rgb)

        for col, key in enumerate(
            ("baseline_error", "cnn_error"), start=3
        ):
            error = sample[key]

            heatmap = axes[col].imshow(
                error,
                cmap="magma",
                vmin=0,
                vmax=error_max
            )

            axes[col].set_xlabel(
                f"MAE: {error.mean():.4f}"
            )

            heatmap_axes.append(axes[col])

        for axis, title in zip(axes, titles):
            axis.set_title(title)
            axis.set_xticks([])
            axis.set_yticks([])

    figure.colorbar(
        heatmap,
        ax=heatmap_axes,
        label="Mean absolute error",
        shrink=0.65
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=160)
    plt.close(figure)


def main():
    model = load_model()
    samples = load_samples(model)

    if not samples:
        raise ValueError("No test samples found")

    plot_comparison(samples)

    print(f"Samples compared: {len(samples)}")
    print(f"Saved: {output_path}")


main()