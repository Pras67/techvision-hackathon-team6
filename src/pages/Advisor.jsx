import { useEffect, useRef, useState } from 'react';
import { Icon } from '../components/ui.jsx';

const SUGGESTIONS = [
  'Summarise what is going on in this view and what I should do.',
  'Which stores are losing money, and why?',
  'How should we split the £1.5m, with expected payback?',
  'Should we open another store in Leeds?',
  'Is delivery actually making us money?',
];

// Light formatting for the advisor's answers: paragraphs, bullet lists and **bold**.
function Rich({ text }) {
  const blocks = text.split(/\n{2,}/);
  const inline = (s, k) => s.split(/(\*\*[^*]+\*\*)/g).map((part, i) =>
    part.startsWith('**') && part.endsWith('**') ? <strong key={`${k}-${i}`}>{part.slice(2, -2)}</strong> : <span key={`${k}-${i}`}>{part}</span>);
  return blocks.map((b, bi) => {
    const lines = b.split('\n').filter(Boolean);
    if (lines.length && lines.every((l) => /^\s*([-*•]|\d+\.)\s+/.test(l))) {
      const ordered = /^\s*\d+\./.test(lines[0]);
      const items = lines.map((l, li) => <li key={li}>{inline(l.replace(/^\s*([-*•]|\d+\.)\s+/, ''), `${bi}-${li}`)}</li>);
      return ordered ? <ol key={bi}>{items}</ol> : <ul key={bi}>{items}</ul>;
    }
    return <p key={bi}>{lines.map((l, li) => <span key={li}>{inline(l.replace(/^#+\s*/, ''), `${bi}-${li}`)}{li < lines.length - 1 && <br />}</span>)}</p>;
  });
}

export default function Advisor({ buildContext, scopeLabel, messages, setMessages }) {
  const [input, setInput] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const endRef = useRef(null);

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' }); }, [messages, busy]);

  async function send(text) {
    const q = (text ?? input).trim();
    if (!q || busy) return;
    const next = [...messages, { role: 'user', text: q }];
    setMessages(next); setInput(''); setError(''); setBusy(true);
    try {
      const r = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: next, context: buildContext() }),
      });
      const j = await r.json().catch(() => ({ error: `The advisor returned an unreadable answer (status ${r.status}).` }));
      if (!r.ok || j.error) throw new Error(j.error || `Request failed (${r.status}).`);
      setMessages([...next, { role: 'assistant', text: j.text }]);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="page advisor">
      <section className="card advisor-card">
        <div className="advisor-scope">
          <Icon name="spark" size={18} />
          <span>The advisor sees: <b>{scopeLabel}</b>. Change the store or dates and your next question uses the new view.</span>
        </div>

        <div className="chat" aria-live="polite">
          {!messages.length && (
            <div className="chat-empty">
              <h2>Ask about any store, any period</h2>
              <p className="muted">Answers use the dashboard's numbers plus the team's findings. Start with a summary or pick a question.</p>
              <div className="suggestions">
                {SUGGESTIONS.map((s) => <button key={s} className="suggestion" onClick={() => send(s)}>{s}</button>)}
              </div>
            </div>
          )}
          {messages.map((m, i) => (
            <div key={i} className={`msg ${m.role}`}>
              <div className="bubble">{m.role === 'assistant' ? <Rich text={m.text} /> : m.text}</div>
            </div>
          ))}
          {busy && <div className="msg assistant"><div className="bubble typing" aria-label="The advisor is writing"><i /><i /><i /></div></div>}
          {error && <div className="chat-error" role="alert">{error}</div>}
          <div ref={endRef} />
        </div>

        <form className="composer" onSubmit={(e) => { e.preventDefault(); send(); }}>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } }}
            placeholder="Ask the advisor, e.g. why is Piccadilly losing money?"
            rows={2}
            aria-label="Message"
          />
          <button className="btn btn-dark" type="submit" disabled={busy || !input.trim()}><Icon name="send" size={16} />Send</button>
        </form>
      </section>
    </div>
  );
}
