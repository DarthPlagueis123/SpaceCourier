import json
import os
from pathlib import Path
import random
import pygame
from .settings import *
from .model import World
from .art import Background, Particles, ship_sprite, meteor
from .audio import Audio


class Game:
    def __init__(self, save_path=None):
        pygame.mixer.pre_init(22050, -16, 1, 512)
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption('SPACE COURIER | Special delivery')
        self.canvas = pygame.Surface((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.fonts = {size: pygame.font.Font(None, size) for size in (18, 22, 26, 32, 44, 64, 80)}
        self.world = World()
        self.background = Background()
        self.particles = Particles()
        self.audio = Audio()
        self.save_path = Path(save_path) if save_path else Path(os.getenv('LOCALAPPDATA', str(Path.home()))) / 'PixelPanic' / 'scores.json'
        self.best = self.load_best()
        self.state = 'title'
        self.running = True
        self.time = 0
        self.shake = 0
        self.flash = 0
        self.popup = 0
        self.death_time = 0
        self.selection = 0
        self.direction = 0
        self.new_best = False
        self.ai_controller = None
        self.ai_model_path = Path(__file__).resolve().parents[1] / 'models' / 'best_model.pth'
        self.ai_debug = False
        self.menu_message = ''

    def load_best(self):
        try:
            return max(0, int(json.loads(self.save_path.read_text())['best']))
        except (OSError, ValueError, KeyError, TypeError):
            return 0

    def save_best(self):
        try:
            self.save_path.parent.mkdir(parents=True, exist_ok=True)
            self.save_path.write_text(json.dumps({'best': self.best}))
        except OSError:
            pass  # A read-only profile must never prevent playing.

    def start(self):
        self.world.reset()
        self.particles.items.clear()
        self.state = 'playing'
        self.shake = self.flash = self.popup = self.death_time = 0
        self.new_best = False
        if self.ai_controller is not None:
            self.ai_controller.reset()
        self.audio.play('start')

    def watch_ai(self):
        try:
            from ai.playback import Playback
            self.ai_controller = Playback(self.ai_model_path, self.ai_debug)
        except (OSError, ValueError, RuntimeError, ImportError) as error:
            self.menu_message = 'AI MODEL UNAVAILABLE - SEE README'
            print(f'Could not load AI: {error}')
            return
        self.menu_message = ''
        self.start()

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        if event.type == pygame.WINDOWFOCUSLOST and self.state == 'playing':
            self.state = 'paused'
            self.selection = 0
        if event.type != pygame.KEYDOWN:
            return
        key = event.key
        if key == pygame.K_m:
            self.audio.enabled = not self.audio.enabled
        if self.state == 'title':
            if key in (pygame.K_RETURN, pygame.K_SPACE):
                self.ai_controller = None
                self.start()
            elif key == pygame.K_i:
                self.watch_ai()
            elif key == pygame.K_ESCAPE:
                self.running = False
        elif self.state == 'playing':
            if key == pygame.K_ESCAPE:
                self.state = 'paused'
                self.selection = 0
                self.audio.play('select')
        elif self.state == 'paused':
            if key == pygame.K_ESCAPE:
                self.state = 'playing'
            elif key in (pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s):
                self.selection = (self.selection + (-1 if key in (pygame.K_UP, pygame.K_w) else 1)) % 3
                self.audio.play('select')
            elif key == pygame.K_r:
                self.start()
            elif key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.selection == 0:
                    self.state = 'playing'
                elif self.selection == 1:
                    self.start()
                else:
                    self.running = False
        elif self.state == 'over':
            if key in (pygame.K_r, pygame.K_RETURN, pygame.K_SPACE):
                self.start()
            elif key == pygame.K_ESCAPE:
                self.state = 'title'
                self.ai_controller = None

    def update(self, dt, direction=None):
        self.time += dt
        self.shake = max(0, self.shake - dt)
        self.flash = max(0, self.flash - dt)
        if self.state == 'playing':
            if self.ai_controller is not None:
                events = self.ai_controller.advance(self.world, dt)
                self.direction = self.ai_controller.direction
            else:
                if direction is None:
                    keys = pygame.key.get_pressed()
                    direction = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
                self.direction = direction
                events = self.world.update(dt, direction)
            self.popup = max(0, self.popup - dt)
            for event in events:
                self.audio.play(event)
                if event == 'death':
                    self.state = 'over'
                    self.death_time = 0
                    self.shake = .45
                    self.flash = .12
                    self.particles.burst(self.world.player_x, PLAYER_Y)
                    if self.ai_controller is not None:
                        self.new_best = self.world.score > self.ai_controller.best
                        self.ai_controller.best = max(self.ai_controller.best, self.world.score)
                    else:
                        self.new_best = self.world.score > self.best
                        self.best = max(self.best, self.world.score)
                        self.save_best()
                else:
                    self.popup = 2
        if self.state == 'over':
            self.death_time += dt
        if self.state != 'paused':
            self.particles.update(dt)

    def text(self, value, y, size=26, color=WHITE, x=None):
        rendered = self.fonts[size].render(str(value), False, color)
        rect = rendered.get_rect(center=(WIDTH // 2 if x is None else x, y))
        self.canvas.blit(rendered, rect)

    def panel(self, rect):
        pygame.draw.rect(self.canvas, (13, 20, 43), rect)
        pygame.draw.rect(self.canvas, CYAN, rect, 2)
        pygame.draw.rect(self.canvas, (37, 68, 91), rect.inflate(-10, -10), 1)

    def hud(self):
        pygame.draw.rect(self.canvas, (10, 16, 34), (0, 0, WIDTH, 76))
        pygame.draw.line(self.canvas, (48, 99, 128), (20, 76), (460, 76), 2)
        self.text('SCORE', 22, 18, CYAN, 74)
        self.text(f'{self.world.score:06}', 49, 32, WHITE, 74)
        self.text('BEST', 22, 18, PINK, 240)
        self.text(f'{max(self.display_best, self.world.score):06}', 49, 32, WHITE, 240)
        self.text('SECTOR', 22, 18, GOLD, 408)
        self.text(f'{self.world.level:02}', 49, 32, GOLD, 408)

    @property
    def display_best(self):
        return self.ai_controller.best if self.ai_controller is not None else self.best

    def draw(self):
        self.background.draw(self.canvas, self.time if self.state != 'paused' else self.world.elapsed)
        if self.state == 'title':
            self.text('INTERSTELLAR POSTAL SERVICE', 88, 18, CYAN)
            self.text('SPACE', 180, 80, (51, 50, 96))
            self.text('SPACE', 176, 80, WHITE)
            self.text('COURIER', 240, 64, GOLD)
            self.text('PRECIOUS CARGO. PERILOUS ROUTE.', 299, 22, WHITE)
            sprite = ship_sprite(self.time)
            self.canvas.blit(pygame.transform.scale(sprite, (96, 96)), (192, 332))
            if int(self.time * 2) % 2 == 0:
                self.text('ENTER / SPACE  PLAY GAME', 466, 26, CYAN)
            self.text('I  WATCH AI', 499, 22, GOLD)
            if self.menu_message:
                self.text(self.menu_message, 582, 18, PINK)
            self.text('A / D  OR  ARROW KEYS TO DODGE', 535, 18)
            self.text('ESC  BACK / QUIT     M  SOUND', 562, 18, (116, 143, 172))
            self.text(f'PERSONAL BEST  {self.best:06}', 608, 18, GOLD)
        else:
            for obstacle in self.world.obstacles:
                meteor(self.canvas, obstacle)
            if self.world.alive:
                sprite = ship_sprite(self.time, self.direction)
                self.canvas.blit(sprite, sprite.get_rect(center=(int(self.world.player_x), PLAYER_Y)))
            self.particles.draw(self.canvas)
            self.hud()
            self.text('AI MODE   |   ESC PAUSE   M SOUND' if self.ai_controller else 'ESC PAUSE     M SOUND',
                      625, 18, GOLD if self.ai_controller else (110, 138, 169))
            if self.ai_controller is not None and self.ai_controller.debug:
                controller = self.ai_controller
                self.text(f'ACTION {controller.action}   Q ' + ' / '.join(f'{q:.1f}' for q in controller.q_values),
                          145, 18, GOLD)
            if self.popup and self.state == 'playing':
                self.text(f'SECTOR {self.world.level:02} / SPEED UP', 119, 26, GOLD)
            if self.state in ('paused', 'over'):
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((5, 7, 20, 175))
                self.canvas.blit(overlay, (0, 0))
                self.panel(pygame.Rect(48, 180, 384, 298))
                if self.state == 'paused':
                    self.text('PAUSED', 228, 44, CYAN)
                    self.text('DELIVERY CAN WAIT A MOMENT.', 266, 18)
                    for i, label in enumerate(('RESUME', 'RESTART', 'QUIT')):
                        self.text(('> ' if i == self.selection else '  ') + label, 321 + i * 44,
                                  26, GOLD if i == self.selection else WHITE)
                    self.text('UP / DOWN + ENTER  |  ESC RESUME', 454, 18, CYAN)
                else:
                    self.text('GAME OVER', 228, 44, PINK)
                    self.text('NEW PERSONAL BEST!' if self.new_best else 'THE MAIL MUST GO ON!', 270, 22, GOLD)
                    shown = int(self.world.score * min(1, self.death_time / .7))
                    self.text(f'{shown:06}', 318, 64, WHITE)
                    self.text(f'SURVIVED {self.world.elapsed:.1f}s  /  BEST {self.display_best:06}', 366, 18, CYAN)
                    self.text('R / ENTER TO RESTART', 417, 26, GOLD)
                    self.text('ESC TO TITLE', 451, 18)
        if self.flash:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 210, 225, int(110 * self.flash / .12)))
            self.canvas.blit(overlay, (0, 0))
        # Integer scaling when possible keeps handmade pixels crisp.
        sw, sh = self.screen.get_size()
        scale = min(sw / WIDTH, sh / HEIGHT)
        if scale >= 1:
            scale = max(1, int(scale))
        size = (max(1, int(WIDTH * scale)), max(1, int(HEIGHT * scale)))
        view = pygame.transform.scale(self.canvas, size)
        offset = (random.randint(-4, 4), random.randint(-4, 4)) if self.shake else (0, 0)
        self.screen.fill((4, 6, 15))
        self.screen.blit(view, ((sw - size[0]) // 2 + offset[0], (sh - size[1]) // 2 + offset[1]))
        pygame.display.flip()

    def run(self):
        while self.running:
            dt = min(self.clock.tick(FPS) / 1000, .05)
            for event in pygame.event.get():
                self.handle_event(event)
            self.update(dt)
            self.draw()
        pygame.quit()
