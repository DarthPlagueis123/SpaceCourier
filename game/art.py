"""Handmade pixel sprites and procedural arcade scenery."""
import math
import random
import pygame
from .settings import *

# Draw at a native 24 x 24 resolution and scale with nearest neighbors.
# The delivery shuttle carries two little strapped cargo pods.
SHIP = [
    "........................",
    "...........oo...........",
    "..........owwo..........",
    ".........owwwwo.........",
    ".........owwwwo.........",
    "........owccccwo........",
    "........oclllcwo........",
    "...oo...ocllbcwo...oo...",
    "..ott o.occbbcwo.o tto..".replace(" ", "o"),
    "..ottto.owccccwo.ottto..",
    "..otsto.owwwwwwo.otsto..",
    "..otttooowwrrwwooottto..",
    ".ootstooowwrrwwooootstoo.",
    ".owwwoooowwwwww oooowwwo.".replace(" ", "o"),
    ".owwwwooowwsswwooowwwwo.",
    "..owwwwoowwsswwoowwwwo..",
    "..owsswoowwwwwwoowsswo..",
    "...oooo..owwwwo..oooo...",
    "....oo...oeeeeo...oo....",
    ".........oooooo.........",
]
PALETTE = {'o': (30, 30, 54), 'w': (236, 220, 192), 's': (145, 137, 155),
           'r': (222, 111, 99), 'c': (46, 94, 129), 'l': (134, 227, 220),
           'b': (56, 132, 162), 't': (202, 145, 83), 'e': (79, 87, 110)}


def ship_sprite(t, direction=0):
    canvas = pygame.Surface((24, 24), pygame.SRCALPHA)
    for y, row in enumerate(SHIP):
        for x, code in enumerate(row[:24]):
            if code in PALETTE:
                # Banking moves the canopy by one native pixel.
                xx = x + (direction if y < 8 else 0)
                canvas.set_at((max(0, min(23, xx)), y), PALETTE[code])
    flame = (3, 4, 2, 5)[int(t * 12) % 4]
    pygame.draw.rect(canvas, (226, 124, 89), (10, 20, 4, flame))
    pygame.draw.rect(canvas, (255, 219, 134), (11, 20, 2, max(1, flame - 1)))
    canvas.set_at((3, 14), (132, 236, 202))
    canvas.set_at((20, 14), (235, 118, 126))
    # Tiny shipping labels on the strapped crates.
    pygame.draw.rect(canvas, (248, 226, 175), (3, 9, 2, 2))
    pygame.draw.rect(canvas, (248, 226, 175), (19, 9, 2, 2))
    return pygame.transform.scale(canvas, (48, 48))


_METEORS = {}


def meteor(surface, obstacle):
    # Cache a shaded, craggy sprite for each size / variant / animation frame.
    frame = int(obstacle.angle * 2) % 4
    key = (obstacle.radius, obstacle.variant, frame)
    if key not in _METEORS:
        r = obstacle.radius / 2
        size = obstacle.radius + 8
        sprite = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size / 2
        rng = random.Random(obstacle.variant * 71 + obstacle.radius)
        palettes = [((66, 44, 55), (116, 72, 69), (176, 112, 85), (228, 164, 112)),
                    ((52, 49, 67), (94, 82, 103), (144, 121, 140), (205, 175, 162)),
                    ((45, 55, 65), (69, 94, 99), (112, 143, 139), (182, 194, 157))]
        colors = palettes[obstacle.variant]
        points = []
        for i in range(12):
            a = i * math.tau / 12 + frame * .17
            rr = r * rng.uniform(.83, 1.07)
            points.append((round(center + math.cos(a) * rr), round(center + math.sin(a) * rr)))
        pygame.draw.polygon(sprite, colors[0], points)
        inner = [(round(center + (x-center)*.87), round(center + (y-center)*.87)) for x,y in points]
        pygame.draw.polygon(sprite, colors[2], inner)
        # Lighting from the top left, darker lower-right rock face.
        for y in range(size):
            for x in range(size):
                if sprite.get_at((x,y))[:3] == colors[2]:
                    if x + y > size + r*.25:
                        sprite.set_at((x,y), colors[1])
                    elif x + y < size - r*.7 and (x+y)%3:
                        sprite.set_at((x,y), colors[3])
        for _ in range(4):
            x = round(center + rng.uniform(-r*.5, r*.5))
            y = round(center + rng.uniform(-r*.5, r*.5))
            cr = rng.randint(1, 3)
            pygame.draw.circle(sprite, colors[0], (x,y), cr)
            pygame.draw.line(sprite, colors[3], (x-cr,y+cr), (x+1,y+cr))
            pygame.draw.line(sprite, colors[1], (x-cr,y-1), (x+1,y-1))
        _METEORS[key] = pygame.transform.scale(sprite, (size*2, size*2))
    sprite = _METEORS[key]
    surface.blit(sprite, sprite.get_rect(center=(round(obstacle.x), round(obstacle.y))))


class Background:
    def __init__(self):
        rng = random.Random(42)
        self.stars = [(rng.randrange(WIDTH), rng.randrange(HEIGHT), rng.randrange(1, 4)) for _ in range(95)]
        # Static pixel-painted nebula, with dithered edges and muted colors.
        small = pygame.Surface((240, 320))
        small.fill((12, 16, 32))
        for y in range(320):
            for x in range(240):
                band = math.sin(x*.021 + y*.012)*38 + 130
                distance = abs(y - band)
                if distance < 48 and rng.random() < (1-distance/48)*.8:
                    small.set_at((x,y), rng.choice([(20, 25, 45), (25, 29, 51), (30, 31, 55)]))
        self.sky = pygame.transform.scale(small, (WIDTH, HEIGHT))
        self.planet = self.make_planet(49, False)
        self.moon = self.make_planet(17, True)

    def make_planet(self, radius, moon):
        rng = random.Random(radius)
        side = radius*2 + 4
        sprite = pygame.Surface((side, side), pygame.SRCALPHA)
        colors = [(40, 48, 73), (58, 75, 97), (83, 108, 121), (119, 145, 145)] if not moon else [(53, 45, 67), (81, 66, 88), (119, 92, 109), (154, 119, 129)]
        for y in range(side):
            for x in range(side):
                dx, dy = x-radius-2, y-radius-2
                if dx*dx+dy*dy <= radius*radius:
                    light = max(0, min(3, int(2.8 - (dx+dy)/radius*1.4)))
                    stripe = math.sin(y*.25 + math.sin(x*.14)*1.7)
                    if stripe > .3 and light > 0:
                        light -= 1
                    if rng.random() < .13:
                        light = max(0, light-1)
                    sprite.set_at((x,y), colors[light])
        return pygame.transform.scale(sprite, (side*2, side*2))

    def draw(self, surface, t):
        surface.blit(self.sky, (0,0))
        surface.blit(self.planet, (306, 90 + int(math.sin(t*.07)*8)))
        surface.blit(self.moon, (35, 357 + int(math.sin(t*.11)*5)))
        for i, (x, y, depth) in enumerate(self.stars):
            yy = int((y + t * depth * 8) % HEIGHT)
            color = [(47, 58, 85), (98, 125, 148), (184, 201, 199)][depth - 1]
            pygame.draw.rect(surface, color, (x//2*2, yy//2*2, 2, 2))
            if depth == 3 and i % 7 == 0:
                pygame.draw.rect(surface, (62, 84, 108), (x//2*2-2, yy//2*2, 6, 2))
                pygame.draw.rect(surface, color, (x//2*2, yy//2*2-2, 2, 6))
        # Route beacons hug the edges so the asteroid lane stays readable.
        for side in (10, WIDTH-12):
            for i in range(9):
                y = int((i*74 + t*18) % HEIGHT)
                pygame.draw.rect(surface, (35, 56, 73), (side, y, 2, 10))
                pygame.draw.rect(surface, (83, 140, 145), (side, y, 2, 2))


class Particles:
    def __init__(self):
        self.items = []
        self.rng = random.Random()

    def burst(self, x, y, count=50):
        for _ in range(count):
            a = self.rng.uniform(0, math.tau)
            speed = self.rng.uniform(30, 220)
            self.items.append([x, y, math.cos(a) * speed, math.sin(a) * speed,
                               self.rng.uniform(.3, 1), self.rng.choice([CYAN, PINK, GOLD, WHITE])])

    def update(self, dt):
        for p in self.items:
            p[0] += p[2] * dt
            p[1] += p[3] * dt
            p[4] -= dt
        self.items = [p for p in self.items if p[4] > 0]

    def draw(self, surface):
        for x, y, _, _, life, color in self.items:
            pygame.draw.rect(surface, color, (int(x), int(y), 3 if life > .2 else 2, 3))
