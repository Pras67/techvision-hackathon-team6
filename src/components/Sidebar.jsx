import { Icon } from './ui.jsx';
import { STORES } from '../lib/data.js';

const NAV = [
  { id: 'home', label: 'Overview', icon: 'home' },
  { id: 'finance', label: 'Finance', icon: 'finance' },
  { id: 'advisor', label: 'AI advisor', icon: 'ai' },
];

export default function Sidebar({ page, setPage, store, setStore }) {
  const cities = [...new Set(STORES.map((s) => s.city))];
  return (
    <aside className="sidebar">
      <div className="brand">
        <span className="brand-mark" aria-hidden="true" />
        <div>
          <div className="brand-name">Grind &amp; Crumb</div>
          <div className="brand-sub">CEO dashboard</div>
        </div>
      </div>

      <nav className="nav" aria-label="Pages">
        {NAV.map((n) => (
          <button key={n.id} className={`nav-item ${page === n.id ? 'active' : ''}`} onClick={() => setPage(n.id)} aria-current={page === n.id ? 'page' : undefined}>
            <Icon name={n.icon} />{n.label}
          </button>
        ))}
      </nav>

      <div className="store-picker">
        <label htmlFor="store-select" className="side-heading">Showing</label>
        <select id="store-select" className="store-select" value={store} onChange={(e) => setStore(e.target.value)}>
          <option value="all">All 12 stores</option>
          {cities.map((c) => (
            <optgroup key={c} label={c}>
              {STORES.filter((s) => s.city === c).map((s) => <option key={s.store_id} value={s.store_id}>{s.store_name}</option>)}
            </optgroup>
          ))}
        </select>
        <div className="store-list" role="list">
          <button role="listitem" className={`store-chip ${store === 'all' ? 'on' : ''}`} onClick={() => setStore('all')}>All stores</button>
          {STORES.map((s) => (
            <button role="listitem" key={s.store_id} className={`store-chip ${store === s.store_id ? 'on' : ''}`} onClick={() => setStore(s.store_id)} title={`${s.format} · ${s.location_type}`}>
              {s.store_name}
            </button>
          ))}
        </div>
      </div>

      <p className="side-note">Data covers 1 Jul 2025 – 30 Jun 2026. Figures are net of VAT.</p>
    </aside>
  );
}
