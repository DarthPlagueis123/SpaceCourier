"""Numerical observations and fixed-timestep interaction with the original game."""
import numpy as np
from game.model import World
from game.settings import WIDTH, HEIGHT, PLAYER_Y

PHYSICS_DT = 1 / 60
ACTION_FRAMES = 6
DIRECTIONS = (0, -1, 1)
OBSTACLE_COUNT = 4
STATE_SIZE = 4 + OBSTACLE_COUNT * 7
STATE_INPUTS = [
    'player_x / WIDTH', 'left clearance / WIDTH', 'right clearance / WIDTH',
    'current difficulty (0..1)',
] + [f'obstacle_{i}.{field}' for i in range(1, OBSTACLE_COUNT + 1) for field in (
    'present', 'x / WIDTH', '(x - player_x) / 100',
    '(PLAYER_Y - y) / HEIGHT', 'radius / 40', 'speed / 300', 'y / HEIGHT')]


def observe(world):
    """No RNG, spawn schedule, future positions, or privileged action labels."""
    state = np.zeros(STATE_SIZE, dtype=np.float32)
    state[:4] = (world.player_x / WIDTH, (world.player_x - 25) / WIDTH,
                 (WIDTH - 25 - world.player_x) / WIDTH, world.difficulty)
    # Passed rocks are no longer threats. Sort the rest by current vertical gap.
    obstacles = sorted((o for o in world.obstacles if o.y - o.radius <= PLAYER_Y + 10),
                       key=lambda o: abs(PLAYER_Y - o.y))[:OBSTACLE_COUNT]
    for i, o in enumerate(obstacles):
        state[4 + i*7:11 + i*7] = (1, o.x / WIDTH, (o.x-world.player_x)/100,
                                   (PLAYER_Y-o.y)/HEIGHT, o.radius/40,
                                   o.speed/300, o.y/HEIGHT)
    return state


class Environment:
    def __init__(self, seed=None, max_seconds=180):
        self.world = World(seed)
        self.max_seconds = max_seconds
        self.steps = 0
        self.done = False

    def reset(self, seed=None):
        if seed is not None:
            self.world.rng.seed(seed)
        self.world.reset()
        self.steps = 0
        self.done = False
        return observe(self.world)

    def step(self, action):
        if isinstance(action, bool) or not isinstance(action, (int, np.integer)) or action not in range(3):
            raise ValueError('Action must be 0 (stay), 1 (left), or 2 (right).')
        if self.done:
            raise RuntimeError('Call reset() after an episode ends.')
        reward = 0.0
        passed = 0
        for _ in range(ACTION_FRAMES):
            before = [(o, o.y - o.radius) for o in self.world.obstacles]
            self.world.update(PHYSICS_DT, DIRECTIONS[action])
            reward += 1 / ACTION_FRAMES
            if not self.world.alive:
                reward -= 20
                break
            passed += sum(y <= PLAYER_Y + 10 < o.y-o.radius for o, y in before)
            if self.world.elapsed >= self.max_seconds:
                break
        reward += .5 * passed
        self.steps += 1
        terminated = not self.world.alive
        truncated = not terminated and self.world.elapsed >= self.max_seconds
        self.done = terminated or truncated
        info = {'score': self.world.score, 'survival_seconds': self.world.elapsed,
                'steps': self.steps, 'terminated': terminated, 'truncated': truncated,
                'passed': passed}
        return observe(self.world), reward, self.done, info
