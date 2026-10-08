import argparse
import json
from pathlib import Path
import numpy as np
from .environment import Environment
from .agent import Agent


def evaluate(agent=None, episodes=100, seed_start=100000, max_seconds=180):
    """Paired obstacle seeds; random actions come from an independent RNG."""
    rng = np.random.default_rng(seed_start + 987)
    env = Environment(max_seconds=max_seconds)
    records = []
    for episode in range(episodes):
        seed = seed_start + episode
        state = env.reset(seed)
        done = False
        total_reward = 0
        while not done:
            action = int(rng.integers(3)) if agent is None else agent.act(state)
            state, reward, done, info = env.step(action)
            total_reward += reward
        records.append({'seed': seed, **info, 'total_reward': total_reward})
    scores = np.array([r['score'] for r in records])
    return {'episodes': episodes, 'seed_start': seed_start, 'max_seconds': max_seconds,
            'mean_score': float(scores.mean()), 'median_score': float(np.median(scores)),
            'min_score': int(scores.min()), 'max_score': int(scores.max()),
            'std_score': float(scores.std(ddof=1)) if episodes > 1 else 0,
            'mean_survival_seconds': float(np.mean([r['survival_seconds'] for r in records])),
            'capped_games': sum(r['truncated'] for r in records), 'games': records}


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def main():
    parser = argparse.ArgumentParser(description='Evaluate learned and random policies on matching seeds.')
    parser.add_argument('--model', default='models/best_model.pth')
    parser.add_argument('--episodes', type=int, default=100)
    parser.add_argument('--seed-start', type=int, default=100000)
    parser.add_argument('--output', default='data')
    args = parser.parse_args()
    if args.episodes < 1:
        parser.error('--episodes must be positive')
    agent = Agent.load(args.model)
    baseline = evaluate(episodes=args.episodes, seed_start=args.seed_start, max_seconds=agent.config.max_seconds)
    result = evaluate(agent, args.episodes, args.seed_start, agent.config.max_seconds)
    write_json(Path(args.output)/'random_baseline.json', baseline)
    write_json(Path(args.output)/'evaluation_results.json', result)
    comparison = {'model': str(Path(args.model).resolve()), 'random_mean': baseline['mean_score'],
                  'dqn_mean': result['mean_score'],
                  'mean_improvement_ratio': result['mean_score']/baseline['mean_score']}
    write_json(Path(args.output)/'comparison.json', comparison)
    print(json.dumps(comparison, indent=2))


if __name__ == '__main__':
    main()
