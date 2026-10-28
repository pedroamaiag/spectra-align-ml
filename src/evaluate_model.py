from pathlib import Path

import torch

from dataset import create_loader
from model import ResidualCNN


project_dir = Path(__file__).resolve().parents[1]
model_path = project_dir / "outputs/models/residual_cnn.pt"

band_names = ("B2", "B3", "B4", "B8")


def evaluate():
    loader = create_loader("test")

    model = ResidualCNN()
    model.load_state_dict(
        torch.load(model_path, map_location="cpu", weights_only=True)
    )
    model.eval()

    results = {
        "baseline": [torch.zeros(4), torch.zeros(4)],
        "cnn": [torch.zeros(4), torch.zeros(4)]
    }

    pixel_count = 0

    with torch.inference_mode():
        for inputs, targets in loader:
            predictions = model(inputs)

            for name, output in (
                ("baseline", inputs),
                ("cnn", predictions)
            ):
                difference = output - targets

                results[name][0] += difference.abs().sum(dim=(0, 2, 3))
                results[name][1] += difference.square().sum(dim=(0, 2, 3))

            pixel_count += inputs.shape[0] * inputs.shape[2] * inputs.shape[3]

    print(f"Test patches: {len(loader.dataset)}")

    for name, (absolute, squared) in results.items():
        mae = absolute / pixel_count
        rmse = torch.sqrt(squared / pixel_count)

        overall_mae = mae.mean()
        overall_rmse = torch.sqrt(squared.sum() / (pixel_count * 4))

        print(f"\n{name.upper()}")

        for index, band in enumerate(band_names):
            print(
                f"{band}: MAE={mae[index]:.6f} "
                f"RMSE={rmse[index]:.6f}"
            )

        print(f"Overall MAE: {overall_mae:.6f}")
        print(f"Overall RMSE: {overall_rmse:.6f}")


evaluate()