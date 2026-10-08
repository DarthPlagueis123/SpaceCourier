import { useMemo, useState } from 'react';
import historyData from '../generated/history.json';
import { format } from '../data';

type Field = 'score' | 'moving_average_score' | 'loss' | 'epsilon' | 'survival_seconds' | 'total_reward';
const fields: { field: Field; label: string; unit: string }[] = [
  { field:'score',label:'Episode score',unit:'points' },
  { field:'moving_average_score',label:'Moving average',unit:'points / trailing 50 episodes' },
  { field:'loss',label:'Training loss',unit:'mean Huber loss per episode' },
  { field:'epsilon',label:'Epsilon',unit:'random-action probability' },
  { field:'survival_seconds',label:'Survival time',unit:'seconds' },
  { field:'total_reward',label:'Total reward',unit:'reward units' },
];

export default function TrainingChart() {
  const [field,setField] = useState<Field>('moving_average_score');
  const [end,setEnd] = useState(historyData.length);
  const [windowSize,setWindowSize] = useState(0);
  const [selected,setSelected] = useState(historyData.length-1);
  const descriptor=fields.find(f=>f.field===field)!;
  const data=useMemo(()=>historyData.slice(windowSize ? Math.max(0,end-windowSize):0,end),[end,windowSize]);
  const values=data.map(r=>r[field]).filter((v):v is number=>typeof v==='number');
  const max=field==='epsilon'?1:Math.max(...values,.01)*1.06;
  const min=Math.min(0,...values);
  const left=68,right=910,top=24,bottom=266;
  const x=(i:number)=>left+(right-left)*i/Math.max(1,data.length-1);
  const y=(v:number)=>bottom-(v-min)/(max-min)*(bottom-top);
  const points=data.flatMap((row,i)=>typeof row[field]==='number'?[`${x(i)},${y(row[field] as number)}`]:[]).join(' ');
  const local=Math.max(0,Math.min(data.length-1,selected-(end-data.length)));
  const row=data[local];
  const current=row[field];
  function move(event: React.PointerEvent<SVGSVGElement>) {
    const rect=event.currentTarget.getBoundingClientRect();
    const mouse=(event.clientX-rect.left)/rect.width*940;
    const i=Math.round(Math.max(0,Math.min(1,(mouse-left)/(right-left)))*(data.length-1));
    setSelected(end-data.length+i);
  }
  return <section className="chart-card" aria-labelledby="chart-title"><div className="chart-heading"><div><span className="micro">ACTUAL TRAINING HISTORY</span><h2 id="chart-title">{descriptor.label}</h2></div><span className="data-badge">{format(historyData.length)} REAL EPISODES</span></div><div className="chart-tabs" aria-label="Chart metric">{fields.map(option=><button key={option.field} className={field===option.field?'active':''} aria-pressed={field===option.field} onClick={()=>setField(option.field)}>{option.label}</button>)}</div><div className="chart-controls"><label>View <select value={windowSize} onChange={e=>setWindowSize(Number(e.target.value))}><option value="0">All episodes to selected end</option><option value="100">100-episode window</option><option value="50">50-episode window</option></select></label><label className="range-label">End episode: {end}<input type="range" min="10" max={historyData.length} value={end} onChange={e=>{setEnd(Number(e.target.value));setSelected(Number(e.target.value)-1);}} /></label></div><div className="chart-svg-wrap"><svg viewBox="0 0 940 320" role="img" tabIndex={0} aria-label={`${descriptor.label} over ${data.length} real training episodes. Use left and right arrow keys to inspect values.`} onPointerMove={move} onKeyDown={event=>{if(event.key==='ArrowRight'||event.key==='ArrowLeft'){event.preventDefault();setSelected(Math.max(end-data.length,Math.min(end-1,selected+(event.key==='ArrowRight'?1:-1))));}}}>
      {[0,.25,.5,.75,1].map(fraction=><g key={fraction}><line x1={left} x2={right} y1={top+fraction*(bottom-top)} y2={top+fraction*(bottom-top)} stroke="#dcded6" /><text x={left-12} y={top+fraction*(bottom-top)+5} textAnchor="end" fill="#66736f" fontSize="13">{format(max-fraction*(max-min),field==='loss'||field==='epsilon'?2:0)}</text></g>)}
      <polyline points={points} fill="none" stroke={field==='score'?'#c27255':'#286560'} strokeWidth={field==='score'?1.2:2.2} strokeLinejoin="round" />
      <line x1={x(local)} x2={x(local)} y1={top} y2={bottom} stroke="#a86b54" strokeDasharray="4 5" />
      {typeof current==='number'&&<circle cx={x(local)} cy={y(current)} r="4.5" fill="#cb7658" stroke="#f8f4ec" strokeWidth="2" />}
      {[0,.25,.5,.75,1].map(fraction=><text key={fraction} x={left+fraction*(right-left)} y="290" textAnchor="middle" fill="#66736f" fontSize="13">{format(data[Math.round(fraction*(data.length-1))].episode)}</text>)}
      <text x="490" y="315" textAnchor="middle" fill="#66736f" fontSize="13">Completed training episode</text>
    </svg></div><div className="chart-readout" aria-live="polite"><span>Episode <strong>{format(row.episode)}</strong></span><span>{descriptor.label}: <strong>{current===null?'Warmup: no update':format(current as number,field==='epsilon'||field==='loss'?4:1)}</strong></span><span>Decision <strong>{format(row.global_step)}</strong></span></div><p className="small muted">{descriptor.unit}. Hover, touch, or focus the plot and use arrow keys. Warmup losses are missing because no training update happened. Training uses exploration; this curve is not greedy evaluation.</p><details><summary>Inspect the selected episode’s data</summary><dl className="episode-data">{Object.entries(row).map(([key,value])=><div key={key}><dt>{key.replaceAll('_',' ')}</dt><dd>{value===null?'Not recorded / no update':String(value)}</dd></div>)}</dl></details></section>;
}
