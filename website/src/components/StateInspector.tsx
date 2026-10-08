import { useState, useEffect } from 'react';
import { model } from '../data';
import type traceSchema from '../generated/trace.json';
type TraceFrame = (typeof traceSchema)[number];

export default function StateInspector() {
  const [traceData, setTraceData] = useState<TraceFrame[] | null>(null);
  const [error, setError] = useState(false);
  useEffect(() => {
    const controller = new AbortController();
    fetch('/media/trace-state.json', { signal: controller.signal })
      .then(response => { if (!response.ok) throw new Error('Trace unavailable'); return response.json(); })
      .then((data: TraceFrame[]) => setTraceData(data))
      .catch(reason => { if (reason.name !== 'AbortError') setError(true); });
    return () => controller.abort();
  }, []);
  const [index, setIndex] = useState(100);
  if (!traceData) return <div className="interactive-widget" role="status">{error ? 'The recorded trace could not load. Refresh to try again.' : 'Loading the actual recorded state trace…'}</div>;
  const frame = traceData[index];
  const nearby = [...frame.obstacles].filter(o => o.y - o.radius <= 575).sort((a,b) => Math.abs(565-a.y) - Math.abs(565-b.y)).slice(0,4);
  const values = frame.state;
  return <div className="interactive-widget state-widget"><div className="widget-heading"><span className="micro">REAL MODEL TRACE / SEED 100002</span><span>{frame.time.toFixed(1)} s</span></div><div className="state-inspector-grid"><svg viewBox="0 60 480 550" role="img" aria-label={`Recorded state at ${frame.time.toFixed(1)} seconds: player x ${Math.round(frame.player_x)}, ${nearby.length} observed asteroids`}><rect x="0" y="60" width="480" height="550" fill="#0c1020" /><line x1="25" y1="70" x2="25" y2="600" stroke="#536b79" strokeDasharray="5 5" /><line x1="455" y1="70" x2="455" y2="600" stroke="#536b79" strokeDasharray="5 5" /><text x="35" y="91" fill="#bfcbd1" fontSize="14">x=25</text><text x="389" y="91" fill="#bfcbd1" fontSize="14">x=455</text>{frame.obstacles.map((rock,i) => <circle key={i} cx={rock.x} cy={rock.y} r={rock.radius} fill="#b18f7b" stroke="#e8c593" strokeWidth="3" />)}{nearby.map((rock,i) => <g key={i}><line x1={rock.x} y1={rock.y} x2={frame.player_x} y2="565" stroke="#9fd5c8" strokeDasharray="4 7" opacity=".5" /><text x={Math.max(40,Math.min(375,rock.x+rock.radius+5))} y={Math.max(115,rock.y)} fill="#c0eadb" fontSize="16">slot {i+1}</text></g>)}<image href="/media/ship.png" x={frame.player_x-24} y="541" width="48" height="48" /><text x="35" y="605" fill="#e5c688" fontSize="16">player x = {frame.player_x.toFixed(0)}</text></svg><div className="state-readout"><strong>32 numbers, not a screenshot</strong><p className="small">Scrub through the actual final-model run. The picture labels current positions; the network receives the numbers below.</p><label htmlFor="state-frame">Recorded time <span>{frame.time.toFixed(1)} s</span></label><input id="state-frame" type="range" min="0" max={traceData.length-1} value={index} onChange={event => setIndex(Number(event.target.value))} /><p className="small">Chosen action: <strong>{['STAY','LEFT','RIGHT'][frame.action]}</strong></p><div className="q-readout">{frame.q_values.map((value,i)=><span key={i}><small>Q({['STAY','LEFT','RIGHT'][i]})</small><strong>{value.toFixed(2)}</strong></span>)}</div><p className="small muted">Asteroids are sorted by current vertical gap. Entirely passed rocks are excluded. No future positions or spawn schedule are exposed.</p><details><summary>Inspect all 32 exact inputs</summary><div className="vector-list">{values.map((value,i) => <div key={i}><code>{model.state_inputs[i]}</code><strong>{value.toFixed(3)}</strong></div>)}</div></details></div></div></div>;
}

