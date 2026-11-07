import { change as changeOf } from '../lib/format.js';

export const Icon = ({ name, size = 20 }) => {
  const p = {
    home: <><path d="M4 11.5 12 5l8 6.5" /><path d="M6 10v9h12v-9" /><path d="M10 19v-5h4v5" /></>,
    finance: <><path d="M12 3a9 9 0 1 0 9 9h-9z" /><path d="M15 3.5A9 9 0 0 1 20.5 9H15z" /></>,
    ai: <><path d="M5 5h14v10H9l-4 4z" /><path d="M9 9.5h6M9 12h4" /></>,
    orders: <><rect x="4" y="4" width="16" height="16" rx="2" /><path d="M4 9h16M4 14h16M9 4v16M15 4v16" /></>,
    pound: <><path d="M15.5 6.5A3.5 3.5 0 0 0 9 8.5V18" /><path d="M7 12h6M7 18h10" /></>,
    walk: <><circle cx="12" cy="8" r="3.2" /><path d="M5.5 19a6.5 6.5 0 0 1 13 0" /></>,
    bike: <><circle cx="6" cy="16" r="3" /><circle cx="18" cy="16" r="3" /><path d="M6 16l4-7h4l4 7M10 9 8.5 6H7M14 9l1.5-3H17" /></>,
    phone: <><rect x="7" y="3" width="10" height="18" rx="2.5" /><path d="M11 17.5h2" /></>,
    clock: <><circle cx="12" cy="12" r="8.5" /><path d="M12 7.5V12l3 2" /></>,
    percent: <><path d="M18 6 6 18" /><circle cx="7.5" cy="7.5" r="2" /><circle cx="16.5" cy="16.5" r="2" /></>,
    bin: <><path d="M5 7h14M10 7V5h4v2M7 7l1 12h8l1-12" /><path d="M10.5 10.5v5M13.5 10.5v5" /></>,
    wallet: <><rect x="3.5" y="6" width="17" height="13" rx="2.5" /><path d="M16 12.5h4.5M3.5 9.5h14" /></>,
    box: <><path d="m12 3 8 4.5v9L12 21l-8-4.5v-9z" /><path d="m4 7.5 8 4.5 8-4.5M12 12v9" /></>,
    trend: <><path d="M4 16l5-5 4 4 7-7" /><path d="M15 8h5v5" /></>,
    download: <><path d="M12 4v11M7.5 10.5 12 15l4.5-4.5" /><path d="M5 19h14" /></>,
    send: <><path d="M4 12 20 4l-6 16-2.5-6.5z" /></>,
    spark: <><path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M6 18l2.5-2.5M15.5 8.5 18 6" /></>,
  }[name];
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{p}</svg>
  );
};

export function Stat({ icon, label, value, sub, tone, prev, now, higherIsGood = true, className = '' }) {
  const ch = prev != null ? changeOf(now, prev, higherIsGood) : null;
  return (
    <div className={`card stat ${className}`}>
      <div className="stat-icon"><Icon name={icon} /></div>
      <div className="stat-label">{label}</div>
      <div className={`stat-value ${tone ? 'tone-' + tone : ''}`}>{value}</div>
      <div className="stat-foot">
        {ch && <span className={`delta ${ch.good ? 'up' : 'down'}`}>{ch.text}</span>}
        {ch && <span className="muted">vs previous period</span>}
        {sub && <span className="muted">{sub}</span>}
      </div>
    </div>
  );
}

export function ExportButton({ onClick, children }) {
  return (
    <button className="btn btn-ghost" onClick={onClick}>
      <Icon name="download" size={16} />{children}
    </button>
  );
}
