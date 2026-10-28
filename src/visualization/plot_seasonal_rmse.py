import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


project_dir = Path(__file__).resolve().parents[2]

input_path = project_dir / "outputs/metrics/seasonal_validation.csv"
output_path = project_dir / "outputs/previews/seasonal_rmse.png"


def load_results():
    with input_path.open(encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    if not rows:
        raise ValueError("No evaluation results found")

    return rows


def plot_results(rows):
    labels = [
        f'{row["season"]}\n{row["band"]}'
        for row in rows
    ]

    baseline = [float(row["baseline_rmse"]) for row in rows]
    cnn = [float(row["cnn_rmse"]) for row in rows]

    positions = np.arange(len(rows))
    width = 0.35

    fig, ax = plt.subplots(figsize=(11, 5))

    ax.bar(positions - width / 2, baseline, width, label="Baseline")
    ax.bar(positions + width / 2, cnn, width, label="CNN")

    ax.set_xticks(positions, labels)
    ax.set_ylabel("RMSE")
    ax.set_title("Sentinel-2 L1C to L2A — Seasonal RMSE")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    ax.set_axisbelow(True)

    fig.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=160)
    plt.close(fig)

    print(f"Saved: {output_path}")


def main():
    rows = load_results()
    plot_results(rows)


main()