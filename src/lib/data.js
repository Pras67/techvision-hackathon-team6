import meta from '../data/meta.json';
import daily from '../data/daily.json';
import insights from '../data/insights.json';

export { meta, insights };
export const STORES = meta.stores;
export const HOURS = meta.hours; // 7..17
export const FIRST = meta.firstDate;
export const LAST = meta.lastDate;

const F = Object.fromEntries(meta.fields.map((f, i) => [f, i]));

// ---------- dates (all ISO yyyy-mm-dd, UTC) ----------
const toD = (s) => new Date(s + 'T00:00:00Z');
const toS = (d) => d.toISOString().slice(0, 10);
const addDays = (s, n) => { const d = toD(s); d.setUTCDate(d.getUTCDate() + n); return toS(d); };
const clamp = (s) => (s < FIRST ? FIRST : s > LAST ? LAST : s);

export function resolveRange(preset, anchor, custom) {
  const a = clamp(anchor || LAST);
  if (preset === 'day') return { from: a, to: a };
  if (preset === 'week') {
    const dow = (toD(a).getUTCDay() + 6) % 7; // Monday = 0
    const from = addDays(a, -dow);
    return { from: clamp(from), to: clamp(addDays(from, 6)) };
  }
  if (preset === 'month') {
    const from = a.slice(0, 8) + '01';
    const end = toD(from); end.setUTCMonth(end.getUTCMonth() + 1); end.setUTCDate(0);
    return { from: clamp(from), to: clamp(toS(end)) };
  }
  if (preset === 'custom' && custom?.from && custom?.to) {
    const [f, t] = [clamp(custom.from), clamp(custom.to)].sort();
    return { from: f, to: t };
  }
  return { from: FIRST, to: LAST };
}

export function rangeLabel({ from, to }) {
  const fmt = (s, opt) => toD(s).toLocaleDateString('en-GB', { timeZone: 'UTC', ...opt });
  if (from === to) return fmt(from, { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
  if (from === FIRST && to === LAST) return 'Full year · Jul 2025 – Jun 2026';
  return `${fmt(from, { day: 'numeric', month: 'short', year: 'numeric' })} – ${fmt(to, { day: 'numeric', month: 'short', year: 'numeric' })}`;
}

export function previousRange({ from, to }) {
  const len = Math.round((toD(to) - toD(from)) / 864e5) + 1;
  const pTo = addDays(from, -1), pFrom = addDays(from, -len);
  if (pTo < FIRST) return null;
  return { from: clamp(pFrom), to: pTo };
}

// ---------- aggregation ----------
const blank = () => ({
  instore_orders: 0, app_orders: 0, delivery_orders: 0, instore_sales: 0, app_sales: 0, delivery_sales: 0,
  discounts: 0, wastage: 0, cogs: 0, labour: 0, delivery_commission: 0, delivery_packaging: 0,
  rent: 0, business_rates: 0, utilities: 0, repairs: 0, other_opex: 0, days: 0,
});
const NUMS = Object.keys(blank()).filter((k) => k !== 'days');

function add(t, row) {
  for (const k of NUMS) t[k] += row[F[k]];
  t.days += 1;
}

export function derive(t) {
  const orders = t.instore_orders + t.app_orders + t.delivery_orders;
  const net_sales = t.instore_sales + t.app_sales + t.delivery_sales;
  const expenses = t.labour + t.delivery_commission + t.delivery_packaging + t.rent + t.business_rates + t.utilities + t.repairs + t.other_opex;
  const gross_profit = net_sales - t.cogs;
  const net_profit = gross_profit - expenses;
  return {
    ...t, orders, net_sales, gross_sales: net_sales + t.discounts, expenses, gross_profit, net_profit,
    aov: orders ? net_sales / orders : 0,
    gross_margin: net_sales ? gross_profit / net_sales : 0,
    net_margin: net_sales ? net_profit / net_sales : 0,
    delivery_share: net_sales ? t.delivery_sales / net_sales : 0,
  };
}

/** Everything a page needs for a set of stores over a date range. */
export function aggregate(storeIds, { from, to }) {
  const total = blank();
  const byStore = {};
  const byDay = {};
  const hourlySales = HOURS.map(() => 0);
  const hourlyOrders = HOURS.map(() => 0);
  for (const id of storeIds) {
    const s = blank();
    const days = daily[id] || {};
    for (const date in days) {
      if (date < from || date > to) continue;
      const row = days[date];
      add(s, row); add(total, row);
      const d = (byDay[date] ||= blank());
      add(d, row);
      row[F.hourly_sales].forEach((v, i) => { hourlySales[i] += v; });
      row[F.hourly_orders].forEach((v, i) => { hourlyOrders[i] += v; });
    }
    if (s.days) byStore[id] = derive(s);
  }
  const t = derive(total);
  const peakIdx = hourlyOrders.reduce((best, v, i) => (v > hourlyOrders[best] ? i : best), 0);
  const peakSalesIdx = hourlySales.reduce((best, v, i) => (v > hourlySales[best] ? i : best), 0);
  const days = Object.keys(byDay).sort().map((date) => ({ date, ...derive(byDay[date]) }));
  return {
    total: t,
    byStore,
    days,
    hourly: HOURS.map((h, i) => ({ hour: h, sales: hourlySales[i], orders: hourlyOrders[i] })),
    peakHour: t.orders ? HOURS[peakIdx] : null,
    peakSalesHour: t.orders ? HOURS[peakSalesIdx] : null,
    tradingDays: days.length,
  };
}

/** Group a day series into weeks or months for longer ranges. */
export function bucket(days) {
  if (days.length <= 45) return days.map((d) => ({ key: d.date, label: d.date, ...d }));
  const unit = days.length > 120 ? 'month' : 'week';
  const groups = new Map();
  for (const d of days) {
    let key;
    if (unit === 'month') key = d.date.slice(0, 7);
    else { const dow = (toD(d.date).getUTCDay() + 6) % 7; key = addDays(d.date, -dow); }
    const g = groups.get(key) || { key, net_sales: 0, orders: 0, net_profit: 0 };
    g.net_sales += d.net_sales; g.orders += d.orders; g.net_profit += d.net_profit;
    groups.set(key, g);
  }
  return [...groups.values()].map((g) => ({ ...g, label: g.key, unit }));
}

export const storeName = (id) => STORES.find((s) => s.store_id === id)?.store_name || id;
export const ALL_IDS = STORES.map((s) => s.store_id);
