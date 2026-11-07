import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine } from 'recharts';
import { moneyShort, moneyExact, count, shortDate, monthLabel } from '../lib/format.js';

const axis = { stroke: 'var(--line)', tick: { fill: 'var(--ink-3)', fontSize: 12 }, tickLine: false };

function Tip({ active, payload, label, labelFmt, rows }) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="chart-tip">
      <div className="tip-head">{labelFmt(label, d)}</div>
      {rows.map((r) => <div key={r.key} className="tip-row"><span>{r.name}</span><b>{r.fmt(d[r.key])}</b></div>)}
    </div>
  );
}

/** Hour-by-hour sales for a single day or the average shape of a range. */
export function HourlyChart({ data, peakHour }) {
  return (
    <ResponsiveContainer width="100%" height={260}>
      <AreaChart data={data} margin={{ top: 12, right: 16, left: 4, bottom: 0 }}>
        <defs>
          <linearGradient id="fill-hourly" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="var(--roast)" stopOpacity={0.22} />
            <stop offset="100%" stopColor="var(--roast)" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid vertical={false} stroke="var(--line)" />
        <XAxis dataKey="hour" {...axis} tickFormatter={(h) => `${String(h).padStart(2, '0')}:00`} padding={{ left: 8, right: 8 }} />
        <YAxis {...axis} axisLine={false} width={56} tickFormatter={moneyShort} />
        {peakHour != null && <ReferenceLine x={peakHour} stroke="var(--crema)" strokeWidth={2} strokeDasharray="4 4" />}
        <Tooltip cursor={{ stroke: 'var(--ink-3)', strokeWidth: 1 }} content={<Tip labelFmt={(h) => `${String(h).padStart(2, '0')}:00–${String(h + 1).padStart(2, '0')}:00`} rows={[{ key: 'sales', name: 'Sales', fmt: moneyExact }, { key: 'orders', name: 'Orders', fmt: count }]} />} />
        <Area
          isAnimationActive={false}
          type="linear"
          dataKey="sales"
          stroke="var(--roast)"
          strokeWidth={2.5}
          strokeLinecap="round"
          strokeLinejoin="round"
          fill="url(#fill-hourly)"
          dot={(p) => (
            <circle key={p.payload.hour} cx={p.cx} cy={p.cy} r={p.payload.hour === peakHour ? 6 : 3.5}
              fill={p.payload.hour === peakHour ? 'var(--crema)' : 'var(--card)'} stroke="var(--roast)" strokeWidth={2} />
          )}
          activeDot={{ r: 6, fill: 'var(--crema)', stroke: 'var(--roast)', strokeWidth: 2 }}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}

const bucketLabel = (b) => (b.unit === 'month' ? monthLabel(b.key) : b.unit === 'week' ? `w/c ${shortDate(b.key)}` : shortDate(b.key));

/** Sales over a date range, by day, week or month depending on length. */
export function TrendChart({ data, valueKey = 'net_sales', name = 'Net sales', showZero = false }) {
  const unitText = data[0]?.unit === 'month' ? 'month' : data[0]?.unit === 'week' ? 'week' : 'day';
  return (
    <ResponsiveContainer width="100%" height={260}>
      <AreaChart data={data} margin={{ top: 8, right: 8, left: 4, bottom: 0 }}>
        <defs>
          <linearGradient id={`fill-${valueKey}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="var(--roast)" stopOpacity={0.22} />
            <stop offset="100%" stopColor="var(--roast)" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid vertical={false} stroke="var(--line)" />
        <XAxis dataKey="key" {...axis} tickFormatter={(k) => bucketLabel(data.find((d) => d.key === k) || { key: k })} minTickGap={24} />
        <YAxis {...axis} axisLine={false} width={56} tickFormatter={moneyShort} />
        {showZero && <ReferenceLine y={0} stroke="var(--ink-3)" />}
        <Tooltip content={<Tip labelFmt={(k, d) => `${bucketLabel(d)} (per ${unitText})`} rows={[{ key: valueKey, name, fmt: moneyExact }, ...(valueKey === 'net_sales' ? [{ key: 'orders', name: 'Orders', fmt: count }] : [])]} />} />
        <Area isAnimationActive={false} type="linear" dataKey={valueKey} stroke="var(--roast)" strokeWidth={2} fill={`url(#fill-${valueKey})`} dot={false} activeDot={{ r: 4, fill: 'var(--crema)', stroke: 'var(--roast)' }} />
      </AreaChart>
    </ResponsiveContainer>
  );
}
