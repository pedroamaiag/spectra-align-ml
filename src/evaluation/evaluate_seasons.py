import json
import csv
from pathlib import Path

import numpy as np
import torch

from src.models.residual_cnn import ResidualCNN


project_dir = Path(__file__).resolve().parents[2]
manifest_path = project_dir / "data/splits.json"
model_path = project_dir / "outputs/models/residual_cnn.pt"

band_names = ("B2", "B3", "B4", "B8")


def evaluate_season(entries, season, model=None):
    absolute_error = np.zeros(4)
    squared_error = np.zeros(4)
    pixel_count = 0
    patch_count = 0

    for entry in entries:
        if entry["season"] != season:
            continue

        with np.load(project_dir / entry["path"]) as data:
            inputs = torch.from_numpy(data["l1c"]).float()
            targets = torch.from_numpy(data["l2a"]).float()

        with torch.inference_mode():
            predictions = model(inputs) if model else inputs

        difference = (predictions - targets).double()

        absolute_error += difference.abs().sum(dim=(0, 2, 3)).numpy()
        squared_error += difference.square().sum(dim=(0, 2, 3)).numpy()

        pixel_count += difference.shape[0] * difference.shape[2] * difference.shape[3]
        patch_count += difference.shape[0]

    if pixel_count == 0:
        print(f"\n{season}: no patches")
        return

    mae = absolute_error / pixel_count
    rmse = np.sqrt(squared_error / pixel_count)

    name = "CNN" if model else "Baseline"

    print(f"\n{name} / {season}")
    print(f"Patches: {patch_count}")

    for band, band_mae, band_rmse in zip(band_names, mae, rmse):
        print(f"{band}: MAE={band_mae:.6f} RMSE={band_rmse:.6f}")

    print(f"Overall MAE: {mae.mean():.6f}")
    print(f"Overall RMSE: {np.sqrt(squared_error.sum() / (pixel_count * 4)):.6f}")

    return mae, rmse


def save_results(rows):
    output_path = project_dir / "outputs/metrics/seasonal_validation.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "season",
            "band",
            "baseline_mae",
            "cnn_mae",
            "baseline_rmse",
            "cnn_rmse"
        ])

        writer.writerows(rows)

    print(f"\nSaved: {output_path}")


def main():
    with manifest_path.open(encoding="utf-8") as file:
        entries = json.load(file)["validation"]

    model = ResidualCNN()
    model.load_state_dict(
        torch.load(model_path, map_location="cpu", weights_only=True)
    )
    model.eval()

    rows = []

    for season in ("rainy", "dry"):
        baseline_mae, baseline_rmse = evaluate_season(entries, season)
        cnn_mae, cnn_rmse = evaluate_season(entries, season, model)

        print(f"\nIMPROVEMENT / {season}")

        for index, band in enumerate(band_names):
            reduction = 100 * (
                1 - cnn_rmse[index] / baseline_rmse[index]
            )

            print(f"{band} RMSE reduction: {reduction:.2f}%")

            rows.append([
                season,
                band,
                baseline_mae[index],
                cnn_mae[index],
                baseline_rmse[index],
                cnn_rmse[index]
            ])

        mae_reduction = 100 * (
            1 - cnn_mae.mean() / baseline_mae.mean()
        )

        rmse_reduction = 100 * (
            1 - np.sqrt(np.mean(cnn_rmse ** 2))
            / np.sqrt(np.mean(baseline_rmse ** 2))
        )

        print(f"Overall MAE reduction: {mae_reduction:.2f}%")
        print(f"Overall RMSE reduction: {rmse_reduction:.2f}%")

    save_results(rows)


main()