import argparse
import csv
import json
import time
from collections import deque
from dataclasses import asdict
from pathlib import Path
import numpy as np
import torch
from .agent import Agent, Config
from .environment import Environment, STATE_INPUTS, ACTION_FRAMES
from .replay_buffer import ReplayBuffer
from .evaluate import evaluate, write_json
from .plots import plot_history


def train(args):
    root = Path(args.output)
    if (root/'data/training_history.csv').exists():
        raise FileExistsError(f'{root} already has training history. Choose a new --output to preserve it.')
    for directory in ('models/checkpoints', 'data', 'results'):
        (root/directory).mkdir(parents=True, exist_ok=True)
    config = Config(seed=args.seed, epsilon_decay_steps=args.decay_steps)
    agent = Agent(config)
    env = Environment(max_seconds=config.max_seconds)
    renderer = None
    if args.render:
        import pygame
        from game.game import Game
        renderer = Game(root/'data/debug_scores.json')
        renderer.audio.enabled = False
        renderer.world = env.world
        renderer.state = 'playing'
    replay = ReplayBuffer(config.replay_capacity, config.seed)
    seeds = np.random.default_rng(config.seed + 1)
    write_json(root/'data/run_config.json', {**asdict(config), 'requested_steps': args.steps,
               'torch_version': str(torch.__version__), 'device': 'cpu',
               'validation_seed_start': 200000, 'test_seed_start': 100000})
    baseline = evaluate(episodes=100, max_seconds=config.max_seconds)
    write_json(root/'data/random_baseline.json', baseline)
    print(f'Random baseline (100 games): {baseline["mean_score"]:.1f}', flush=True)
    agent.save(root/'models/checkpoints/untrained.pth', episode=0, step=0)
    state = env.reset(int(seeds.integers(0, 90000)))
    episode = 0
    reward_sum = 0
    episode_checkpoint = ''
    losses = []
    recent = deque(maxlen=50)
    validations = []
    best_validation = -float('inf')
    started = time.perf_counter()
    fields = ('episode', 'global_step', 'score', 'total_reward', 'moving_average_score',
              'loss', 'epsilon', 'steps_survived', 'survival_seconds', 'truncated', 'checkpoint')
    interrupted = False
    with (root/'data/training_history.csv').open('w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        try:
            for step in range(1, args.steps + 1):
                epsilon = agent.epsilon(step-1)
                action = agent.act(state, epsilon)
                next_state, reward, done, info = env.step(action)
                if renderer is not None:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            raise KeyboardInterrupt
                    renderer.time = env.world.elapsed
                    renderer.direction = (0, -1, 1)[action]
                    renderer.draw()
                replay.add(state, action, reward, next_state, info['terminated'])
                reward_sum += reward
                state = next_state
                if replay.size >= config.warmup_steps and step % config.train_every == 0:
                    losses.append(agent.learn(replay))
                if step % config.target_every == 0:
                    agent.sync_target()
                if step % args.validate_every == 0 or step == args.steps:
                    checkpoint = f'models/checkpoints/step_{step:07}.pth'
                    episode_checkpoint = checkpoint
                    agent.save(root/checkpoint, episode=episode, step=step)
                    validation = evaluate(agent, episodes=20, seed_start=200000, max_seconds=config.max_seconds)
                    validations.append({'step': step, 'completed_episodes': episode,
                                        'mean_score': validation['mean_score'],
                                        'median_score': validation['median_score']})
                    write_json(root/'data/validation_history.json', validations)
                    if validation['mean_score'] > best_validation:
                        best_validation = validation['mean_score']
                        agent.save(root/'models/best_model.pth', episode=episode, step=step,
                                   validation_mean=best_validation)
                    print(f'Step {step:,} | episodes {episode} | epsilon {epsilon:.3f} | '
                          f'train avg {np.mean(recent) if recent else 0:.0f} | '
                          f'validation {validation["mean_score"]:.0f} | '
                          f'{step/(time.perf_counter()-started):.0f} steps/s', flush=True)
                if done:
                    episode += 1
                    recent.append(info['score'])
                    writer.writerow({'episode': episode, 'global_step': step, 'score': info['score'],
                                     'total_reward': reward_sum, 'moving_average_score': np.mean(recent),
                                     'loss': np.mean(losses) if losses else '', 'epsilon': epsilon,
                                     'steps_survived': info['steps'], 'survival_seconds': info['survival_seconds'],
                                     'truncated': info['truncated'], 'checkpoint': episode_checkpoint})
                    file.flush()
                    reward_sum = 0
                    episode_checkpoint = ''
                    losses = []
                    state = env.reset(int(seeds.integers(0, 90000)))
        except KeyboardInterrupt:
            interrupted = True
            print('Interrupted: saving current model and completed episode history.', flush=True)
    agent.save(root/'models/final_model.pth', episode=episode, step=step)
    if renderer is not None:
        pygame.quit()
    if not (root/'models/best_model.pth').exists():
        agent.save(root/'models/best_model.pth', episode=episode, step=step)
    best = Agent.load(root/'models/best_model.pth')
    final = evaluate(best, episodes=100, max_seconds=config.max_seconds)
    write_json(root/'data/evaluation_results.json', final)
    comparison = {'random_mean': baseline['mean_score'], 'dqn_mean': final['mean_score'],
                  'mean_improvement_ratio': final['mean_score']/baseline['mean_score']}
    write_json(root/'data/comparison.json', comparison)
    metadata = {'architecture': [32, 128, 128, 3], 'activation': 'ReLU', 'algorithm': 'Double DQN',
                'state_inputs': STATE_INPUTS, 'missing_obstacles': 'All seven values are zero.',
                'actions': {'0': 'stay', '1': 'left', '2': 'right'},
                'physics_hz': 60, 'action_frames': ACTION_FRAMES, 'config': asdict(config),
                'reward': {'per_surviving_action': 1, 'passed_obstacle': .5, 'collision': -20},
                'training_episodes': episode, 'training_steps': step, 'interrupted': interrupted,
                'wall_seconds': time.perf_counter()-started,
                'best_checkpoint': torch.load(root/'models/best_model.pth', weights_only=True)['step'],
                'random_baseline': {k:v for k,v in baseline.items() if k != 'games'},
                'evaluation': {k:v for k,v in final.items() if k != 'games'}, 'comparison': comparison}
    write_json(root/'models/model_metadata.json', metadata)
    plot_history(root/'data/training_history.csv', root/'results')
    print(json.dumps(comparison, indent=2), flush=True)


def main():
    parser = argparse.ArgumentParser(description='Train genuine DQN from experience, headlessly.')
    parser.add_argument('--steps', type=int, default=250000)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--decay-steps', type=int, default=120000)
    parser.add_argument('--validate-every', type=int, default=25000)
    parser.add_argument('--output', default='.')
    parser.add_argument('--render', action='store_true', help='Render training for debugging; no FPS cap.')
    args = parser.parse_args()
    if min(args.steps, args.decay_steps, args.validate_every) < 1:
        parser.error('Step arguments must be positive.')
    train(args)


if __name__ == '__main__':
    main()
