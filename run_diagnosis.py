"""
Comprehensive Diagnosis Engine for Grind & Crumb
Executes all quantitative tests required for STEP 2.
"""
import os
import pandas as pd
import numpy as np

DATA_DIR = r"c:\Users\prasa\Downloads\hackathon techvision\data files"

stores = pd.read_csv(os.path.join(DATA_DIR, "stores.csv"))
daily = pd.read_csv(os.path.join(DATA_DIR, "daily_store_sales.csv"), parse_dates=['date'])
daily['total_net'] = daily['net_sales_instore_gbp'] + daily['net_sales_app_gbp'] + daily['net_sales_delivery_gbp']
daily['month'] = daily['date'].dt.to_period('M').dt.to_timestamp()

foot = pd.read_csv(os.path.join(DATA_DIR, "footfall.csv"), parse_dates=['date'])
foot['month'] = foot['date'].dt.to_period('M').dt.to_timestamp()

rota = pd.read_csv(os.path.join(DATA_DIR, "staff_rota_weekly.csv"), parse_dates=['week_start'])
rota['labour_cost'] = rota['scheduled_hours'] * rota['avg_hourly_wage_gbp'] * 1.13
rota['month'] = rota['week_start'].dt.to_period('M').dt.to_timestamp()

costs = pd.read_csv(os.path.join(DATA_DIR, "store_costs_monthly.csv"))
costs['month'] = pd.to_datetime(costs['month'], format='%Y-%m')

waste = pd.read_csv(os.path.join(DATA_DIR, "waste_log.csv"))
raw_waste_date = waste['date'].copy()
waste['date'] = pd.to_datetime(waste['date'], dayfirst=False, format='mixed')
non_iso = ~raw_waste_date.str.match(r'^\d{4}-\d{2}-\d{2}$', na=False)
waste.loc[non_iso, 'date'] = pd.to_datetime(raw_waste_date[non_iso], dayfirst=True, format='mixed')
waste['month'] = waste['date'].dt.to_period('M').dt.to_timestamp()

reviews = pd.read_csv(os.path.join(DATA_DIR, "customer_reviews.csv"), parse_dates=['review_date'])
staff_monthly = pd.read_csv(os.path.join(DATA_DIR, "staff_monthly.csv"))
staff_exit = pd.read_csv(os.path.join(DATA_DIR, "staff_exit_survey.csv"))
survey = pd.read_csv(os.path.join(DATA_DIR, "customer_survey.csv"))
catchment = pd.read_csv(os.path.join(DATA_DIR, "store_catchment.csv"))
candidates = pd.read_csv(os.path.join(DATA_DIR, "candidate_sites.csv"))
events = pd.read_csv(os.path.join(DATA_DIR, "business_events.csv"), parse_dates=['date'])
promos = pd.read_csv(os.path.join(DATA_DIR, "promotions.csv"))
products = pd.read_csv(os.path.join(DATA_DIR, "products.csv"))
weather = pd.read_csv(os.path.join(DATA_DIR, "weather.csv"), parse_dates=['date'])
loyalty = pd.read_csv(os.path.join(DATA_DIR, "loyalty_customers.csv"), parse_dates=['signup_date'])
txn = pd.read_csv(os.path.join(DATA_DIR, "transactions.csv"), parse_dates=['timestamp'], low_memory=False)

print("="*80)
print("TEST 1: LEEDS BRIGGATE (S03) VS LEEDS TRINITY (S12) CANNIBALISATION")
print("="*80)
# Check Briggate before Trinity (July-Aug 2025) vs after (Sep 2025 onwards)
s03_daily = daily[daily['store_id'] == 'S03'].copy()
s12_daily = daily[daily['store_id'] == 'S12'].copy()

s03_monthly = s03_daily.groupby('month').agg(
    total_sales=('total_net', 'sum'),
    instore_sales=('net_sales_instore_gbp', 'sum'),
    receipts_instore=('receipts_instore', 'sum')
).reset_index()

s12_monthly = s12_daily.groupby('month').agg(
    total_sales=('total_net', 'sum'),
    instore_sales=('net_sales_instore_gbp', 'sum'),
    receipts_instore=('receipts_instore', 'sum')
).reset_index()

# Footfall for S03 and S12
s03_foot = foot[foot['store_id'] == 'S03'].groupby('month')['door_count'].sum().reset_index()
s12_foot = foot[foot['store_id'] == 'S12'].groupby('month')['door_count'].sum().reset_index()

s03_merged = s03_monthly.merge(s03_foot, on='month')
s03_merged['conversion_rate'] = s03_merged['receipts_instore'] / s03_merged['door_count'] * 100
s03_merged['sales_per_visitor'] = s03_merged['instore_sales'] / s03_merged['door_count']

print("Briggate Monthly Trajectory:")
print(s03_merged[['month', 'total_sales', 'door_count', 'conversion_rate', 'sales_per_visitor']].to_string(index=False))

pre_trinity_sales = s03_merged[s03_merged['month'] < '2025-09-01']['total_sales'].mean()
post_trinity_sales = s03_merged[s03_merged['month'] >= '2025-09-01']['total_sales'].mean()
pre_trinity_foot = s03_merged[s03_merged['month'] < '2025-09-01']['door_count'].mean()
post_trinity_foot = s03_merged[s03_merged['month'] >= '2025-09-01']['door_count'].mean()

print(f"\nBriggate Pre-Trinity Avg Monthly Sales: £{pre_trinity_sales:,.2f}")
print(f"Briggate Post-Trinity Avg Monthly Sales: £{post_trinity_sales:,.2f} (Drop of £{pre_trinity_sales - post_trinity_sales:,.2f}/mo or {(post_trinity_sales/pre_trinity_sales - 1)*100:.1f}%)")
print(f"Briggate Pre-Trinity Avg Monthly Footfall: {pre_trinity_foot:,.0f}")
print(f"Briggate Post-Trinity Avg Monthly Footfall: {post_trinity_foot:,.0f} (Drop of {(post_trinity_foot/pre_trinity_foot - 1)*100:.1f}%)")

# Compare with other stores footfall trend over same period
other_foot = foot[~foot['store_id'].isin(['S03', 'S12'])].groupby('month')['door_count'].sum().reset_index()
other_pre = other_foot[other_foot['month'] < '2025-09-01']['door_count'].mean()
other_post = other_foot[other_foot['month'] >= '2025-09-01']['door_count'].mean()
print(f"Other 10 stores avg monthly footfall Pre vs Post Sep 2025: {other_pre:,.0f} vs {other_post:,.0f} (Change: {(other_post/other_pre - 1)*100:.1f}%)")

print("="*80)
print("TEST 2: MANCHESTER PICCADILLY (S07) PROFITABILITY & WALK-AWAYS")
print("="*80)
pic_sales = daily[daily['store_id'] == 'S07']['total_net'].sum()
pic_costs = costs[costs['store_id'] == 'S07']
pic_rent = pic_costs['rent_gbp'].sum()
pic_fixed = pic_costs[['rent_gbp', 'business_rates_gbp', 'utilities_gbp', 'repairs_maintenance_gbp', 'other_opex_gbp']].sum().sum()
pic_labour = rota[rota['store_id'] == 'S07']['labour_cost'].sum()
pic_waste = waste[waste['store_id'] == 'S07']['est_cost_wasted_gbp'].sum()

# Delivery cost for S07
s07_del_sales = daily[daily['store_id'] == 'S07']['net_sales_delivery_gbp'].sum()
s07_del_receipts = daily[daily['store_id'] == 'S07']['receipts_delivery'].sum()
# Commission rate ~30.5%, packaging 0.45, staff time 4 min * 12.50 * 1.13 = 0.9416 -> total non-rev cost = (0.45+0.9416)*receipts
pic_del_cost = s07_del_sales * 0.305 + s07_del_receipts * (0.45 + 0.9416)

pic_profit = pic_sales - (pic_labour + pic_fixed + pic_waste + pic_del_cost)
print(f"Piccadilly Total Revenue: £{pic_sales:,.2f}")
print(f"Piccadilly Rent: £{pic_rent:,.2f} ({pic_rent/pic_sales*100:.1f}% of revenue!)")
print(f"Piccadilly Labour: £{pic_labour:,.2f} ({pic_labour/pic_sales*100:.1f}% of revenue)")
print(f"Piccadilly Fixed Costs: £{pic_fixed:,.2f}")
print(f"Piccadilly Waste: £{pic_waste:,.2f}")
print(f"Piccadilly Delivery Costs: £{pic_del_cost:,.2f}")
print(f"Piccadilly True Store Operating Profit: £{pic_profit:,.2f} (Margin: {pic_profit/pic_sales*100:.1f}%)")

# Compare to York Stonegate (S04)
york_sales = daily[daily['store_id'] == 'S04']['total_net'].sum()
york_costs = costs[costs['store_id'] == 'S04']
york_rent = york_costs['rent_gbp'].sum()
york_fixed = york_costs[['rent_gbp', 'business_rates_gbp', 'utilities_gbp', 'repairs_maintenance_gbp', 'other_opex_gbp']].sum().sum()
york_labour = rota[rota['store_id'] == 'S04']['labour_cost'].sum()
york_waste = waste[waste['store_id'] == 'S04']['est_cost_wasted_gbp'].sum()
york_del_sales = daily[daily['store_id'] == 'S04']['net_sales_delivery_gbp'].sum()
york_del_receipts = daily[daily['store_id'] == 'S04']['receipts_delivery'].sum()
york_del_cost = york_del_sales * 0.305 + york_del_receipts * (0.45 + 0.9416)
york_profit = york_sales - (york_labour + york_fixed + york_waste + york_del_cost)

print(f"\nYork Stonegate Total Revenue: £{york_sales:,.2f}")
print(f"York Stonegate Rent: £{york_rent:,.2f} ({york_rent/york_sales*100:.1f}% of revenue)")
print(f"York Stonegate Profit: £{york_profit:,.2f} (Margin: {york_profit/york_sales*100:.1f}%)")
print(f"-> York generates £{york_profit - pic_profit:,.2f} MORE profit than Piccadilly on £{pic_sales - york_sales:,.2f} LESS revenue!")

# Piccadilly Rota vs Footfall by Daypart
pic_foot = foot[foot['store_id'] == 'S07'].groupby('daypart')['door_count'].sum()
pic_rota = rota[rota['store_id'] == 'S07'].groupby('daypart')['scheduled_hours'].sum()
pic_f_r = pd.DataFrame({'footfall': pic_foot, 'scheduled_hours': pic_rota})
pic_f_r['visitors_per_hour'] = pic_f_r['footfall'] / pic_f_r['scheduled_hours']
print("\nPiccadilly Daypart Stress Test:")
print(pic_f_r)

# Compare with chain average visitors per hour by daypart
chain_foot = foot.groupby('daypart')['door_count'].sum()
chain_rota = rota.groupby('daypart')['scheduled_hours'].sum()
chain_f_r = pd.DataFrame({'footfall': chain_foot, 'scheduled_hours': chain_rota})
chain_f_r['chain_visitors_per_hour'] = chain_f_r['footfall'] / chain_f_r['scheduled_hours']
print("\nChain Average Daypart:")
print(chain_f_r)

print("="*80)
print("TEST 3: HULL PARAGON (S10) WASTE & MAINTENANCE DRAG")
print("="*80)
hull_waste = waste[waste['store_id'] == 'S10']
hull_prepared = hull_waste['units_prepared'].sum()
hull_wasted = hull_waste['units_wasted'].sum()
hull_waste_cost = hull_waste['est_cost_wasted_gbp'].sum()
hull_waste_rate = hull_wasted / hull_prepared * 100

chain_prepared = waste['units_prepared'].sum()
chain_wasted = waste['units_wasted'].sum()
chain_waste_cost = waste['est_cost_wasted_gbp'].sum()
chain_waste_rate = chain_wasted / chain_prepared * 100

print(f"Hull Units Prepared: {hull_prepared:,}, Units Wasted: {hull_wasted:,.0f} ({hull_waste_rate:.2f}% waste rate)")
print(f"Chain Units Prepared: {chain_prepared:,}, Units Wasted: {chain_wasted:,.0f} ({chain_waste_rate:.2f}% waste rate)")
print(f"Hull Waste Cost: £{hull_waste_cost:,.2f} (out of chain total £{chain_waste_cost:,.2f} or {hull_waste_cost/chain_waste_cost*100:.1f}%!)")

# Repairs at Hull vs other stores
hull_repairs = costs[costs['store_id'] == 'S10']['repairs_maintenance_gbp'].sum()
avg_repairs = costs[costs['store_id'] != 'S10'].groupby('store_id')['repairs_maintenance_gbp'].sum().mean()
print(f"Hull Annual Repairs & Maintenance: £{hull_repairs:,.2f}")
print(f"Average Other Store Repairs: £{avg_repairs:,.2f} (Hull is {hull_repairs/avg_repairs:.1f}x higher!)")

print("="*80)
print("TEST 4: APP V3.0 RELEASE (2 MARCH 2026) VS V3.1 HOTFIX (13 APRIL 2026)")
print("="*80)
# App channel revenue by week/month
app_weekly = daily.set_index('date').resample('W-MON').agg(
    app_sales=('net_sales_app_gbp', 'sum'),
    app_receipts=('receipts_app', 'sum'),
    total_sales=('total_net', 'sum')
).reset_index()
app_weekly['app_share'] = app_weekly['app_sales'] / app_weekly['total_sales'] * 100

print("App Sales Trend around March 2, 2026 release:")
app_focus = app_weekly[(app_weekly['date'] >= '2026-01-15') & (app_weekly['date'] <= '2026-05-15')]
print(app_focus[['date', 'app_sales', 'app_receipts', 'app_share']].to_string(index=False))

# Customer reviews before, during bug period, and after fix
reviews['review_date'] = pd.to_datetime(reviews['review_date'])
rev_pre = reviews[reviews['review_date'] < '2026-03-02']
rev_bug = reviews[(reviews['review_date'] >= '2026-03-02') & (reviews['review_date'] < '2026-04-13')]
rev_post = reviews[reviews['review_date'] >= '2026-04-13']

print(f"\nReviews Pre-App v3.0 (before Mar 2): {len(rev_pre)} reviews, Mean Rating: {rev_pre['rating'].mean():.2f}")
print(f"Reviews During App v3.0 Bug Period (Mar 2 - Apr 13): {len(rev_bug)} reviews, Mean Rating: {rev_bug['rating'].mean():.2f}")
print(f"Reviews Post App v3.1 Hotfix (Apr 13 onwards): {len(rev_post)} reviews, Mean Rating: {rev_post['rating'].mean():.2f}")

# Mentions of app keywords
app_kw = ['app', 'stamp', 'crash', 'freeze', 'disappeared', 'bug', 'glitch']
rev_bug['is_app_mention'] = rev_bug['review_text'].fillna('').str.lower().apply(lambda x: any(k in x for k in app_kw))
print(f"App-related negative reviews during bug period: {rev_bug['is_app_mention'].sum()} out of {len(rev_bug)} ({rev_bug['is_app_mention'].mean()*100:.1f}%)")

print("="*80)
print("TEST 5: OAT MILK SURCHARGE (12 JAN 2026) ELASTICITY & REACTION")
print("="*80)
# Oat milk sales in transaction lines before and after 2026-01-12
lines = pd.read_csv(os.path.join(DATA_DIR, "transaction_lines.csv"), low_memory=False)
lines_merged = lines.merge(txn[['receipt_id', 'timestamp']], on='receipt_id')
lines_merged['date'] = lines_merged['timestamp'].dt.date
lines_merged['is_oat'] = lines_merged['milk_option'] == 'Oat'
lines_merged['is_milk'] = lines_merged['milk_option'].notnull()

daily_milk = lines_merged[lines_merged['is_milk']].groupby(['date', 'milk_option']).size().unstack(fill_value=0)
daily_milk['total'] = daily_milk.sum(axis=1)
daily_milk['oat_share'] = daily_milk['Oat'] / daily_milk['total'] * 100

pre_oat_share = daily_milk[daily_milk.index < pd.to_datetime('2026-01-12').date()]['oat_share'].mean()
post_oat_share = daily_milk[daily_milk.index >= pd.to_datetime('2026-01-12').date()]['oat_share'].mean()
print(f"Oat milk share of milk drinks Pre-Charge (before Jan 12): {pre_oat_share:.2f}%")
print(f"Oat milk share of milk drinks Post-Charge (after Jan 12): {post_oat_share:.2f}% (Drop of {pre_oat_share - post_oat_share:.2f} percentage points)")

# Revenue from oat surcharge
oat_lines = lines_merged[(lines_merged['date'] >= pd.to_datetime('2026-01-12').date()) & lines_merged['is_oat']]
sample_surcharge_rev = (oat_lines['modifier_gbp']).sum()
print(f"Surcharge collected in 10% sample: £{sample_surcharge_rev:,.2f}")
print(f"Estimated full year annualised surcharge revenue: £{sample_surcharge_rev * 10 * (365 / 170):,.2f}")

print("="*80)
print("TEST 6: STAFF TURNOVER & EXIT REASONS")
print("="*80)
turnover_by_store = staff_monthly.groupby('store_id').agg(
    leavers=('leavers', 'sum'),
    avg_headcount=('headcount', 'mean'),
    avg_score=('staff_survey_score_10', 'mean')
).reset_index()
turnover_by_store['turnover_rate'] = turnover_by_store['leavers'] / turnover_by_store['avg_headcount'] * 100
turnover_by_store = turnover_by_store.merge(stores[['store_id', 'store_name']], on='store_id')
print(turnover_by_store[['store_name', 'leavers', 'avg_headcount', 'turnover_rate', 'avg_score']].sort_values('turnover_rate', ascending=False).to_string(index=False))

print("\nStaff Exit Survey Reasons across chain:")
print(staff_exit['main_reason'].value_counts())
print("\nStaff Exit Survey Reasons at Manchester Piccadilly (S07):")
print(staff_exit[staff_exit['store_id'] == 'S07']['main_reason'].value_counts())

print("="*80)
print("TEST 7: DELIVERY PLATFORM UNIT ECONOMICS")
print("="*80)
del_txns = txn[txn['channel'] == 'Delivery']
print(f"Total delivery receipts in 10% sample: {len(del_txns)}")
print("Delivery partner counts in sample:")
print(del_txns['delivery_partner'].value_counts())

# Dashly pre and post April 1, 2026
dashly_pre = del_txns[(del_txns['delivery_partner'] == 'Dashly') & (del_txns['timestamp'] < '2026-04-01')]
dashly_post = del_txns[(del_txns['delivery_partner'] == 'Dashly') & (del_txns['timestamp'] >= '2026-04-01')]
rusheats = del_txns[del_txns['delivery_partner'] == 'RushEats']

print(f"Dashly pre-Apr avg order: £{dashly_pre['net_gbp'].mean():.2f}, post-Apr avg order: £{dashly_post['net_gbp'].mean():.2f}")
print(f"RushEats avg order: £{rusheats['net_gbp'].mean():.2f}")

print("\nDIAGNOSIS COMPLETE.")
