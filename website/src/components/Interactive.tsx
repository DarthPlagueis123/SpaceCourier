import { useState } from 'react';
import { model, format, percentage } from '../data';
import traceData from '../generated/trace-sample.json';

export function LearningLoop() {
  const [step, setStep] = useState(0);
  const stages = [
    ['Observe', 'Read the player, boundaries, difficulty, and up to four approaching asteroids.'],
    ['Predict', 'The online neural network produces Q-values for stay, left, and right.'],
    ['Act', 'Choose one action and hold it for six 1/60-second physics ticks.'],
    ['Receive', 'Collect the survival reward, any pass bonuses, and any collision penalty.'],
    ['Remember', 'Store this state, action, reward, next state, and collision flag in replay memory.'],
    ['Learn', 'After warmup, sample past transitions every four decisions and update network weights.'],
  ];
  return <div className="interactive-widget"><div className="widget-heading"><span className="micro">STEP THROUGH A DECISION</span><span>{step + 1} / {stages.length}</span></div><div className="loop-diagram">{stages.map(([label], index) => <button key={label} aria-pressed={index === step} className={index === step ? 'active' : ''} onClick={() => setStep(index)}><span>{String(index+1).padStart(2,'0')}</span>{label}<i aria-hidden="true">→</i></button>)}</div><div className="widget-explanation" aria-live="polite"><strong>{stages[step][0]}</strong><p>{stages[step][1]}</p></div><button className="small-button" onClick={() => setStep((step + 1) % stages.length)}>Next step →</button></div>;
}

export function ActionSpace() {
  const [x,setX] = useState(240);
  const [action,setAction] = useState(0);
  function move(a: number) { setAction(a); setX(previous => Math.max(25,Math.min(455,previous + [0,-29,29][a]))); }
  return <div className="interactive-widget"><div className="widget-heading"><span className="micro">TRY THE THREE ACTIONS</span><span>Illustrated control mapping</span></div><div className="action-lane"><img src="/media/ship.png" alt="Delivery ship" style={{ left: `${x/480*100}%` }} width="48" height="48" /></div><div className="action-buttons">{['Stay','Left','Right'].map((label,i) => <button key={label} aria-pressed={action===i} onClick={() => move(i)}><kbd>{i}</kbd><strong>{label}</strong><span>{['No key','A / ←','D / →'][i]}</span></button>)}</div><p className="small muted">A full action moves 29 pixels (290 pixels/s × 0.1 s), clamped to x=25…455. This is a control illustration, not browser gameplay.</p></div>;
}

export function BellmanDemo() {
  const [reward,setReward] = useState(1);
  const [gamma,setGamma] = useState(.99);
  const [future,setFuture] = useState(12);
  const [terminal,setTerminal] = useState(false);
  const target = reward + (terminal ? 0 : gamma*future);
  return <div className="interactive-widget"><div className="widget-heading"><span className="micro">THE BELLMAN TARGET, UNPACKED</span><span>Illustrative values</span></div><div className="bellman-formula"><span>{reward.toFixed(1)}</span><small>+</small><span>{gamma.toFixed(2)}</span><small>×</small><span>{terminal ? '0' : future.toFixed(1)}</span><small>=</small><strong>{target.toFixed(2)}</strong></div><div className="slider-grid"><label>Immediate reward r <input type="range" min="-20" max="2" step=".5" value={reward} onChange={e=>setReward(Number(e.target.value))} /></label><label>Future discount γ <input type="range" min="0" max="1" step=".01" value={gamma} onChange={e=>setGamma(Number(e.target.value))} /></label><label>Next action value <input type="range" min="0" max="30" step=".5" value={future} onChange={e=>setFuture(Number(e.target.value))} /></label></div><label className="checkbox-label"><input type="checkbox" checked={terminal} onChange={e=>setTerminal(e.target.checked)} /> The ship collided (terminal transition)</label><p className="small">{terminal ? 'A collision ends the episode. There is no future reward to bootstrap.' : 'The target combines what happened now with discounted expected reward later.'} These sliders explain the arithmetic; they are not recorded network predictions.</p></div>;
}

export function ArchitectureDiagram() {
  return <div className="interactive-widget"><div className="widget-heading"><span className="micro">THE ACTUAL NETWORK</span><span>32 → 128 → 128 → 3</span></div><div className="architecture-diagram">{[{title:'State',number:'32',label:'numerical inputs'}, {title:'Hidden layer',number:'128',label:'Linear + ReLU'}, {title:'Hidden layer',number:'128',label:'Linear + ReLU'}, {title:'Actions',number:'3',label:'stay · left · right'}].map((layer,i) => <div className="architecture-layer" key={i}><span>{layer.title}</span><div className="neuron-symbol" aria-hidden="true">{Array.from({length:i===3?3:9},(_,j)=><i key={j} />)}</div><strong>{layer.number}</strong><small>{layer.label}</small>{i<3&&<b aria-hidden="true">→</b>}</div>)}</div><p className="small muted">The dots represent layers, not all individual neurons or live activations. The final layer predicts three action values, not probabilities.</p></div>;
}

export function ReplayDemo() {
  const [count,setCount] = useState(5);
  const [sampled,setSampled] = useState<number[]>([]);
  const samples = traceData;
  function sample() {
    const indices = Array.from({length:count},(_,i)=>i);
    for(let i=indices.length-1;i>0;i--) { const j=Math.floor(Math.random()*(i+1)); [indices[i],indices[j]]=[indices[j],indices[i]]; }
    setSampled(indices.slice(0,3));
  }
  return <div className="interactive-widget"><div className="widget-heading"><span className="micro">A TINY VIEW OF REPLAY MEMORY</span><span>{count} / 10 illustrative slots</span></div><div className="replay-slots">{Array.from({length:10},(_,i)=><div className={i<count?(sampled.includes(i)?'sampled':'filled'):'empty'} key={i}><span>#{i+1}</span><strong>{i<count?['STAY','LEFT','RIGHT'][samples[i].action]:'—'}</strong><small>{sampled.includes(i)?'SAMPLED':i<count?`${samples[i].time.toFixed(1)} s`:'EMPTY'}</small></div>)}</div><div className="widget-buttons"><button className="small-button" disabled={count===10} onClick={()=>{setCount(count+1);setSampled([]);}}>Store experience</button><button className="small-button" onClick={sample}>Sample 3</button><button className="text-button" onClick={()=>{setCount(5);setSampled([]);}}>Reset</button></div><p className="small muted">Tiles use actions from the actual trace. This small illustration samples three entries; real training stores up to {format(model.config.replay_capacity)} full transitions and samples {model.config.batch_size} at a time.</p><span role="status" className="sr-only">{sampled.length ? `Sampled entries ${sampled.map(i=>i+1).join(', ')}` : ''}</span></div>;
}

export function EpsilonMeter() {
  const [step,setStep] = useState(0);
  const c = model.config;
  const epsilon = c.epsilon_start+(c.epsilon_end-c.epsilon_start)*Math.min(1,step/c.epsilon_decay_steps);
  return <div className="interactive-widget"><div className="widget-heading"><span className="micro">EXPLORE OR EXPLOIT?</span><span>{format(step)} decisions</span></div><div className="epsilon-labels"><strong>{percentage(epsilon)} random</strong><strong>{percentage(1-epsilon)} network</strong></div><div className="epsilon-bar" role="img" aria-label={`${percentage(epsilon)} probability of a random action`}><i style={{width:`${epsilon*100}%`}} /></div><label className="range-label">Training decision<input type="range" min="0" max={model.training_steps} step="1000" value={step} onChange={e=>setStep(Number(e.target.value))} /></label><p className="small">Epsilon falls linearly from 1.0 to 0.05 over 120,000 decisions. It stays at 0.05 afterward. Evaluation and playback use epsilon=0.</p><p className="small muted">“Random” and “network” describe how an action is selected. A random action may coincidentally match the network’s choice.</p></div>;
}

export function HyperparameterTable() {
  const c=model.config;
  const entries = [['Network','32 → 128 → 128 → 3'],['Algorithm','Double DQN'],['Learning rate',String(c.learning_rate)],['Gamma',String(c.gamma)],['Batch size',format(c.batch_size)],['Replay capacity',format(c.replay_capacity)],['Warmup decisions',format(c.warmup_steps)],['Train every',`${c.train_every} decisions`],['Target sync every',`${format(c.target_every)} decisions`],['Epsilon start / floor',`${c.epsilon_start} / ${c.epsilon_end}`],['Linear decay duration',`${format(c.epsilon_decay_steps)} decisions`],['Physics / action cadence','60 Hz / 10 Hz'],['Training seed',String(c.seed)],['Completed training episodes',format(model.training_episodes)],['Total training decisions',format(model.training_steps)],['Selected checkpoint',`${format(model.best_checkpoint)} decisions`],['Experiment time limit',`${c.max_seconds} s (truncation, not death)`]];
  return <div className="table-scroll"><table><caption>Values read from the saved model metadata</caption><thead><tr><th scope="col">Setting</th><th scope="col">Actual value</th></tr></thead><tbody>{entries.map(([key,value])=><tr key={key}><th scope="row">{key}</th><td>{value}</td></tr>)}</tbody></table></div>;
}
