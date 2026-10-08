import { useEffect, useState } from 'react';
import { Link, NavLink, useLocation } from 'react-router-dom';
import { chapters, navLinks } from '../data';
import { Arrow } from './ui';

export function Navigation() {
  const [open, setOpen] = useState(false);
  const location = useLocation();
  useEffect(() => setOpen(false), [location.pathname]);
  return <header className="site-header"><div className="nav-inner"><Link to="/" className="brand" aria-label="Space Courier home"><img src="/media/ship.png" alt="" width="40" height="40" /><span>SPACE COURIER<small>A REINFORCEMENT LEARNING FIELD GUIDE</small></span></Link><button className="menu-toggle" aria-expanded={open} aria-controls="main-nav" onClick={() => setOpen(!open)}>{open ? 'Close' : 'Menu'}<span aria-hidden="true">{open ? '×' : '☰'}</span></button><nav id="main-nav" className={open ? 'main-nav is-open' : 'main-nav'} aria-label="Main navigation">{navLinks.map(link => <NavLink key={link.to} to={link.to}>{link.label}</NavLink>)}<Link to="/train" className="nav-cta">Try it yourself <Arrow /></Link></nav></div></header>;
}

export function ChapterNavigation({ slug, completed, onToggle }: { slug: string; completed: string[]; onToggle: (slug: string) => void }) {
  const [expanded, setExpanded] = useState(false);
  const index = chapters.findIndex(chapter => chapter.slug === slug);
  return <aside className="chapter-nav"><div className="chapter-nav-heading"><span className="micro">YOUR LEARNING ROUTE</span><button className="chapter-toggle" aria-expanded={expanded} aria-controls="chapter-list" onClick={() => setExpanded(!expanded)}>{expanded ? 'Hide chapters' : 'All chapters'}</button></div><div className="chapter-progress"><span>{completed.length} / {chapters.length} completed</span><progress value={completed.length} max={chapters.length} aria-label="Completed chapters" /></div><nav id="chapter-list" className={expanded ? 'chapter-list expanded' : 'chapter-list'} aria-label="Tutorial chapters">{chapters.map((chapter, i) => <div key={chapter.slug}>{(i === 0 || chapter.group !== chapters[i - 1].group) && <h2 className="chapter-group">{chapter.group}</h2>}<NavLink to={`/learn/${chapter.slug}`} className={chapter.slug === slug ? 'chapter-link current' : 'chapter-link'}><span className="chapter-number">{completed.includes(chapter.slug) ? '✓' : String(i+1).padStart(2,'0')}</span>{chapter.short}</NavLink></div>)}</nav><button className="complete-button" onClick={() => onToggle(slug)}>{completed.includes(slug) ? '✓ Completed · undo' : 'Mark chapter complete'}</button><p className="small muted">Progress stays in this browser.</p><span className="sr-only">Chapter {index+1} of {chapters.length}</span></aside>;
}

export function Footer() {
  return <footer className="site-footer"><div className="container footer-inner"><div><Link className="footer-brand" to="/">SPACE COURIER<span>FROM PIXELS TO POLICY.</span></Link><p>A small game. An honest experiment. A guide you can reproduce.</p></div><nav aria-label="Footer navigation"><Link to="/about">Project details</Link><Link to="/download">Source & data</Link><a href="https://docs.pytorch.org/tutorials/intermediate/reinforcement_q_learning.html" target="_blank" rel="noreferrer">PyTorch DQN reference ↗</a></nav><span className="micro">BUILT WITH PYTHON, PYTORCH & CURIOSITY</span></div></footer>;
}
