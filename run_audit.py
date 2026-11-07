"""
Comprehensive Data Audit Script for Grind & Crumb Hackathon
"""
import os
import pandas as pd
import numpy as np

DATA_DIR = r"c:\Users\prasa\Downloads\hackathon techvision\data files"

files = [
    "stores.csv",
    "products.csv",
    "daily_store_sales.csv",
    "transactions.csv",
    "transaction_lines.csv",
    "footfall.csv",
    "weather.csv",
    "loyalty_customers.csv",
    "staff_rota_weekly.csv",
    "staff_monthly.csv",
    "waste_log.csv",
    "store_costs_monthly.csv",
    "capex.csv",
    "promotions.csv",
    "delivery_partner_terms.csv",
    "customer_reviews.csv",
    "customer_survey.csv",
    "staff_exit_survey.csv",
    "store_catchment.csv",
    "candidate_sites.csv",
    "business_events.csv"
]

print("="*80)
print("GRIND & CRUMB DATA AUDIT REPORT")
print("="*80)

audit_results = []

for filename in files:
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        print(f"MISSING: {filename}")
        continue
    
    # Read raw
    df = pd.read_csv(path, low_memory=False)
    
    row_count = len(df)
    col_count = len(df.columns)
    cols = list(df.columns)
    
    # Date detection
    date_cols = [c for c in cols if 'date' in c.lower() or 'month' in c.lower() or 'timestamp' in c.lower() or 'valid' in c.lower() or 'week' in c.lower()]
    date_ranges = {}
    for dc in date_cols:
        try:
            # check min max
            valid_dates = df[dc].dropna()
            if len(valid_dates) > 0:
                date_ranges[dc] = (str(valid_dates.min()), str(valid_dates.max()))
        except Exception as e:
            date_ranges[dc] = f"Error: {e}"
            
    # Nulls
    null_counts = df.isnull().sum()
    cols_with_nulls = null_counts[null_counts > 0].to_dict()
    
    # Duplicates
    dup_rows = df.duplicated().sum()
    
    print(f"\n--- {filename} ---")
    print(f"Rows: {row_count:,} | Cols: {col_count} | Duplicates: {dup_rows}")
    print(f"Columns: {cols}")
    if date_ranges:
        print(f"Date Ranges: {date_ranges}")
    if cols_with_nulls:
        print(f"Nulls: {cols_with_nulls}")
    else:
        print("Nulls: None")
        
    audit_results.append({
        'file': filename,
        'rows': row_count,
        'cols': col_count,
        'nulls': cols_with_nulls,
        'dups': dup_rows,
        'date_ranges': date_ranges
    })

print("\n" + "="*80)
print("DETAILED INTEGRITY & ANOMALY CHECKS")
print("="*80)

# 1. Transactions negative values / impossible values
txn = pd.read_csv(os.path.join(DATA_DIR, "transactions.csv"), low_memory=False)
neg_gross = (txn['gross_gbp'] < 0).sum()
neg_net = (txn['net_gbp'] < 0).sum()
neg_disc = (txn['discount_gbp'] < 0).sum()
print(f"Transactions: {len(txn):,} rows. Negative gross: {neg_gross}, Negative net: {neg_net}, Negative discount: {neg_disc}")
if neg_net > 0:
    print("Negative net samples:")
    print(txn[txn['net_gbp'] < 0].head(5)[['receipt_id', 'channel', 'delivery_partner', 'gross_gbp', 'discount_gbp', 'net_gbp']])

# 2. Transaction lines
lines = pd.read_csv(os.path.join(DATA_DIR, "transaction_lines.csv"), low_memory=False)
neg_lines = (lines['line_total_gbp'] < 0).sum()
print(f"Transaction Lines: {len(lines):,} rows. Negative line totals: {neg_lines}")
print(f"MEALDEAL lines count: {(lines['product_id'] == 'MEALDEAL').sum()}")
if neg_lines > 0:
    print("Negative lines sample:")
    print(lines[lines['line_total_gbp'] < 0].head(5))

# 3. Waste log mixed formats
waste = pd.read_csv(os.path.join(DATA_DIR, "waste_log.csv"))
non_iso = (~waste['date'].str.match(r'^\d{4}-\d{2}-\d{2}$', na=False)).sum()
print(f"Waste log: {len(waste):,} rows. Non-ISO date format count: {non_iso}")

# 4. Daily store sales reconciliation
daily = pd.read_csv(os.path.join(DATA_DIR, "daily_store_sales.csv"))
print(f"Daily sales: {len(daily):,} rows. Date range: {daily['date'].min()} to {daily['date'].max()}")
daily['total_net'] = daily['net_sales_instore_gbp'] + daily['net_sales_app_gbp'] + daily['net_sales_delivery_gbp']
print(f"Total Chain Net Sales: £{daily['total_net'].sum():,.2f}")
print(f"Total In-store: £{daily['net_sales_instore_gbp'].sum():,.2f}")
print(f"Total App: £{daily['net_sales_app_gbp'].sum():,.2f}")
print(f"Total Delivery: £{daily['net_sales_delivery_gbp'].sum():,.2f}")

# 5. Store costs monthly
costs = pd.read_csv(os.path.join(DATA_DIR, "store_costs_monthly.csv"))
print(f"Store costs: {len(costs)} rows. Total rent: £{costs['rent_gbp'].sum():,.2f}")
print(f"Rates: £{costs['business_rates_gbp'].sum():,.2f}, Utilities: £{costs['utilities_gbp'].sum():,.2f}, Repairs: £{costs['repairs_maintenance_gbp'].sum():,.2f}, Other: £{costs['other_opex_gbp'].sum():,.2f}")

# 6. Staff rota weekly
rota = pd.read_csv(os.path.join(DATA_DIR, "staff_rota_weekly.csv"))
rota['labour_cost'] = rota['scheduled_hours'] * rota['avg_hourly_wage_gbp'] * 1.13
print(f"Staff rota: {len(rota):,} rows. Total Labour Cost: £{rota['labour_cost'].sum():,.2f}")
print(f"Date range: {rota['week_start'].min()} to {rota['week_start'].max()}")

# 7. Footfall
foot = pd.read_csv(os.path.join(DATA_DIR, "footfall.csv"))
print(f"Footfall: {len(foot):,} rows. Total door count: {foot['door_count'].sum():,}")

# 8. Stores
stores = pd.read_csv(os.path.join(DATA_DIR, "stores.csv"))
print(f"Stores count: {len(stores)}")
print(stores[['store_id', 'store_name', 'format', 'location_type', 'rent_gbp_month', 'refit_year']])

print("\nAUDIT CHECK COMPLETE.")
