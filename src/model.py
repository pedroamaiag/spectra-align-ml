import torch
from torch import nn


class ResidualCNN(nn.Module):
    def __init__(self):
        super().__init__()

        self.layers = nn.Sequential(
            nn.Conv2d(4, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(32, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(32, 4, kernel_size=3, padding=1)
        )

    def forward(self, x):
        correction = self.layers(x)
        return x + correction