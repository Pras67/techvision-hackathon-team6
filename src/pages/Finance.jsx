import { Stat } from '../components/ui.jsx';
import { TrendChart } from '../components/Charts.jsx';
import { bucket, storeName } from '../lib/data.js';
import { money, moneyFull, pct } from '../lib/format.js';

const EXPENSES = [
  ['labour', 'Labour'],
  ['rent', 'Rent'],
  ['delivery_commission', 'Delivery commission'],
  ['utilities', 'Utilities'],
  ['business_rates', 'Business rates'],
  ['repairs', 'Repairs & maintenance'],
  ['other_opex', 'Other running costs'],
  ['delivery_packaging', 'Delivery packaging'],
];

export default function Finance({ agg, prev, isAll, setStore }) {
  const t = agg.total, p = prev?.total;
  if (!agg.tradingDays) {
    return <div className="card empty">This store wasn't trading in the selected dates. Leeds Trinity opened on 15 September 2025 — pick a later date or another store.</div>;
  }
  const maxExp = Math.max(...EXPENSES.map(([k]) => t[k]));
  const stores = Object.entries(agg.byStore).sort((a, b) => b[1].net_profit - a[1].net_profit);

  return (
    <div className="page">
      <section className="fin-grid">
        <Stat icon="pound" label="Gross sales" value={money(t.gross_sales)} now={t.gross_sales} prev={p?.gross_sales} sub="Before discounts" />
        <Stat icon="percent" label="Discounts" value={money(t.discounts)} tone="bad" now={t.discounts} prev={p?.discounts} higherIsGood={false} sub="Estimated from receipts" />
        <Stat icon="bin" label="Wastage" value={money(t.wastage)} tone={t.wastage ? 'bad' : undefined} now={t.wastage} prev={p?.wastage} higherIsGood={false} sub={`${pct(t.net_sales ? t.wastage / t.net_sales : 0)} of sales · counted in COGS`} />
        <Stat icon="wallet" label="Expenses" value={money(t.expenses)} now={t.expenses} prev={p?.expenses} higherIsGood={false} sub="Labour, rent, delivery and running costs" />
        <Stat icon="pound" label="Net sales" value={money(t.net_sales)} tone="good" now={t.net_sales} prev={p?.net_sales} />
        <Stat icon="box" label="COGS" value={money(t.cogs)} now={t.cogs} prev={p?.cogs} higherIsGood={false} sub={`${pct(t.net_sales ? t.cogs / t.net_sales : 0)} of net sales`} />
        <Stat icon="trend" label="Gross profit" value={money(t.gross_profit)} tone="good" now={t.gross_profit} prev={p?.gross_profit} sub={`${pct(t.gross_margin)} margin`} />
        <Stat icon="trend" label="Net profit" value={money(t.net_profit)} tone={t.net_profit < 0 ? 'bad' : 'good'} now={t.net_profit} prev={p?.net_profit} sub={`${pct(t.net_margin)} store margin`} className="stat-feature" />
      </section>

      <div className="two-col">
        <section className="card">
          <div className="card-head"><div><h2>Where the money goes</h2><p className="muted">Expenses for this period, largest first.</p></div></div>
          <ul className="exp-list">
            {EXPENSES.slice().sort((a, b) => t[b[0]] - t[a[0]]).map(([k, label]) => (
              <li key={k}>
                <span className="exp-name">{label}</span>
                <span className="exp-track"><span className="exp-fill" style={{ width: `${maxExp ? (t[k] / maxExp) * 100 : 0}%` }} /></span>
                <span className="exp-val">{money(t[k])}</span>
                <span className="exp-pct muted">{pct(t.net_sales ? t[k] / t.net_sales : 0)}</span>
              </li>
            ))}
          </ul>
          <p className="muted small">Percentages are of net sales. Monthly costs are spread evenly across trading days, so single-day figures are estimates.</p>
        </section>

        <section className="card chart-card">
          <div className="card-head"><div><h2>Net profit over time</h2><p className="muted">After food, labour, delivery and running costs.</p></div></div>
          {agg.days.length > 1 ? <TrendChart data={bucket(agg.days)} valueKey="net_profit" name="Net profit" showZero /> : <p className="muted">Pick a week, month or longer to see the trend.</p>}
        </section>
      </div>

      {isAll && (
        <section className="card">
          <div className="card-head"><div><h2>Profit and loss by store</h2><p className="muted">Sorted by net profit. Select a store to open its own view.</p></div></div>
          <div className="table-wrap">
            <table className="table">
              <thead><tr><th>Store</th><th className="num">Net sales</th><th className="num">COGS</th><th className="num">Gross profit</th><th className="num">Labour</th><th className="num">Rent</th><th className="num">Delivery costs</th><th className="num">Net profit</th><th className="num">Margin</th></tr></thead>
              <tbody>
                {stores.map(([id, s]) => (
                  <tr key={id} onClick={() => setStore(id)} tabIndex={0} onKeyDown={(e) => e.key === 'Enter' && setStore(id)}>
                    <td className="strong">{storeName(id)}</td>
                    <td className="num">{moneyFull(s.net_sales)}</td>
                    <td className="num">{moneyFull(s.cogs)}</td>
                    <td className="num">{moneyFull(s.gross_profit)}</td>
                    <td className="num">{moneyFull(s.labour)}</td>
                    <td className="num">{moneyFull(s.rent)}</td>
                    <td className="num">{moneyFull(s.delivery_commission + s.delivery_packaging)}</td>
                    <td className={`num strong ${s.net_profit < 0 ? 'tone-bad' : ''}`}>{moneyFull(s.net_profit)}</td>
                    <td className={`num ${s.net_margin < 0 ? 'tone-bad' : ''}`}>{pct(s.net_margin)}</td>
                  </tr>
                ))}
              </tbody>
              <tfoot><tr><td className="strong">All stores</td><td className="num">{moneyFull(t.net_sales)}</td><td className="num">{moneyFull(t.cogs)}</td><td className="num">{moneyFull(t.gross_profit)}</td><td className="num">{moneyFull(t.labour)}</td><td className="num">{moneyFull(t.rent)}</td><td className="num">{moneyFull(t.delivery_commission + t.delivery_packaging)}</td><td className="num strong">{moneyFull(t.net_profit)}</td><td className="num">{pct(t.net_margin)}</td></tr></tfoot>
            </table>
          </div>
        </section>
      )}
    </div>
  );
}
