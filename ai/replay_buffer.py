import numpy as np
import torch
from .environment import STATE_SIZE


class ReplayBuffer:
    def __init__(self, capacity=50000, seed=42):
        self.capacity = capacity
        self.rng = np.random.default_rng(seed)
        self.states = np.empty((capacity, STATE_SIZE), np.float32)
        self.next_states = np.empty_like(self.states)
        self.actions = np.empty(capacity, np.int64)
        self.rewards = np.empty(capacity, np.float32)
        self.terminals = np.empty(capacity, np.float32)
        self.position = self.size = 0

    def add(self, state, action, reward, next_state, terminated):
        i = self.position
        self.states[i], self.next_states[i] = state, next_state
        self.actions[i], self.rewards[i], self.terminals[i] = action, reward, terminated
        self.position = (i + 1) % self.capacity
        self.size = min(self.size + 1, self.capacity)

    def sample(self, batch_size):
        if self.size < batch_size:
            raise ValueError('Not enough transitions for a batch.')
        indices = self.rng.choice(self.size, batch_size, replace=False)
        return tuple(torch.from_numpy(values[indices]) for values in
                     (self.states, self.actions, self.rewards, self.next_states, self.terminals))
