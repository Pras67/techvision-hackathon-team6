import { Stat, Icon } from '../components/ui.jsx';
import { HourlyChart, TrendChart } from '../components/Charts.jsx';
import { bucket, storeName } from '../lib/data.js';
import { money, moneyFull, moneyShort, moneyExact, count, pct, hourLabel } from '../lib/format.js';

export default function Home({ agg, prev, singleDay, isAll, setStore }) {
  const t = agg.total, p = prev?.total;
  if (!agg.tradingDays) {
    return <div className="card empty">This store wasn't trading in the selected dates. Leeds Trinity opened on 15 September 2025 — pick a later date or another store.</div>;
  }
  const channels = [
    { key: 'instore', label: 'Walk-in', v: t.instore_sales },
    { key: 'app', label: 'App click & collect', v: t.app_sales },
    { key: 'delivery', label: 'Delivery', v: t.delivery_sales },
  ];
  const stores = Object.entries(agg.byStore).sort((a, b) => b[1].net_sales - a[1].net_sales);
  const maxSales = Math.max(...stores.map(([, s]) => s.net_sales));

  return (
    <div className="page">
      <section className="home-grid">
        <Stat icon="orders" label="Orders" value={count(t.orders)} now={t.orders} prev={p?.orders} />
        <Stat icon="pound" label="Average order value" value={moneyExact(t.aov)} now={t.aov} prev={p?.aov} />
        <Stat icon="walk" label="Walk-in orders" value={count(t.instore_orders)} now={t.instore_orders} prev={p?.instore_orders} />

        <div className="card revenue-card">
          <div className="stat-icon dark"><Icon name="pound" /></div>
          <div className="rev-label">Revenue{singleDay ? ' for the day' : ''}</div>
          <div className="rev-value">{money(t.net_sales)}</div>
          <div className="rev-bar" aria-hidden="true">
            {channels.map((c) => <span key={c.key} className={`seg seg-${c.key}`} style={{ flexGrow: c.v || 0.0001 }} />)}
          </div>
          <dl className="rev-split">
            {channels.map((c) => (
              <div key={c.key}><dt><i className={`dot seg-${c.key}`} />{c.label}</dt><dd>{moneyShort(c.v)}</dd></div>
            ))}
          </dl>
        </div>

        <Stat icon="bike" label="Delivery orders" value={count(t.delivery_orders)} now={t.delivery_orders} prev={p?.delivery_orders} sub={`${pct(t.delivery_share)} of sales`} />
        <Stat icon="phone" label="App orders" value={count(t.app_orders)} now={t.app_orders} prev={p?.app_orders} />
        <Stat icon="clock" label="Peak hour" value={hourLabel(agg.peakSalesHour)} sub={`Highest sales (estimated). Most orders: ${hourLabel(agg.peakHour)}`} />
      </section>

      <section className="card chart-card">
        <div className="card-head">
          <div>
            <h2>{singleDay ? 'Revenue by hour' : 'Revenue over time'}</h2>
            <p className="muted">{singleDay ? 'Sales through the day. The highest-sales hour is marked in yellow. Hourly split is estimated from the 10% receipt sample.' : `${money(t.net_sales)} across ${agg.tradingDays} trading day${agg.tradingDays === 1 ? '' : 's'}.`}</p>
          </div>
        </div>
        {singleDay ? <HourlyChart data={agg.hourly} peakHour={agg.peakSalesHour} /> : <TrendChart data={bucket(agg.days)} />}
      </section>

      {!singleDay && (
        <section className="card chart-card">
          <div className="card-head"><div><h2>Average day by hour</h2><p className="muted">When customers buy across this period. Use it to plan lunch staffing.</p></div></div>
          <HourlyChart data={agg.hourly} peakHour={agg.peakSalesHour} />
        </section>
      )}

      {isAll && (
        <section className="card">
          <div className="card-head"><div><h2>Stores side by side</h2><p className="muted">Select a store to open its own view.</p></div></div>
          <div className="table-wrap">
            <table className="table">
              <thead><tr><th>Store</th><th className="num">Revenue</th><th className="bar-col" aria-hidden="true" /><th className="num">Orders</th><th className="num">Avg order</th><th className="num">Walk-ins</th><th className="num">Delivery share</th></tr></thead>
              <tbody>
                {stores.map(([id, s]) => (
                  <tr key={id} onClick={() => setStore(id)} tabIndex={0} onKeyDown={(e) => e.key === 'Enter' && setStore(id)}>
                    <td className="strong">{storeName(id)}</td>
                    <td className="num">{moneyFull(s.net_sales)}</td>
                    <td className="bar-col"><span className="inbar" style={{ width: `${(s.net_sales / maxSales) * 100}%` }} /></td>
                    <td className="num">{count(s.orders)}</td>
                    <td className="num">{moneyExact(s.aov)}</td>
                    <td className="num">{count(s.instore_orders)}</td>
                    <td className="num">{pct(s.delivery_share)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  );
}
