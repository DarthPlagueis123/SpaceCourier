"""Derive website inputs and downloadable archives from existing real artifacts."""
import ast
import csv
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

SITE = Path(__file__).resolve().parents[1]
ROOT = SITE.parent


def snippet(file, name):
    source = (ROOT/file).read_text()
    tree = ast.parse(source)
    parts = name.split('.')
    node = next(n for n in tree.body if getattr(n, 'name', '') == parts[0])
    for part in parts[1:]:
        node = next(n for n in node.body if getattr(n, 'name', '') == part)
    lines = source.splitlines()
    start = min([node.lineno] + [decorator.lineno for decorator in getattr(node, 'decorator_list', [])])
    return {'filename': file, 'code': '\n'.join(lines[start-1:node.end_lineno]),
            'line': start, 'sha256': hashlib.sha256(source.encode()).hexdigest()}


def main():
    generated = SITE/'src/generated'
    downloads = SITE/'public/downloads'
    media = SITE/'public/media'
    for directory in (generated, downloads, media):
        directory.mkdir(parents=True, exist_ok=True)
    metadata = json.loads((ROOT/'models/model_metadata.json').read_text())
    with (ROOT/'data/training_history.csv').open(newline='') as file:
        history = []
        for row in csv.DictReader(file):
            history.append({key: (None if value == '' else value == 'True' if key=='truncated'
                                     else value if key=='checkpoint' else float(value)) for key,value in row.items()})
    clips_file = media/'recordings.json'
    clips = json.loads(clips_file.read_text()) if clips_file.exists() else []
    experiment = {'metadata': metadata, 'history': history,
                  'validation': json.loads((ROOT/'data/validation_history.json').read_text()),
                  'baseline': json.loads((ROOT/'data/random_baseline.json').read_text()),
                  'evaluation': json.loads((ROOT/'data/evaluation_results.json').read_text()),
                  'diagnostics': json.loads((ROOT/'data/behavior_diagnostics.json').read_text()),
                  'recordings': clips,
                  'trace': json.loads((media/'trace-state.json').read_text())}
    (generated/'experiment.json').write_text(json.dumps(experiment, separators=(',', ':')))
    for name, value in experiment.items():
        (generated/f'{name}.json').write_text(json.dumps(value, separators=(',', ':')))
    (generated/'trace-sample.json').write_text(json.dumps([
        {'action':row['action'], 'time':row['time']} for row in experiment['trace'][100:110]
    ], separators=(',', ':')))
    snippets = {key: snippet(file,name) for key,file,name in [
        ('world_reset','game/model.py','World.reset'), ('world_update','game/model.py','World.update'),
        ('score','game/model.py','World.score'), ('difficulty','game/model.py','World.difficulty'),
        ('game_loop','game/game.py','Game.run'), ('game_input','game/game.py','Game.handle_event'),
        ('ship_art','game/art.py','ship_sprite'), ('particles','game/art.py','Particles.burst'),
        ('observation','ai/environment.py','observe'), ('env_reset','ai/environment.py','Environment.reset'),
        ('env_step','ai/environment.py','Environment.step'), ('network','ai/model.py','QNetwork'),
        ('config','ai/agent.py','Config'), ('epsilon','ai/agent.py','Agent.epsilon'),
        ('act','ai/agent.py','Agent.act'), ('learn','ai/agent.py','Agent.learn'),
        ('target','ai/agent.py','Agent.sync_target'), ('replay_add','ai/replay_buffer.py','ReplayBuffer.add'),
        ('replay_sample','ai/replay_buffer.py','ReplayBuffer.sample'), ('playback','ai/playback.py','Playback.advance')
    ]}
    # Focused ranges are exact slices, never rewritten example implementations.
    train_lines = (ROOT/'ai/train.py').read_text().splitlines()
    start = next(i for i,l in enumerate(train_lines) if 'epsilon = agent.epsilon' in l)
    end = next(i for i,l in enumerate(train_lines) if 'agent.sync_target()' in l)
    snippets['training'] = {'filename':'ai/train.py','line':start+1,
                            'code':'\n'.join(train_lines[start:end+1])}
    (generated/'snippets.json').write_text(json.dumps(snippets, indent=2))
    for name in ('title-preview.png','game-preview.png','ai-preview.png'):
        shutil.copy2(ROOT/name, media/name)
    for source,target in [('models/best_model.pth','space-courier-dqn.pth'),
                          ('models/model_metadata.json','model-metadata.json'),
                          ('data/training_history.csv','training-history.csv'),
                          ('data/evaluation_results.json','evaluation-results.json')]:
        shutil.copy2(ROOT/source, downloads/target)
    source_files = [ROOT/'main.py',ROOT/'requirements.txt',ROOT/'requirements-ai.txt',
                    ROOT/'README.md',ROOT/'AI_EXPERIMENT.md']
    for directory in ('game','ai','tests','models','data','results'):
        source_files.extend(p for p in (ROOT/directory).rglob('*') if p.is_file()
                            and '__pycache__' not in p.parts and 'recheck' not in p.parts)
    # Include the website source without its dependencies, build output, or recursive archives.
    source_files.extend(p for p in SITE.rglob('*') if p.is_file()
                        and not any(part in ('node_modules','dist','downloads','__pycache__','.vite')
                                    for part in p.relative_to(SITE).parts)
                        and not p.name.endswith('.tsbuildinfo'))
    with zipfile.ZipFile(downloads/'space-courier-source.zip','w',zipfile.ZIP_DEFLATED) as archive:
        for p in sorted(set(source_files)):
            archive.write(p,Path('pixel-panic')/p.relative_to(ROOT))
    with zipfile.ZipFile(downloads/'space-courier-game.zip','w',zipfile.ZIP_DEFLATED) as archive:
        for p in [ROOT/'main.py',ROOT/'requirements.txt'] + list((ROOT/'game').glob('*.py')):
            archive.write(p,Path('pixel-panic')/p.relative_to(ROOT))
        archive.writestr('pixel-panic/README.md', '# Space Courier\n\nRequires Python 3.10+.\n\nFrom this directory:\n\npython -m pip install -r requirements.txt\npython main.py\n\nMove with A/D or arrows. Enter starts, Escape pauses, R restarts, M toggles audio.\n\nThis archive contains human gameplay. Download the complete source for AI mode.\n')
    manifest = []
    for p in sorted(downloads.iterdir()):
        if p.is_file():
            manifest.append({'filename':p.name,'url':'/downloads/'+p.name,'bytes':p.stat().st_size,
                             'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    (generated/'downloads.json').write_text(json.dumps(manifest,indent=2))
    # Actual folder structure, excluding caches and repeated experiment artifacts.
    structure = ['pixel-panic/']
    for directory in ('game','ai','models','data','results','tests','website'):
        structure.append(f'  {directory}/')
        structure.extend('    '+p.name+('/' if p.is_dir() else '') for p in sorted((ROOT/directory).iterdir())
                         if p.name not in ('__pycache__','node_modules','dist','.vite') and not p.name.endswith('.tsbuildinfo'))
    (generated/'structure.json').write_text(json.dumps(structure,indent=2))
    print(f'Prepared {len(history)} real episodes, {len(snippets)} exact snippets, {len(manifest)} downloads, {len(clips)} recordings.')


if __name__ == '__main__':
    main()
