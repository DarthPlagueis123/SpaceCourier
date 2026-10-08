import torch
from torch import nn
from .environment import STATE_SIZE


class QNetwork(nn.Module):
    def __init__(self):
        super().__init__()
        self.layers = nn.Sequential(nn.Linear(STATE_SIZE, 128), nn.ReLU(),
                                    nn.Linear(128, 128), nn.ReLU(), nn.Linear(128, 3))

    def forward(self, state):
        return self.layers(state)
