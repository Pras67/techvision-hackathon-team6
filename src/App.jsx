import { useMemo, useState } from 'react';
import Sidebar from './components/Sidebar.jsx';
import DateBar from './components/DateBar.jsx';
import { ExportButton } from './components/ui.jsx';
import Home from './pages/Home.jsx';
import Finance from './pages/Finance.jsx';
import Advisor from './pages/Advisor.jsx';
import { aggregate, resolveRange, previousRange, rangeLabel, storeName, ALL_IDS, LAST, insights } from './lib/data.js';
import { exportOverview, exportSales, exportExpenses, exportPnl, exportChat } from './lib/exporter.js';

const TITLES = { home: 'Overview', finance: 'Finance', advisor: 'AI advisor' };
const r0 = (v) => Math.round(v);

export default function App() {
  const [page, setPage] = useState('home');
  const [store, setStore] = useState('all');
  const [preset, setPreset] = useState('month');
  const [anchor, setAnchor] = useState(LAST);
  const [custom, setCustom] = useState({ from: '2026-01-01', to: LAST });
  const [messages, setMessages] = useState([]);
  const [chatBusy, setChatBusy] = useState(false);
  const [chatError, setChatError] = useState('');

  const ids = store === 'all' ? ALL_IDS : [store];
  const range = useMemo(() => resolveRange(preset, anchor, custom), [preset, anchor, custom]);
  const agg = useMemo(() => aggregate(ids, range), [store, range]);
  const prevRange = preset === 'all' ? null : previousRange(range, preset);
  const prev = useMemo(() => (prevRange ? aggregate(ids, prevRange) : null), [store, prevRange?.from, prevRange?.to]);
  const scope = store === 'all' ? 'All stores' : storeName(store);
  const singleDay = range.from === range.to;

  const goStore = (id) => { setStore(id); window.scrollTo({ top: 0, behavior: 'smooth' }); };

  // What the AI advisor is given: the current view, the previous period, every store, and the team's findings.
  const buildContext = () => {
    const pick = (s) => s && ({
      net_sales: r0(s.net_sales), gross_sales: r0(s.gross_sales), discounts: r0(s.discounts), orders: r0(s.orders),
      walk_in_orders: s.instore_orders, app_orders: s.app_orders, delivery_orders: s.delivery_orders, avg_order_value: +s.aov.toFixed(2),
      delivery_share: +s.delivery_share.toFixed(3), cogs: r0(s.cogs), wastage: r0(s.wastage), gross_profit: r0(s.gross_profit),
      labour: r0(s.labour), rent: r0(s.rent), delivery_commission: r0(s.delivery_commission), other_costs: r0(s.business_rates + s.utilities + s.repairs + s.other_opex + s.delivery_packaging),
      expenses: r0(s.expenses), net_profit: r0(s.net_profit), net_margin: +s.net_margin.toFixed(3),
    });
    const everyStore = aggregate(ALL_IDS, range);
    return {
      view: { scope, period: rangeLabel(range), from: range.from, to: range.to, trading_days: agg.tradingDays, peak_hour: agg.peakHour },
      totals: pick(agg.total),
      previous_period: prev?.tradingDays ? { period: rangeLabel(prevRange), totals: pick(prev.total) } : null,
      all_stores_this_period: Object.fromEntries(Object.entries(everyStore.byStore).map(([id, s]) => [storeName(id), pick(s)])),
      hourly_sales_estimate: agg.hourly.map((h) => ({ hour: h.hour, sales: r0(h.sales), orders: r0(h.orders) })),
      background: insights,
      notes: 'Sales and orders are full daily totals. Hourly split and discounts are estimated from a 10% receipt sample. Monthly costs are spread across trading days. Wastage is already included in COGS.',
    };
  };

  const exports = {
    home: [['Export Excel', () => exportOverview(agg, scope, range)]],
    finance: [['Sales Excel', () => exportSales(agg, scope, range)], ['Expenses Excel', () => exportExpenses(agg, scope, range)], ['Full P&L Excel', () => exportPnl(agg, scope, range)]],
    advisor: messages.length ? [['Export chat', () => exportChat(messages)]] : [],
  }[page];

  return (
    <div className="shell">
      <Sidebar page={page} setPage={setPage} store={store} setStore={goStore} />
      <main className="main">
        <header className="topbar">
          <div className="title-block">
            <h1>{TITLES[page]}</h1>
            <p className="scope">{scope} · {rangeLabel(range)}</p>
          </div>
          <div className="controls">
            <DateBar preset={preset} setPreset={setPreset} anchor={anchor} setAnchor={setAnchor} custom={custom} setCustom={setCustom} />
            {exports.length > 0 && <div className="exports">{exports.map(([label, fn]) => <ExportButton key={label} onClick={fn}>{label}</ExportButton>)}</div>}
          </div>
        </header>

        {page === 'home' && <Home agg={agg} prev={prev} singleDay={singleDay} isAll={store === 'all'} setStore={goStore} />}
        {page === 'finance' && <Finance agg={agg} prev={prev} isAll={store === 'all'} setStore={goStore} />}
        {page === 'advisor' && <Advisor buildContext={buildContext} scopeLabel={`${scope}, ${rangeLabel(range)}`} messages={messages} setMessages={setMessages} busy={chatBusy} setBusy={setChatBusy} error={chatError} setError={setChatError} />}
      </main>
    </div>
  );
}
