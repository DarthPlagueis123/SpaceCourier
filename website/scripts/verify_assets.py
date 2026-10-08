"""Check website claims, exact snippets, media, and downloadable artifacts."""
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

SITE = Path(__file__).resolve().parents[1]
ROOT = SITE.parent
generated = SITE/'src/generated'
metadata = json.loads((generated/'metadata.json').read_text(encoding='utf-8'))
assert metadata == json.loads((ROOT/'models/model_metadata.json').read_text(encoding='utf-8'))
history = json.loads((generated/'history.json').read_text(encoding='utf-8'))
with (ROOT/'data/training_history.csv').open(newline='') as file:
    actual = list(csv.DictReader(file))
assert len(history) == len(actual) == metadata['training_episodes']
for item, row in zip(history, actual):
    for key in ('episode','global_step','score','total_reward','moving_average_score','epsilon','steps_survived','survival_seconds'):
        assert item[key] == float(row[key]), (key, item['episode'])
    assert item['loss'] == (float(row['loss']) if row['loss'] else None)
for name, original in [('baseline','random_baseline'),('evaluation','evaluation_results'),('validation','validation_history')]:
    assert json.loads((generated/f'{name}.json').read_text()) == json.loads((ROOT/f'data/{original}.json').read_text())
snippets = json.loads((generated/'snippets.json').read_text())
for snippet in snippets.values():
    lines = (ROOT/snippet['filename']).read_text(encoding='utf-8').splitlines()
    start = snippet['line'] - 1
    assert '\n'.join(lines[start:start+len(snippet['code'].splitlines())]) == snippet['code']
manifest = json.loads((generated/'downloads.json').read_text())
for asset in manifest:
    path = SITE/'public'/asset['url'].lstrip('/')
    assert path.is_file()
    assert path.stat().st_size == asset['bytes']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == asset['sha256']
for filename in ('space-courier-game.zip','space-courier-source.zip'):
    with zipfile.ZipFile(SITE/'public/downloads'/filename) as archive:
        assert archive.testzip() is None
        assert 'pixel-panic/main.py' in archive.namelist()
        assert 'pixel-panic/game/model.py' in archive.namelist()
        if 'source' in filename:
            assert archive.read('pixel-panic/models/best_model.pth') == (ROOT/'models/best_model.pth').read_bytes()
            assert 'pixel-panic/website/src/App.tsx' in archive.namelist()
for name in ('title-preview.png','game-preview.png','ai-preview.png'):
    assert (ROOT/name).read_bytes() == (SITE/'public/media'/name).read_bytes()
recordings = json.loads((generated/'recordings.json').read_text())
assert len(recordings) == 5
for recording in recordings:
    path = SITE/'public'/recording['video'].lstrip('/')
    assert path.is_file() and path.stat().st_size == recording['bytes']
    assert (SITE/'public'/recording['poster'].lstrip('/')).is_file()
    output = subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0',
                                      '-show_entries','stream=codec_name,width,height:format=duration',
                                      '-of','json',str(path)],text=True)
    probe = json.loads(output)
    assert probe['streams'][0]['codec_name']=='h264'
    assert probe['streams'][0]['width']==480 and probe['streams'][0]['height']==640
    assert abs(float(probe['format']['duration']) - recording['survival_seconds'] - (0 if recording['capped'] else 1.5)) < .1
trace = json.loads((generated/'trace.json').read_text())
assert len(trace)==952 and all(len(frame['state'])==32 and len(frame['q_values'])==3 for frame in trace)
assert all(frame['action']==max(range(3),key=lambda i:frame['q_values'][i]) for frame in trace)
for name in ('favicon.png','ship.png','social-preview.png'):
    assert (SITE/'public/media'/name).is_file(), name
print(f'PASS: {len(history)} exact episodes, {len(snippets)} exact code excerpts, {len(manifest)} checksummed downloads, 5 H.264 videos, 952 real inference states.')
