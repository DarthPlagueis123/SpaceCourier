import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
import tempfile
import unittest
from pathlib import Path
import pygame
from game.model import World, Obstacle
from game.settings import PLAYER_Y
from game.game import Game


class RulesTests(unittest.TestCase):
    def test_movement_bounds_score_and_restart(self):
        w = World(1)
        for _ in range(120):
            w.update(1 / 60, -1)
        self.assertEqual(w.player_x, 25)
        self.assertAlmostEqual(w.elapsed, 2)
        self.assertGreaterEqual(w.score, 199)
        w.obstacles.clear()
        w.update(2, 1)
        self.assertEqual(w.player_x, 455)
        w.reset()
        self.assertEqual(w.score, 0)
        self.assertEqual(w.obstacles, [])
        self.assertTrue(w.alive)

    def test_spawn_motion_difficulty_and_cleanup(self):
        w = World(3)
        w.update(.81, 0)
        self.assertEqual(len(w.obstacles), 1)
        y = w.obstacles[0].y
        w.update(.1, 0)
        self.assertGreater(w.obstacles[0].y, y)
        w.elapsed = 89.99
        w.obstacles.clear()
        w.spawn_timer = 0
        self.assertIn('milestone', w.update(.02, 0))
        self.assertEqual(w.difficulty, 1)
        self.assertEqual(w.level, 7)
        self.assertGreater(w.obstacles[0].speed, 260)
        self.assertLessEqual(w.spawn_timer, .42)
        w.obstacles = [Obstacle(40, 700, 15, 120, 0)]
        w.update(.01, 0)
        self.assertEqual(w.obstacles, [])

    def test_collision_and_score_freeze(self):
        w = World()
        w.obstacles = [Obstacle(w.player_x, PLAYER_Y, 15, 0, 0)]
        self.assertIn('death', w.update(.1, 0))
        self.assertFalse(w.alive)
        score = w.score
        w.update(10, 1)
        self.assertEqual(w.score, score)


class ScreenTests(unittest.TestCase):
    def test_screens_persistence_focus_and_repeated_restarts(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as folder:
            path = Path(folder) / 'scores.json'
            g = Game(path)
            self.assertEqual(g.state, 'title')
            g.draw()
            def key(k):
                g.handle_event(pygame.event.Event(pygame.KEYDOWN, key=k))
            key(pygame.K_RETURN)
            self.assertEqual(g.state, 'playing')
            g.update(.1, 1)
            self.assertGreater(g.world.player_x, 240)
            key(pygame.K_ESCAPE)
            before = g.world.elapsed
            g.update(1, 0)
            self.assertEqual(g.world.elapsed, before)
            g.draw()
            key(pygame.K_RETURN)
            self.assertEqual(g.state, 'playing')
            g.handle_event(pygame.event.Event(pygame.WINDOWFOCUSLOST))
            self.assertEqual(g.state, 'paused')
            key(pygame.K_ESCAPE)
            for _ in range(25):
                g.world.obstacles = [Obstacle(g.world.player_x, PLAYER_Y, 20, 0, 0)]
                g.update(.1, 0)
                self.assertEqual(g.state, 'over')
                g.draw()
                self.assertEqual(g.load_best(), g.best)
                key(pygame.K_r)
                self.assertEqual(g.state, 'playing')
                self.assertEqual(g.world.obstacles, [])
                self.assertEqual(g.particles.items, [])
            key(pygame.K_ESCAPE)
            key(pygame.K_DOWN)
            key(pygame.K_RETURN)
            self.assertEqual(g.state, 'playing')
            g.audio.play('death')
            key(pygame.K_m)
            g.audio.play('start')
            pygame.quit()


if __name__ == '__main__':
    unittest.main()
