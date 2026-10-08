"""Game rules and entities, independent of display and sound."""
from dataclasses import dataclass
import random
from .settings import WIDTH, HEIGHT, PLAYER_Y, PLAYER_SPEED


@dataclass
class Obstacle:
    x: float
    y: float
    radius: int
    speed: float
    variant: int
    angle: float = 0


class World:
    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.reset()

    def reset(self):
        self.player_x = WIDTH / 2
        self.elapsed = 0.0
        self.obstacles = []
        self.alive = True
        self.spawn_timer = 0.8
        self.milestone = 0

    @property
    def score(self):
        return int(self.elapsed * 100)

    @property
    def level(self):
        return 1 + int(self.elapsed // 15)

    @property
    def difficulty(self):
        return min(self.elapsed / 90, 1.0)

    def update(self, dt, direction):
        if not self.alive:
            return []
        events = []
        self.player_x = max(25, min(WIDTH - 25, self.player_x + direction * PLAYER_SPEED * dt))
        self.elapsed += dt
        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            # One hazard per wave and a minimum gap preserve escape routes.
            radius = self.rng.randint(13, 24)
            self.obstacles.append(Obstacle(self.rng.uniform(30, WIDTH - 30), -32, radius,
                                           125 + 140 * self.difficulty + self.rng.uniform(0, 35),
                                           self.rng.randrange(3)))
            self.spawn_timer += 0.95 - 0.53 * self.difficulty
        for obstacle in self.obstacles:
            obstacle.y += obstacle.speed * dt
            obstacle.angle += dt * (0.7 + obstacle.variant * 0.3)
            # Forgiving collision circle inside the ship's visible silhouette.
            if (obstacle.x - self.player_x)**2 + (obstacle.y - PLAYER_Y)**2 < (obstacle.radius + 10)**2:
                self.alive = False
                events.append('death')
                break
        self.obstacles = [o for o in self.obstacles if o.y < HEIGHT + 40]
        milestone = int(self.elapsed // 15)
        if self.alive and milestone > self.milestone:
            self.milestone = milestone
            events.append('milestone')
        return events
