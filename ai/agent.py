from dataclasses import dataclass, asdict
from pathlib import Path
import numpy as np
import torch
from torch import nn
from .model import QNetwork
from .environment import STATE_INPUTS, STATE_SIZE, ACTION_FRAMES


@dataclass
class Config:
    seed: int = 42
    learning_rate: float = .0003
    gamma: float = .99
    batch_size: int = 128
    replay_capacity: int = 50000
    warmup_steps: int = 3000
    train_every: int = 4
    target_every: int = 2000
    epsilon_start: float = 1.0
    epsilon_end: float = .05
    epsilon_decay_steps: int = 120000
    max_seconds: int = 180


class Agent:
    def __init__(self, config=None):
        self.config = config or Config()
        torch.set_num_threads(1)
        torch.manual_seed(self.config.seed)
        self.rng = np.random.default_rng(self.config.seed)
        self.online = QNetwork()
        self.target = QNetwork()
        self.sync_target()
        self.target.eval()
        self.optimizer = torch.optim.Adam(self.online.parameters(), lr=self.config.learning_rate)
        self.updates = 0

    def epsilon(self, step):
        c = self.config
        return c.epsilon_start + (c.epsilon_end-c.epsilon_start) * min(1, step/c.epsilon_decay_steps)

    def act(self, state, epsilon=0):
        if epsilon and self.rng.random() < epsilon:
            return int(self.rng.integers(3))
        with torch.no_grad():
            return int(self.online(torch.from_numpy(state)).argmax().item())

    def sync_target(self):
        self.target.load_state_dict(self.online.state_dict())

    def learn(self, replay):
        states, actions, rewards, next_states, terminals = replay.sample(self.config.batch_size)
        predicted = self.online(states).gather(1, actions[:, None]).squeeze(1)
        with torch.no_grad():
            # Double DQN: online selects, frozen target evaluates.
            next_actions = self.online(next_states).argmax(1, keepdim=True)
            future = self.target(next_states).gather(1, next_actions).squeeze(1)
            targets = rewards + self.config.gamma * (1-terminals) * future
        loss = nn.functional.smooth_l1_loss(predicted, targets)
        self.optimizer.zero_grad(set_to_none=True)
        loss.backward()
        nn.utils.clip_grad_norm_(self.online.parameters(), 10)
        self.optimizer.step()
        self.updates += 1
        return float(loss.item())

    def save(self, path, **extra):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {'format_version': 1, 'config': asdict(self.config),
                   'state_size': STATE_SIZE, 'state_inputs': STATE_INPUTS,
                   'action_frames': ACTION_FRAMES, 'online': self.online.state_dict(),
                   'target': self.target.state_dict(), 'optimizer': self.optimizer.state_dict(),
                   'updates': self.updates, **extra}
        temporary = path.with_suffix('.tmp')
        torch.save(payload, temporary)
        temporary.replace(path)

    @classmethod
    def load(cls, path, training=False):
        payload = torch.load(path, map_location='cpu', weights_only=True)
        if (payload.get('format_version') != 1 or payload.get('state_size') != STATE_SIZE
                or payload.get('state_inputs') != STATE_INPUTS or payload.get('action_frames') != ACTION_FRAMES):
            raise ValueError('Checkpoint observation or action format does not match this game.')
        agent = cls(Config(**payload['config']))
        agent.online.load_state_dict(payload['online'])
        agent.target.load_state_dict(payload['target'])
        agent.updates = payload['updates']
        if training:
            agent.optimizer.load_state_dict(payload['optimizer'])
        agent.online.train(training)
        return agent
