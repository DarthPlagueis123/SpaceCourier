"""Real-time inference; decisions and physics match headless training exactly."""
import torch
from .agent import Agent
from .environment import observe, PHYSICS_DT, ACTION_FRAMES, DIRECTIONS


class Playback:
    def __init__(self, path, debug=False):
        self.agent = Agent.load(path)
        self.debug = debug
        self.best = 0
        self.reset()

    def reset(self):
        self.accumulator = 0.0
        self.frame = 0
        self.action = 0
        self.direction = 0
        self.q_values = [0.0, 0.0, 0.0]

    def advance(self, world, dt):
        self.accumulator += dt
        events = []
        while self.accumulator + 1e-9 >= PHYSICS_DT and world.alive:
            if self.frame % ACTION_FRAMES == 0:
                with torch.no_grad():
                    values = self.agent.online(torch.from_numpy(observe(world)))
                self.action = int(values.argmax().item())
                self.q_values = values.tolist()
                self.direction = DIRECTIONS[self.action]
            events.extend(world.update(PHYSICS_DT, self.direction))
            self.accumulator -= PHYSICS_DT
            self.frame += 1
        return events
