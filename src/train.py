from pathlib import Path

import torch
from torch import nn

from dataset import create_loader
from model import ResidualCNN


project_dir = Path(__file__).resolve().parents[1]
model_path = project_dir / "outputs/models/residual_cnn.pt"

epochs = 20
learning_rate = 0.001
batch_size = 8

torch.manual_seed(42)


def evaluate(model, loader):
    model.eval()

    absolute_error = 0.0
    squared_error = 0.0
    total_values = 0

    with torch.no_grad():
        for inputs, targets in loader:
            predictions = model(inputs)
            difference = predictions - targets

            absolute_error += difference.abs().sum().item()
            squared_error += difference.square().sum().item()
            total_values += difference.numel()

    mae = absolute_error / total_values
    rmse = (squared_error / total_values) ** 0.5

    return mae, rmse


def train():
    train_loader = create_loader("train", batch_size)
    val_loader = create_loader("validation", batch_size)

    model = ResidualCNN()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    criterion = nn.MSELoss()

    best_rmse = float("inf")
    model_path.parent.mkdir(parents=True, exist_ok=True)

    for epoch in range(1, epochs + 1):
        model.train()

        for inputs, targets in train_loader:
            optimizer.zero_grad()

            predictions = model(inputs)
            loss = criterion(predictions, targets)

            loss.backward()
            optimizer.step()

        train_mae, train_rmse = evaluate(model, train_loader)
        val_mae, val_rmse = evaluate(model, val_loader)

        print(
            f"Epoch {epoch:02d}/{epochs} | "
            f"Train MAE: {train_mae:.6f} | "
            f"Train RMSE: {train_rmse:.6f} | "
            f"Val MAE: {val_mae:.6f} | "
            f"Val RMSE: {val_rmse:.6f}"
        )

        if val_rmse < best_rmse:
            best_rmse = val_rmse
            torch.save(model.state_dict(), model_path)

    print(f"\nBest validation RMSE: {best_rmse:.6f}")
    print(f"Model saved: {model_path}")


train()