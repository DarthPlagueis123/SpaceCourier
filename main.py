import argparse
from pathlib import Path
from game.game import Game

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Play Space Courier or watch a learned DQN.')
    parser.add_argument('--ai', action='store_true', help='Start AI playback immediately.')
    parser.add_argument('--model', type=Path, default=Path(__file__).resolve().parent/'models/best_model.pth')
    parser.add_argument('--debug', action='store_true', help='Show AI action and Q-values.')
    parser.add_argument('--seed', type=int, help='Seed the obstacle generator for repeatable playback.')
    args = parser.parse_args()
    game = Game()
    game.ai_model_path = args.model
    game.ai_debug = args.debug
    if args.seed is not None:
        game.world.rng.seed(args.seed)
    if args.ai:
        game.watch_ai()
    game.run()
