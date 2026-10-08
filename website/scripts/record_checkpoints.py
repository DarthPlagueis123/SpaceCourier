"""Record actual saved policies, without training or changing game files."""
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
from pathlib import Path
import json
import subprocess
import sys
import pygame
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from game.game import Game
from game.art import ship_sprite
from ai.environment import PHYSICS_DT


def main():
    media = Path(__file__).resolve().parents[1] / 'public' / 'media'
    media.mkdir(parents=True, exist_ok=True)
    stages = [('untrained', 'Untrained', 'models/checkpoints/untrained.pth'),
              ('early', 'Early training', 'models/checkpoints/step_0050000.pth'),
              ('middle', 'Mid training', 'models/checkpoints/step_0100000.pth'),
              ('selected', 'Selected model', 'models/best_model.pth'),
              ('last', 'Last checkpoint', 'models/final_model.pth')]
    records = []
    for key, name, model in stages:
        path = ROOT/model
        payload = torch.load(path, map_location='cpu', weights_only=True)
        game = Game(media/'unused-score.json')
        game.ai_model_path = path
        game.world.rng.seed(100002)
        game.watch_ai()
        filename = f'{key}.mp4'
        command = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-vcodec', 'rawvideo',
                   '-pix_fmt', 'rgb24', '-s', '480x640', '-r', '30', '-i', '-', '-an',
                   '-c:v', 'libx264', '-preset', 'fast', '-crf', '25', '-pix_fmt', 'yuv420p',
                   '-movflags', '+faststart', str(media/filename)]
        process = subprocess.Popen(command, stdin=subprocess.PIPE)
        frame = 0
        poster_saved = False
        while game.world.alive and game.world.elapsed < 180:
            game.update(PHYSICS_DT)
            frame += 1
            if frame % 2 == 0:
                game.draw()
                pixels = pygame.surfarray.array3d(game.canvas).transpose(1, 0, 2).copy()
                process.stdin.write(pixels.tobytes())
                if not poster_saved and game.world.elapsed >= 4:
                    pygame.image.save(game.canvas, str(media/f'{key}.png'))
                    poster_saved = True
        # Hold the actual game-over panel briefly; surviving capped runs remain in play.
        if not game.world.alive:
            for _ in range(45):
                game.update(1/30)
                game.draw()
                process.stdin.write(pygame.surfarray.array3d(game.canvas).transpose(1,0,2).copy().tobytes())
        process.stdin.close()
        if process.wait() != 0:
            raise RuntimeError(f'ffmpeg failed for {key}')
        if not poster_saved:
            pygame.image.save(game.canvas, str(media/f'{key}.png'))
        record = {'key': key, 'name': name, 'step': payload['step'], 'completed_episodes': payload['episode'],
                  'seed': 100002, 'score': game.world.score, 'survival_seconds': game.world.elapsed,
                  'capped': game.world.alive, 'video': f'/media/{filename}',
                  'poster': f'/media/{key}.png', 'bytes': (media/filename).stat().st_size}
        records.append(record)
        print(json.dumps(record), flush=True)
        pygame.quit()
    (media/'recordings.json').write_text(json.dumps(records, indent=2))
    # Icons are exported directly from the game's own handmade sprite.
    pygame.init()
    ship = ship_sprite(0)
    pygame.image.save(ship, str(media/'ship.png'))
    pygame.image.save(pygame.transform.scale(ship, (32,32)), str(media/'favicon.png'))
    pygame.quit()


if __name__ == '__main__':
    main()
