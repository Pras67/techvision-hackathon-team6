"""Turn the Grind & Crumb data pack (CSVs) into the compact JSON the dashboard loads.

Usage: python scripts/build_data.py <folder with the CSVs>

Cleaning applied (see README "Data notes"):
- transactions / lines: exact duplicate rows dropped; refunds (-RF) kept as negatives;
  the 7 flat white lines priced £35 on 14 Mar 2026 (York) corrected to £3.50.
- waste_log: 273 Hull rows written DD/MM/YYYY parsed day-first.
- Daily sales totals come from daily_store_sales.csv (full data). The 10% receipt sample is
  only used for the shape of the day (share of sales and orders per hour) and discount rates.
- Monthly costs from the starter P&L are spread across trading days: food cost and delivery
  costs in proportion to that day's sales/orders, fixed costs and labour evenly.
  Summing any month gives back the starter P&L exactly.
"""
import json, sys, pathlib
import numpy as np, pandas as pd

src = pathlib.Path(sys.argv[1]); out = pathlib.Path(__file__).resolve().parent.parent / 'src' / 'data'
P = pd.read_csv(src / 'starter_store_monthly_pnl.csv')
stores = pd.read_csv(src / 'stores.csv')
ds = pd.read_csv(src / 'daily_store_sales.csv'); ds['month'] = ds.date.str[:7]
ds['net'] = ds.net_sales_instore_gbp + ds.net_sales_app_gbp + ds.net_sales_delivery_gbp

# waste (daily, actual)
w = pd.read_csv(src / 'waste_log.csv')
iso = w.date.str.match(r'^\d{4}-')
w['d'] = pd.NaT
w.loc[iso, 'd'] = pd.to_datetime(w.loc[iso, 'date'], format='%Y-%m-%d')
w.loc[~iso, 'd'] = pd.to_datetime(w.loc[~iso, 'date'], format='%d/%m/%Y')
w['date'] = pd.to_datetime(w.d).dt.strftime('%Y-%m-%d')
waste = w.groupby(['store_id', 'date']).est_cost_wasted_gbp.sum()

# receipt sample: hourly shape + discount rate
t = pd.read_csv(src / 'transactions.csv').drop_duplicates()
l = pd.read_csv(src / 'transaction_lines.csv').drop_duplicates()
bad = l[l.unit_price_gbp == 35].groupby('receipt_id').size() * 31.5
t = t.set_index('receipt_id'); t.loc[bad.index, ['gross_gbp', 'net_gbp']] -= bad.values[:, None]; t = t.reset_index()
ts = pd.to_datetime(t.timestamp); t['date'] = ts.dt.strftime('%Y-%m-%d'); t['hour'] = ts.dt.hour.clip(7, 17)
t['month'] = t.date.str[:7]
HOURS = list(range(7, 18))
sale = t[~t.receipt_id.str.endswith('-RF')]
hs = sale.pivot_table(index=['store_id', 'date'], columns='hour', values='net_gbp', aggfunc='sum', fill_value=0).reindex(columns=HOURS, fill_value=0)
hr = sale.pivot_table(index=['store_id', 'date'], columns='hour', values='net_gbp', aggfunc='size', fill_value=0).reindex(columns=HOURS, fill_value=0)
store_shape_s = hs.groupby(level=0).sum(); store_shape_r = hr.groupby(level=0).sum()
disc = sale.groupby(['store_id', 'month'])[['gross_gbp', 'discount_gbp']].sum()
disc_rate = (disc.discount_gbp / disc.gross_gbp)

pm = P.set_index(['store_id', 'month'])
days_in = ds.groupby(['store_id', 'month']).size()
del_rcp = ds.groupby(['store_id', 'month']).receipts_delivery.sum()
del_sales = ds.groupby(['store_id', 'month']).net_sales_delivery_gbp.sum()

def shape(series_row, fallback):
    v = np.asarray(series_row, dtype=float)
    if v.sum() <= 0: v = np.asarray(fallback, dtype=float)
    return v / v.sum()

data = {}
for r in ds.itertuples():
    k = (r.store_id, r.month); p = pm.loc[k]; n = days_in.loc[k]
    net = r.net
    ratio_food = p.food_cost_gbp / p.total_sales_gbp
    comm = p.delivery_commission_gbp * (r.net_sales_delivery_gbp / del_sales.loc[k] if del_sales.loc[k] else 0)
    pack = p.delivery_packaging_gbp * (r.receipts_delivery / del_rcp.loc[k] if del_rcp.loc[k] else 0)
    dr = disc_rate.get(k, 0.0)
    gross = net / (1 - dr) if dr < 1 else net
    key = (r.store_id, r.date)
    s_shape = shape(hs.loc[key] if key in hs.index else [], store_shape_s.loc[r.store_id])
    r_shape = shape(hr.loc[key] if key in hr.index else [], store_shape_r.loc[r.store_id])
    receipts = r.receipts_instore + r.receipts_app + r.receipts_delivery
    data.setdefault(r.store_id, {})[r.date] = [
        int(r.receipts_instore), int(r.receipts_app), int(r.receipts_delivery),
        round(r.net_sales_instore_gbp, 2), round(r.net_sales_app_gbp, 2), round(r.net_sales_delivery_gbp, 2),
        round(gross - net, 2),                          # discounts (estimated)
        round(float(waste.get(key, 0.0)), 2),           # wastage (actual, already inside COGS)
        round(net * ratio_food, 2),                     # COGS
        round(p.labour_cost_gbp / n, 2),
        round(comm, 2), round(pack, 2),
        round(p.rent_gbp / n, 2), round(p.business_rates_gbp / n, 2), round(p.utilities_gbp / n, 2),
        round(p.repairs_maintenance_gbp / n, 2), round(p.other_opex_gbp / n, 2),
        [round(net * x, 2) for x in s_shape],           # sales by hour 07..17
        [round(receipts * x, 1) for x in r_shape],      # orders by hour 07..17
    ]

meta = {
    'fields': ['instore_orders', 'app_orders', 'delivery_orders', 'instore_sales', 'app_sales', 'delivery_sales',
               'discounts', 'wastage', 'cogs', 'labour', 'delivery_commission', 'delivery_packaging',
               'rent', 'business_rates', 'utilities', 'repairs', 'other_opex', 'hourly_sales', 'hourly_orders'],
    'hours': HOURS,
    'firstDate': ds.date.min(), 'lastDate': ds.date.max(),
    'stores': stores[['store_id', 'store_name', 'city', 'format', 'location_type', 'store_manager', 'opened_date']].to_dict('records'),
}
(out / 'meta.json').write_text(json.dumps(meta))
(out / 'daily.json').write_text(json.dumps(data, separators=(',', ':')))
print('stores', len(data), 'rows', sum(len(v) for v in data.values()), 'bytes', (out / 'daily.json').stat().st_size)
