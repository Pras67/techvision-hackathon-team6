const gbp0 = new Intl.NumberFormat('en-GB', { style: 'currency', currency: 'GBP', maximumFractionDigits: 0 });
const gbp2 = new Intl.NumberFormat('en-GB', { style: 'currency', currency: 'GBP', minimumFractionDigits: 2, maximumFractionDigits: 2 });
const compact = new Intl.NumberFormat('en-GB', { notation: 'compact', maximumFractionDigits: 1 });
const int = new Intl.NumberFormat('en-GB', { maximumFractionDigits: 0 });

const sign = (v) => (v < 0 ? '−' : '');
export const money = (v) => (Math.abs(v) >= 100000 ? sign(v) + '£' + compact.format(Math.abs(v)) : gbp0.format(v));
export const moneyFull = (v) => gbp0.format(v);
export const moneyExact = (v) => gbp2.format(v);
export const moneyShort = (v) => (Math.abs(v) >= 1000 ? sign(v) + '£' + compact.format(Math.abs(v)) : gbp0.format(v));
export const count = (v) => int.format(Math.round(v));
export const pct = (v, d = 1) => `${(v * 100).toFixed(d)}%`;
export const hourLabel = (h) => (h == null ? '–' : `${String(h).padStart(2, '0')}:00–${String(h + 1).padStart(2, '0')}:00`);
export const shortDate = (s) => new Date(s + 'T00:00:00Z').toLocaleDateString('en-GB', { timeZone: 'UTC', day: 'numeric', month: 'short' });
export const monthLabel = (s) => new Date(s.slice(0, 7) + '-01T00:00:00Z').toLocaleDateString('en-GB', { timeZone: 'UTC', month: 'short', year: '2-digit' });

/** Change vs the previous period, as { text, good } or null. */
export function change(now, before, higherIsGood = true) {
  if (before == null || !isFinite(before) || before === 0) return null;
  const d = (now - before) / Math.abs(before);
  return { text: `${d >= 0 ? '+' : '−'}${Math.abs(d * 100).toFixed(1)}%`, good: higherIsGood ? d >= 0 : d <= 0 };
}
