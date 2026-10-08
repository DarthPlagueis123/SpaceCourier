import { useState, type ReactNode } from 'react';
import { Link } from 'react-router-dom';
import Prism from 'prismjs';
import 'prismjs/components/prism-python';
import 'prismjs/components/prism-bash';
import 'prismjs/components/prism-powershell';
import snippetData from '../generated/snippets.json';

export function Arrow({ direction = 'right' }: { direction?: 'right' | 'down' }) {
  return <svg viewBox="0 0 24 24" width="20" height="20" fill="none" aria-hidden="true" style={{ transform: direction === 'down' ? 'rotate(90deg)' : undefined }}><path d="M4 12h15m-6-6 6 6-6 6" stroke="currentColor" strokeWidth="1.7" /></svg>;
}

export function Eyebrow({ children }: { children: ReactNode }) { return <div className="eyebrow"><span className="pixel-dot" />{children}</div>; }
export function ButtonLink({ to, children, secondary = false }: { to: string; children: ReactNode; secondary?: boolean }) {
  return <Link className={`button ${secondary ? 'button-secondary' : ''}`} to={to}>{children}<Arrow /></Link>;
}
export function MetricCard({ label, value, detail }: { label: string; value: string; detail?: string }) {
  return <div className="metric-card"><span className="micro">{label}</span><strong>{value}</strong>{detail && <span>{detail}</span>}</div>;
}
export function Note({ title, children, kind = 'info' }: { title: string; children: ReactNode; kind?: 'info' | 'warning' }) {
  return <aside className={`note note-${kind}`}><span className="note-symbol" aria-hidden="true">{kind === 'warning' ? '!' : 'i'}</span><div><strong>{title}</strong><div>{children}</div></div></aside>;
}

export function CodeBlock({ snippet, code, filename, language = 'python' }: { snippet?: keyof typeof snippetData; code?: string; filename?: string; language?: string }) {
  const record = snippet ? snippetData[snippet] : undefined;
  const value = record?.code ?? code ?? '';
  const [status, setStatus] = useState('Copy');
  const grammar = Prism.languages[language] ?? Prism.languages.plain;
  const highlighted = grammar ? Prism.highlight(value, grammar, language) : value.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;');
  async function copy() {
    try {
      await navigator.clipboard.writeText(value);
      setStatus('Copied');
    } catch {
      setStatus('Select to copy');
    }
    window.setTimeout(() => setStatus('Copy'), 2200);
  }
  return <div className="code-block"><div className="code-toolbar"><span>{record?.filename ?? filename ?? 'Terminal'}{record && <small> · line {record.line}</small>}</span><button onClick={copy} aria-label={`Copy ${record?.filename ?? filename ?? 'command'}`}>{status}</button><span className="sr-only" role="status">{status === 'Copied' ? 'Code copied to clipboard' : ''}</span></div><pre tabIndex={0}><code className={`language-${language}`} dangerouslySetInnerHTML={{ __html: highlighted }} /></pre></div>;
}

export function PageHeading({ eyebrow, title, description }: { eyebrow: string; title: string; description: string }) {
  return <header className="page-heading"><Eyebrow>{eyebrow}</Eyebrow><h1>{title}</h1><p>{description}</p></header>;
}

export function GameScreenshot({ src, caption, alt }: { src: string; caption: string; alt: string }) {
  return <figure className="game-screenshot"><img src={src} alt={alt} loading="lazy" width="480" height="640" /><figcaption>{caption}</figcaption></figure>;
}

export function TutorialSection({ id, title, children }: { id: string; title: string; children: ReactNode }) {
  return <section className="tutorial-section" id={id}><h2>{title}</h2>{children}</section>;
}
