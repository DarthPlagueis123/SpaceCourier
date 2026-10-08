"""Original synthesized effects; gracefully tolerates unavailable audio."""
import math
from array import array
import pygame


class Audio:
    def __init__(self):
        self.enabled = True
        self.sounds = {}
        try:
            pygame.mixer.init(22050, -16, 1, 512)
            for name, notes in {'select': [(660, .06)], 'start': [(440, .09), (660, .09), (880, .15)],
                                'milestone': [(880, .08), (1100, .08), (1320, .18)],
                                'death': [(180, .12), (100, .16), (45, .22)]}.items():
                samples = array('h')
                for freq, duration in notes:
                    count = int(22050 * duration)
                    for i in range(count):
                        envelope = (1 - i / count)**1.5
                        samples.append(int(4500 * envelope * (1 if math.sin(2 * math.pi * freq * i / 22050) > 0 else -1)))
                self.sounds[name] = pygame.mixer.Sound(buffer=samples)
        except pygame.error:
            self.enabled = False

    def play(self, name):
        if self.enabled and name in self.sounds:
            self.sounds[name].play()
