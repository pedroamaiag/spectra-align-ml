import torch

from src.data.dataset import create_loader


band_names = ("B2", "B3", "B4", "B8")


def evaluate(split):
    loader = create_loader(split)

    absolute_errors = torch.zeros(4)
    squared_errors = torch.zeros(4)
    pixel_count = 0

    for l1c, l2a in loader:
        difference = l1c - l2a

        absolute_errors += difference.abs().sum(dim=(0, 2, 3))
        squared_errors += difference.square().sum(dim=(0, 2, 3))

        pixel_count += l1c.shape[0] * l1c.shape[2] * l1c.shape[3]

    mae = absolute_errors / pixel_count
    rmse = torch.sqrt(squared_errors / pixel_count)

    print(f"\n{split.upper()} — Identity baseline")

    for index, band in enumerate(band_names):
        print(
            f"{band}: MAE={mae[index]:.6f} "
            f"RMSE={rmse[index]:.6f}"
        )

    print(f"Overall MAE: {mae.mean():.6f}")
    print(f"Overall RMSE: {torch.sqrt(squared_errors.sum() / (pixel_count * 4)):.6f}")


evaluate("train")
evaluate("validation")