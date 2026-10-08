import { lazy, Suspense, useEffect } from 'react';
import { BrowserRouter, Link, Route, Routes, useLocation } from 'react-router-dom';
import { Navigation, Footer } from './components/Navigation';
import Home from './pages/Home';
import { chapters } from './data';

const Tutorial = lazy(() => import('./pages/Tutorial'));
const Results = lazy(() => import('./pages/Results'));
const Watch = lazy(() => import('./pages/Watch'));
const Download = lazy(() => import('./pages/Download'));
const Train = lazy(() => import('./pages/Train'));
const About = lazy(() => import('./pages/About'));

function RouteEffects() {
  const location = useLocation();
  useEffect(() => {
    const slug = location.pathname.split('/')[2];
    const chapter = chapters.find(c => c.slug === slug);
    const label = chapter?.title ?? ({ '/results': 'Real results', '/watch': 'Watch the AI', '/download': 'Downloads', '/train': 'Train it yourself', '/about': 'Project details' } as Record<string, string>)[location.pathname];
    document.title = label ? `${label} — Space Courier` : 'Teaching an AI to Play Space Courier';
    const description = chapter
      ? `Learn ${chapter.title.toLowerCase()} through the actual Space Courier game and PyTorch Double DQN, with real code and measured evidence.`
      : ({ '/results': 'Explore 1,059 real training episodes and the 100-game evaluation of Space Courier’s learned Double DQN.', '/watch': 'Watch five real saved policies play Space Courier on the same obstacle seed, from untrained to selected and last checkpoints.', '/download': 'Download the original Space Courier game, complete source, trained PyTorch model, real training CSV, and model metadata.', '/train': 'Reproduce the Space Courier experiment with the verified Windows setup, actual Python commands, and saved project artifacts.', '/about': 'Inspect the actual architecture, evidence, limitations, and source behind Space Courier’s reinforcement learning experiment.' } as Record<string, string>)[location.pathname]
        ?? 'Teach an AI to play Space Courier. Follow a real pixel-art game, PyTorch Double DQN, and measured training results from start to finish.';
    document.querySelector('meta[name="description"]')?.setAttribute('content', description);
    document.querySelector('meta[property="og:title"]')?.setAttribute('content', document.title);
    document.querySelector('meta[property="og:description"]')?.setAttribute('content', description);
    if (location.hash) {
      const timer = window.setTimeout(() => document.getElementById(location.hash.slice(1))?.scrollIntoView(), 250);
      return () => window.clearTimeout(timer);
    }
    window.scrollTo(0, 0);
    document.getElementById('main-content')?.focus({ preventScroll: true });
  }, [location.pathname, location.hash]);
  return null;
}

export default function App() {
  return <BrowserRouter><a href="#main-content" className="skip-link">Skip to content</a><Navigation /><RouteEffects /><main id="main-content" tabIndex={-1}><Suspense fallback={<div className="container loading" role="status">Opening your next chapter…</div>}><Routes><Route path="/" element={<Home />} /><Route path="/learn/:slug" element={<Tutorial />} /><Route path="/game" element={<Tutorial fixedSlug="game" />} /><Route path="/results" element={<Results />} /><Route path="/watch" element={<Watch />} /><Route path="/download" element={<Download />} /><Route path="/train" element={<Train />} /><Route path="/about" element={<About />} /><Route path="*" element={<div className="container not-found"><h1>Off the delivery route.</h1><p>This page doesn’t exist. Your ship is safe.</p><Link className="button" to="/">Back to mission control</Link></div>} /></Routes></Suspense></main><Footer /></BrowserRouter>;
}
