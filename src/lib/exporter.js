import * as XLSX from 'xlsx';
import { storeName, rangeLabel, HOURS } from './data.js';

const r2 = (v) => Math.round(v * 100) / 100;

function sheet(rows, widths) {
  const ws = XLSX.utils.json_to_sheet(rows);
  if (widths) ws['!cols'] = widths.map((w) => ({ wch: w }));
  return ws;
}

function save(wb, name) {
  XLSX.writeFile(wb, `${name}.xlsx`);
}

const scopeRows = (scope, range) => [
  { Field: 'Scope', Value: scope },
  { Field: 'Period', Value: rangeLabel(range) },
  { Field: 'Exported', Value: new Date().toLocaleString('en-GB') },
  { Field: 'Source', Value: 'Grind & Crumb data pack. Sales and orders are full daily totals; hourly figures are estimated from the 10% receipt sample.' },
];

const storeRow = (id, s) => ({
  Store: storeName(id),
  'Orders': Math.round(s.orders),
  'Walk-in orders': s.instore_orders,
  'App orders': s.app_orders,
  'Delivery orders': s.delivery_orders,
  'Avg order value (£)': r2(s.aov),
  'Net sales (£)': r2(s.net_sales),
  'In-store sales (£)': r2(s.instore_sales),
  'App sales (£)': r2(s.app_sales),
  'Delivery sales (£)': r2(s.delivery_sales),
});

const pnlRow = (label, s, key = 'Store') => ({
  [key]: label,
  'Gross sales (£)': r2(s.gross_sales),
  'Discounts (£)': r2(s.discounts),
  'Net sales (£)': r2(s.net_sales),
  'COGS (£)': r2(s.cogs),
  'Gross profit (£)': r2(s.gross_profit),
  'Expenses (£)': r2(s.expenses),
  'Net profit (£)': r2(s.net_profit),
  'Net margin': r2(s.net_margin * 100) / 100,
  'Wastage (£, inside COGS)': r2(s.wastage),
});

const expenseRow = (label, s, key = 'Store') => ({
  [key]: label,
  'Labour (£)': r2(s.labour),
  'Delivery commission (£)': r2(s.delivery_commission),
  'Delivery packaging (£)': r2(s.delivery_packaging),
  'Rent (£)': r2(s.rent),
  'Business rates (£)': r2(s.business_rates),
  'Utilities (£)': r2(s.utilities),
  'Repairs & maintenance (£)': r2(s.repairs),
  'Other opex (£)': r2(s.other_opex),
  'Total expenses (£)': r2(s.expenses),
});

const fileStamp = (scope, range) => `grind-crumb_${scope.replace(/[^a-z0-9]+/gi, '-').toLowerCase()}_${range.from}_to_${range.to}`;

export function exportOverview(agg, scope, range) {
  const wb = XLSX.utils.book_new();
  const t = agg.total;
  XLSX.utils.book_append_sheet(wb, sheet([
    ...scopeRows(scope, range),
    { Field: 'Orders', Value: Math.round(t.orders) },
    { Field: 'Walk-in orders', Value: t.instore_orders },
    { Field: 'App orders', Value: t.app_orders },
    { Field: 'Delivery orders', Value: t.delivery_orders },
    { Field: 'Avg order value (£)', Value: r2(t.aov) },
    { Field: 'Net sales (£)', Value: r2(t.net_sales) },
    { Field: 'Peak hour', Value: agg.peakHour == null ? '' : `${agg.peakHour}:00–${agg.peakHour + 1}:00` },
  ], [24, 70]), 'Summary');
  XLSX.utils.book_append_sheet(wb, sheet(Object.entries(agg.byStore).map(([id, s]) => storeRow(id, s)), [28, 10, 14, 11, 15, 18, 15, 17, 14, 17]), 'By store');
  XLSX.utils.book_append_sheet(wb, sheet(agg.days.map((d) => ({ Date: d.date, ...storeRow('', d), Store: undefined })).map(({ Store, ...r }) => r), [12]), 'By day');
  XLSX.utils.book_append_sheet(wb, sheet(agg.hourly.map((h) => ({ Hour: `${h.hour}:00–${h.hour + 1}:00`, 'Orders (est.)': Math.round(h.orders), 'Net sales (£, est.)': r2(h.sales) })), [14, 14, 18]), 'By hour');
  save(wb, fileStamp(scope, range) + '_overview');
}

export function exportSales(agg, scope, range) {
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, sheet(scopeRows(scope, range), [12, 70]), 'About');
  XLSX.utils.book_append_sheet(wb, sheet(Object.entries(agg.byStore).map(([id, s]) => ({ ...storeRow(id, s), 'Gross sales (£)': r2(s.gross_sales), 'Discounts (£)': r2(s.discounts) })), [28]), 'Sales by store');
  XLSX.utils.book_append_sheet(wb, sheet(agg.days.map((d) => ({ Date: d.date, 'Gross sales (£)': r2(d.gross_sales), 'Discounts (£)': r2(d.discounts), 'Net sales (£)': r2(d.net_sales), 'In-store (£)': r2(d.instore_sales), 'App (£)': r2(d.app_sales), 'Delivery (£)': r2(d.delivery_sales), Orders: Math.round(d.orders) })), [12]), 'Sales by day');
  save(wb, fileStamp(scope, range) + '_sales');
}

export function exportExpenses(agg, scope, range) {
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, sheet(scopeRows(scope, range), [12, 70]), 'About');
  XLSX.utils.book_append_sheet(wb, sheet([...Object.entries(agg.byStore).map(([id, s]) => expenseRow(storeName(id), s)), expenseRow('Total', agg.total)], [28]), 'Expenses by store');
  XLSX.utils.book_append_sheet(wb, sheet(agg.days.map((d) => expenseRow(d.date, d, 'Date')), [12]), 'Expenses by day');
  save(wb, fileStamp(scope, range) + '_expenses');
}

export function exportPnl(agg, scope, range) {
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, sheet(scopeRows(scope, range), [12, 70]), 'About');
  XLSX.utils.book_append_sheet(wb, sheet([pnlRow(scope, agg.total, 'Scope')], [28]), 'P&L summary');
  XLSX.utils.book_append_sheet(wb, sheet([...Object.entries(agg.byStore).map(([id, s]) => pnlRow(storeName(id), s)), pnlRow('Total', agg.total)], [28]), 'P&L by store');
  XLSX.utils.book_append_sheet(wb, sheet(agg.days.map((d) => pnlRow(d.date, d, 'Date')), [12]), 'P&L by day');
  XLSX.utils.book_append_sheet(wb, sheet([...Object.entries(agg.byStore).map(([id, s]) => expenseRow(storeName(id), s)), expenseRow('Total', agg.total)], [28]), 'Expenses by store');
  save(wb, fileStamp(scope, range) + '_profit-and-loss');
}

export function exportChat(messages) {
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, sheet(messages.map((m) => ({ From: m.role === 'assistant' ? 'AI advisor' : 'CEO', Message: m.text })), [12, 120]), 'Conversation');
  save(wb, `grind-crumb_ai-advisor_${new Date().toISOString().slice(0, 10)}`);
}

export { HOURS };
