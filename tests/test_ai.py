import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
import tempfile
import unittest
from pathlib import Path
import numpy as np
import torch
from ai.agent import Agent, Config
from ai.environment import Environment, observe, STATE_SIZE, PHYSICS_DT, ACTION_FRAMES
from ai.replay_buffer import ReplayBuffer
from ai.playback import Playback
from ai.evaluate import evaluate
from game.model import Obstacle
from game.settings import PLAYER_Y


class EnvironmentTests(unittest.TestCase):
    def test_seed_actions_normalization_and_reset(self):
        a, b = Environment(), Environment()
        np.testing.assert_array_equal(a.reset(55), b.reset(55))
        self.assertEqual(observe(a.world).shape, (STATE_SIZE,))
        self.assertTrue(np.isfinite(observe(a.world)).all())
        for _ in range(40):
            left = a.step(1)
            right = b.step(1)
            np.testing.assert_array_equal(left[0], right[0])
            self.assertEqual(left[1:], right[1:])
            if left[2]:
                break
        self.assertEqual(a.world.player_x, 25)
        a.reset(55)
        self.assertEqual(a.steps, 0)
        self.assertEqual(a.world.score, 0)
        self.assertEqual(a.world.obstacles, [])
        a.step(2)
        self.assertAlmostEqual(a.world.player_x, 269)
        for invalid in (-1, 3, 1.5, True):
            with self.assertRaises(ValueError):
                a.step(invalid)

    def test_terminal_truncation_reward_and_no_future_input(self):
        env = Environment(max_seconds=.1)
        state = env.reset(1)
        # Hidden RNG and next-spawn timer do not appear in the observation.
        env.world.spawn_timer = 999
        env.world.rng.seed(999)
        np.testing.assert_array_equal(state, observe(env.world))
        _, reward, done, info = env.step(0)
        if not done:
            _, reward, done, info = env.step(0)
        self.assertTrue(done)
        self.assertTrue(info['truncated'])
        self.assertFalse(info['terminated'])
        self.assertGreater(reward, 0)
        with self.assertRaises(RuntimeError):
            env.step(0)
        env = Environment()
        env.world.obstacles = [Obstacle(240, PLAYER_Y, 20, 0, 0)]
        _, reward, done, info = env.step(0)
        self.assertTrue(done)
        self.assertTrue(info['terminated'])
        self.assertLess(reward, -19)
        env.reset(8)
        env.world.obstacles = [Obstacle(40, PLAYER_Y+10+14-.5, 14, 150, 0)]
        _, reward, _, info = env.step(0)
        self.assertEqual(info['passed'], 1)
        self.assertAlmostEqual(reward, 1.5)
        self.assertEqual(env.step(0)[3]['passed'], 0)


class LearningTests(unittest.TestCase):
    def test_replay_learning_target_checkpoint_and_evaluation(self):
        config = Config(batch_size=8)
        agent = Agent(config)
        replay = ReplayBuffer(capacity=16)
        env = Environment()
        state = env.reset(2)
        for i in range(24):
            new, reward, done, info = env.step(i%3)
            replay.add(state, i%3, reward, new, info['terminated'])
            state = env.reset(3) if done else new
        self.assertEqual(replay.size, 16)
        self.assertEqual(replay.sample(8)[0].shape, (8, STATE_SIZE))
        previous = [p.detach().clone() for p in agent.online.parameters()]
        targets = [p.detach().clone() for p in agent.target.parameters()]
        loss = agent.learn(replay)
        self.assertTrue(np.isfinite(loss))
        self.assertTrue(any(not torch.equal(a,b) for a,b in zip(previous,agent.online.parameters())))
        self.assertTrue(all(torch.equal(a,b) for a,b in zip(targets,agent.target.parameters())))
        agent.sync_target()
        self.assertTrue(all(torch.equal(a,b) for a,b in zip(agent.online.parameters(),agent.target.parameters())))
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as folder:
            path = Path(folder)/'model.pth'
            agent.save(path, step=24)
            restored = Agent.load(path, training=True)
            self.assertEqual(restored.act(state), agent.act(state))
            for a,b in zip(agent.online.parameters(),restored.online.parameters()):
                self.assertTrue(torch.equal(a,b))
            self.assertEqual(restored.updates, 1)
            result = evaluate(restored, episodes=3, max_seconds=1)
            self.assertEqual(result['episodes'], 3)
            self.assertEqual(result['capped_games'], 3)
        self.assertEqual(agent.epsilon(0), 1)
        self.assertAlmostEqual(agent.epsilon(1000000), .05)

    def test_playback_matches_headless_and_preserves_human_scores(self):
        import pygame
        from game.game import Game
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as folder:
            path = Path(folder)/'model.pth'
            Agent().save(path)
            controller = Playback(path)
            env = Environment()
            env.reset(123)
            other = Environment()
            other.reset(123)
            for _ in range(100):
                action = controller.agent.act(observe(env.world))
                _, _, done, _ = env.step(action)
                for _ in range(ACTION_FRAMES):
                    controller.advance(other.world, PHYSICS_DT)
                self.assertAlmostEqual(env.world.player_x, other.world.player_x)
                self.assertAlmostEqual(env.world.elapsed, other.world.elapsed)
                self.assertEqual(env.world.alive, other.world.alive)
                np.testing.assert_array_equal(observe(env.world), observe(other.world))
                if done:
                    break
            game = Game(Path(folder)/'human_scores.json')
            game.ai_model_path = path
            game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_i))
            self.assertIsNotNone(game.ai_controller)
            self.assertEqual(game.state, 'playing')
            for _ in range(10):
                game.world.obstacles = [Obstacle(game.world.player_x, PLAYER_Y, 20, 0, 0)]
                game.update(PHYSICS_DT)
                self.assertEqual(game.state, 'over')
                game.draw()
                game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_r))
                self.assertEqual(game.ai_controller.frame, 0)
            self.assertFalse(game.save_path.exists())
            game.state = 'over'
            game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_ESCAPE))
            game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_RETURN))
            self.assertIsNone(game.ai_controller)
            self.assertEqual(game.state, 'playing')
            pygame.quit()


if __name__ == '__main__':
    unittest.main()
