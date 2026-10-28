import json
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader, Dataset


project_dir = Path(__file__).resolve().parents[2]
manifest_path = project_dir / "data/splits.json"


class SentinelDataset(Dataset):
    def __init__(self, split):
        with manifest_path.open(encoding="utf-8") as file:
            manifest = json.load(file)

        if split not in manifest:
            raise ValueError(f"Unknown split: {split}")

        inputs = []
        targets = []

        for entry in manifest[split]:
            path = project_dir / entry["path"]

            with np.load(path) as data:
                x = data["l1c"].astype(np.float32)
                y = data["l2a"].astype(np.float32)

            if x.shape != y.shape or x.ndim != 4:
                raise ValueError(f"Invalid data: {path}")

            if x.shape[1:] != (4, 64, 64):
                raise ValueError(f"Invalid patch size: {path}")

            if len(x) != entry["patches"]:
                raise ValueError(f"Patch count mismatch: {path}")

            inputs.append(x)
            targets.append(y)

        if not inputs:
            raise ValueError(f"Empty dataset: {split}")

        self.inputs = torch.from_numpy(np.concatenate(inputs))
        self.targets = torch.from_numpy(np.concatenate(targets))

    def __len__(self):
        return len(self.inputs)

    def __getitem__(self, index):
        return self.inputs[index], self.targets[index]


def create_loader(split, batch_size=8):
    dataset = SentinelDataset(split)

    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=(split == "train"),
        num_workers=0
    )


def main():
    for split in ("train", "validation", "test"):
        loader = create_loader(split)

        x, y = next(iter(loader))

        print(f"\n{split}")
        print(f"Patches: {len(loader.dataset)}")
        print(f"Batches: {len(loader)}")
        print(f"L1C shape: {tuple(x.shape)}")
        print(f"L2A shape: {tuple(y.shape)}")