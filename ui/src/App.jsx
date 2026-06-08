import { useState, useRef, useEffect, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

// ─── Constants ────────────────────────────────────────────────────────────────

const FORMATS = [
  { value: 'report',       label: 'Research Report' },
  { value: 'blog',         label: 'Blog Post' },
  { value: 'summary',      label: 'Executive Summary' },
  { value: 'essay',        label: 'Essay' },
  { value: 'tweet-thread', label: 'Tweet Thread' },
  { value: 'linkedin',     label: 'LinkedIn Post' },
  { value: 'newsletter',   label: 'Newsletter' },
  { value: 'slides',       label: 'Slide Deck' },
];

const STEP_LABELS = {
  search:   'Search',
  read:     'Read & Extract',
  write:    'Write',
  critique: 'Critique',
};

const STEP_ORDER = ['search', 'read', 'write', 'critique'];

const STATUS_ICON = {
  pending: '○',
  running: '◌',
  done:    '✓',
  error:   '✕',
};

// ─── Sub-components ────────────────────────────────────────────────────────────

function StepBadge({ stepKey, status, info }) {
  const icon  = STATUS_ICON[status] || '○';
  const label = STEP_LABELS[stepKey];
  return (
    <div className={`step-badge step-${status}`}>
      <span className="step-icon">{icon}</span>
      <span className="step-label">{label}</span>
      {info && <span className="step-info">{info}</span>}
    </div>
  );
}

function QualityPip({ score, attempt }) {
  const color = score >= 8 ? '#39FF14' : score >= 6 ? '#f5a623' : '#ff4444';
  return (
    <div className="quality-pip" style={{ borderColor: color }}>
      <span style={{ color }}>⬡ {score}/10</span>
      <span className="quality-attempt">attempt {attempt}</span>
    </div>
  );
}

function StatBar({ sources, words, score }) {
  return (
    <div className="stat-bar">
      {sources != null && <span>⬡ {sources} sources</span>}
      {words   != null && <span>⬡ {words} words</span>}
      {score   != null && <span>⬡ quality {score}/10</span>}
    </div>
  );
}

function CopyButton({ text }) {
  const [copied, setCopied] = useState(false);
  const copy = () => {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };
  return (
    <button className="copy-btn" onClick={copy}>
      {copied ? '✓ Copied' : 'Copy'}
    </button>
  );
}

// ─── Main App ──────────────────────────────────────────────────────────────────

export default function App() {
  const [goal,      setGoal]      = useState('');
  const [format,    setFormat]    = useState('report');
  const [running,   setRunning]   = useState(false);
  const [steps,     setSteps]     = useState({});
  const [output,    setOutput]    = useState('');
  const [streaming, setStreaming] = useState(false);
  const [stats,     setStats]     = useState(null);
  const [quality,   setQuality]   = useState([]);  // [{score, attempt, feedback}]
  const [urls,      setUrls]      = useState([]);
  const [error,     setError]     = useState('');

  const esRef        = useRef(null);
  const outputRef    = useRef(null);

  // Auto-scroll output area
  useEffect(() => {
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight;
    }
  }, [output]);

  const reset = useCallback(() => {
    setSteps({});
    setOutput('');
    setStreaming(false);
    setStats(null);
    setQuality([]);
    setUrls([]);
    setError('');
  }, []);

  const stop = useCallback(() => {
    if (esRef.current) {
      esRef.current.close();
      esRef.current = null;
    }
    setRunning(false);
    setStreaming(false);
  }, []);

  const run = useCallback(() => {
    if (!goal.trim()) return;
    if (running) { stop(); return; }

    reset();
    setRunning(true);

    const params = new URLSearchParams({ goal: goal.trim(), format });
    const es     = new EventSource(`/run?${params}`);
    esRef.current = es;

    es.onmessage = (e) => {
      if (e.data === '[DONE]') { stop(); return; }

      let event;
      try { event = JSON.parse(e.data); } catch { return; }

      switch (event.type) {
        case 'step':
          setSteps(prev => ({
            ...prev,
            [event.step]: { status: event.status, info: event.info || '' },
          }));
          if (event.urls?.length) setUrls(event.urls);
          break;

        case 'streaming_start':
          setStreaming(true);
          break;

        case 'token':
          setOutput(prev => prev + event.content);
          break;

        case 'streaming_end':
          setStreaming(false);
          break;

        case 'quality':
          setQuality(prev => [...prev, {
            score:    event.score,
            attempt:  event.attempt,
            feedback: event.feedback,
          }]);
          break;

        case 'done':
          setStats(event.stats);
          break;

        case 'error':
          setError(event.message);
          stop();
          break;
      }
    };

    es.onerror = () => {
      setError('Connection lost. Make sure the Nexus server is running on port 8000.');
      stop();
    };
  }, [goal, format, running, reset, stop]);

  const handleKey = (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) run();
  };

  const isDone   = !running && output.length > 0;
  const hasSteps = Object.keys(steps).length > 0;

  return (
    <div className="app">
      {/* ── Header ── */}
      <header className="header">
        <div className="header-left">
          <span className="logo">◈ NEXUS</span>
          <span className="logo-sub">by Rewrite Labs</span>
        </div>
        <div className="header-right">
          <a href="https://github.com/iamadhitya1/nexus" target="_blank" rel="noreferrer" className="badge">
            MIT · Open Source
          </a>
          <a href="https://rewritelabs.vercel.app" target="_blank" rel="noreferrer" className="badge badge-dim">
            rewritelabs
          </a>
        </div>
      </header>

      <main className="main">
        {/* ── Input panel ── */}
        <section className="input-panel">
          <label className="input-label">What do you want to research?</label>
          <textarea
            className="goal-input"
            placeholder="e.g. How does retrieval-augmented generation work and when should I use it?"
            value={goal}
            onChange={e => setGoal(e.target.value)}
            onKeyDown={handleKey}
            rows={3}
            disabled={running}
          />
          <div className="input-row">
            <div className="format-wrapper">
              <label className="format-label">Format</label>
              <select
                className="format-select"
                value={format}
                onChange={e => setFormat(e.target.value)}
                disabled={running}
              >
                {FORMATS.map(f => (
                  <option key={f.value} value={f.value}>{f.label}</option>
                ))}
              </select>
            </div>
            <button
              className={`run-btn ${running ? 'run-btn--stop' : ''}`}
              onClick={run}
              disabled={!goal.trim() && !running}
            >
              {running ? '■ Stop' : '▶ Run Nexus'}
            </button>
          </div>
          <p className="hint">Ctrl+Enter to run</p>
        </section>

        {/* ── Pipeline steps ── */}
        {hasSteps && (
          <section className="pipeline">
            {STEP_ORDER.map(key => {
              const s = steps[key];
              if (!s) return (
                <StepBadge key={key} stepKey={key} status="pending" />
              );
              return <StepBadge key={key} stepKey={key} status={s.status} info={s.info} />;
            })}
          </section>
        )}

        {/* ── Quality scores ── */}
        {quality.length > 0 && (
          <div className="quality-row">
            {quality.map((q, i) => (
              <QualityPip key={i} score={q.score} attempt={q.attempt} />
            ))}
          </div>
        )}

        {/* ── Error ── */}
        {error && (
          <div className="error-box">
            <span>✕ {error}</span>
          </div>
        )}

        {/* ── Output ── */}
        {output.length > 0 && (
          <section className="output-section">
            <div className="output-header">
              <span className="output-title">Output {streaming && <span className="cursor">▌</span>}</span>
              {isDone && <CopyButton text={output} />}
            </div>
            <div className="output-area" ref={outputRef}>
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{output}</ReactMarkdown>
            </div>
            {stats && (
              <StatBar sources={stats.sources} words={stats.words} score={stats.score} />
            )}
          </section>
        )}

        {/* ── Sources ── */}
        {urls.length > 0 && isDone && (
          <section className="sources">
            <p className="sources-title">Sources</p>
            <ul>
              {urls.map((url, i) => (
                <li key={i}>
                  <a href={url} target="_blank" rel="noreferrer">{url}</a>
                </li>
              ))}
            </ul>
          </section>
        )}
      </main>

      <footer className="footer">
        <span>© 2026 Rewrite Labs · M Adhitya</span>
        <span>·</span>
        <a href="https://github.com/iamadhitya1/nexus" target="_blank" rel="noreferrer">GitHub</a>
        <span>·</span>
        <span>MIT License</span>
      </footer>
    </div>
  );
}
