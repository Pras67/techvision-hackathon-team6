import { FIRST, LAST } from '../lib/data.js';

const PRESETS = [
  { id: 'day', label: 'Day' },
  { id: 'week', label: 'Week' },
  { id: 'month', label: 'Month' },
  { id: 'all', label: 'All time' },
  { id: 'custom', label: 'Custom' },
];

export default function DateBar({ preset, setPreset, anchor, setAnchor, custom, setCustom }) {
  return (
    <div className="datebar">
      <div className="segmented" role="tablist" aria-label="Date range">
        {PRESETS.map((p) => (
          <button key={p.id} role="tab" aria-selected={preset === p.id} className={preset === p.id ? 'on' : ''} onClick={() => setPreset(p.id)}>{p.label}</button>
        ))}
      </div>
      {preset === 'custom' ? (
        <div className="date-pair">
          <input type="date" aria-label="From" min={FIRST} max={LAST} value={custom.from} onChange={(e) => setCustom({ ...custom, from: e.target.value })} />
          <span className="muted">to</span>
          <input type="date" aria-label="To" min={FIRST} max={LAST} value={custom.to} onChange={(e) => setCustom({ ...custom, to: e.target.value })} />
        </div>
      ) : preset !== 'all' ? (
        <input
          type={preset === 'month' ? 'month' : 'date'}
          aria-label={preset === 'month' ? 'Month' : 'Date'}
          min={preset === 'month' ? FIRST.slice(0, 7) : FIRST}
          max={preset === 'month' ? LAST.slice(0, 7) : LAST}
          value={preset === 'month' ? anchor.slice(0, 7) : anchor}
          onChange={(e) => e.target.value && setAnchor(preset === 'month' ? e.target.value + '-01' : e.target.value)}
        />
      ) : null}
    </div>
  );
}
