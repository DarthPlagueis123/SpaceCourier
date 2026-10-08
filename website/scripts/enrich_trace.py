"""Reproduce the existing trace to record exact observations and Q-values."""
from pathlib import Path
import json
import sys
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from ai.environment import Environment
from ai.agent import Agent

agent = Agent.load(ROOT/'models/best_model.pth')
env = Environment()
state = env.reset(100002)
original = json.loads((ROOT/'data/playback_trace.json').read_text())
records = []
for expected in original:
    with torch.no_grad():
        q = agent.online(torch.from_numpy(state)).tolist()
    action = int(torch.tensor(q).argmax())
    assert action == expected['action']
    assert env.world.elapsed == expected['time']
    assert env.world.player_x == expected['player_x']
    assert [{'x':o.x,'y':o.y,'radius':o.radius} for o in env.world.obstacles] == expected['obstacles']
    records.append({**expected, 'obstacles':[{'x':o.x,'y':o.y,'radius':o.radius,'speed':o.speed} for o in env.world.obstacles],
                    'state':state.tolist(), 'q_values':q})
    state, _, done, _ = env.step(action)
target = Path(__file__).resolve().parents[1]/'public/media/trace-state.json'
target.write_text(json.dumps(records,separators=(',',':')))
print(f'Reproduced all {len(records)} original decisions exactly; saved actual inputs and Q-values.')
