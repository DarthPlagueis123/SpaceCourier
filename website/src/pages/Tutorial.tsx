import { useState, lazy, Suspense, type ReactNode } from 'react';
import { Link, useParams } from 'react-router-dom';
import { chapters } from '../data';
import { lessons, type Widget } from '../content/lessons';
import { ChapterNavigation } from '../components/Navigation';
import { CodeBlock, Eyebrow, TutorialSection, Note, GameScreenshot, Arrow } from '../components/ui';
import { ActionSpace, ArchitectureDiagram, BellmanDemo, EpsilonMeter, HyperparameterTable, LearningLoop, ReplayDemo } from '../components/Interactive';
import SetupGuide from '../components/SetupGuide';
import CheckpointPlayer from '../components/CheckpointPlayer';
import structure from '../generated/structure.json';

const StateInspector = lazy(() => import('../components/StateInspector'));

function widgetComponent(widget:Widget):ReactNode {
  switch(widget) {
    case 'loop': return <LearningLoop />;
    case 'state': return <Suspense fallback={<p>Loading the actual recorded state trace...</p>}><StateInspector /></Suspense>;
    case 'actions': return <ActionSpace />;
    case 'bellman': return <BellmanDemo />;
    case 'network': return <ArchitectureDiagram />;
    case 'replay': return <ReplayDemo />;
    case 'epsilon': return <EpsilonMeter />;
    case 'hyperparameters': return <HyperparameterTable />;
    case 'video': return <CheckpointPlayer />;
    case 'setup': return <SetupGuide />;
    case 'structure': return <CodeBlock code={structure.join('\n')} filename="Actual project structure" language="plain" />;
    case 'results': return <Link className="button" to="/results">Explore the interactive results <Arrow /></Link>;
  }
}

export default function Tutorial({fixedSlug}:{fixedSlug?:string}) {
  const params=useParams();
  const slug=fixedSlug??params.slug??'game';
  const chapter=chapters.find(c=>c.slug===slug);
  const lesson=lessons[slug];
  const [completed,setCompleted]=useState<string[]>(()=>{try{return JSON.parse(localStorage.getItem('space-courier-progress')??'[]').filter((s:string)=>chapters.some(c=>c.slug===s));}catch{return [];}});
  function toggle(value:string) {
    setCompleted(previous=>{const next=previous.includes(value)?previous.filter(s=>s!==value):[...previous,value];try{localStorage.setItem('space-courier-progress',JSON.stringify(next));}catch{/* Reading remains available if storage is disabled. */}return next;});
  }
  if(!chapter||!lesson) return <div className="container not-found"><h1>That chapter isn’t on this route.</h1><Link className="button" to="/learn/game">Start at chapter one</Link></div>;
  const index=chapters.findIndex(c=>c.slug===slug);
  return <div className="container tutorial-layout"><ChapterNavigation slug={slug} completed={completed} onToggle={toggle} /><article className="lesson"><header className="lesson-heading"><Eyebrow>CHAPTER {String(index+1).padStart(2,'0')} / {chapters.length} <span>· {chapter.time} estimated reading</span></Eyebrow><h1>{chapter.title}</h1><p>{lesson.intro}</p><nav className="lesson-toc" aria-label="On this page">{lesson.sections.map(section=><a href={`#${section.id}`} key={section.id}>{section.title}</a>)}</nav></header>{lesson.sections.map(section=><TutorialSection key={section.id} id={section.id} title={section.title}>{section.paragraphs.map((p,i)=><p key={i}>{p}</p>)}{section.bullets&&<ul>{section.bullets.map(bullet=><li key={bullet}>{bullet}</li>)}</ul>}{section.image&&<GameScreenshot {...section.image} />}{section.widget&&widgetComponent(section.widget)}{section.snippet&&<CodeBlock snippet={section.snippet} />}{section.note&&<Note title={section.note.title}><p>{section.note.body}</p></Note>}</TutorialSection>)}<div className="lesson-takeaway"><span className="micro">TAKE THIS WITH YOU</span><p>{lesson.takeaway}</p><button className="small-button" onClick={()=>toggle(slug)}>{completed.includes(slug)?'✓ Chapter completed · undo':'Mark this chapter complete'}</button></div><nav className="lesson-pagination" aria-label="Chapter navigation">{index>0?<Link to={`/learn/${chapters[index-1].slug}`}><span className="micro">PREVIOUS CHAPTER</span><strong>← {chapters[index-1].short}</strong></Link>:<Link to="/"><span className="micro">BACK TO</span><strong>← Mission control</strong></Link>}{index<chapters.length-1?<Link to={`/learn/${chapters[index+1].slug}`}><span className="micro">NEXT CHAPTER</span><strong>{chapters[index+1].short} →</strong></Link>:<Link to="/train"><span className="micro">YOUR NEXT MISSION</span><strong>Train it yourself →</strong></Link>}</nav></article></div>;
}
