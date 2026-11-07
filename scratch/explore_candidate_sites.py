import pandas as pd
import numpy as np

cs = pd.read_csv('data files/candidate_sites.csv')
stores = pd.read_csv('data files/stores.csv')
catchment = pd.read_csv('data files/store_catchment.csv')
dss = pd.read_csv('data files/daily_store_sales.csv')

# Existing store sales
sales = dss.groupby('store_id').agg({
    'net_sales_instore_gbp': 'sum',
    'net_sales_app_gbp': 'sum',
    'net_sales_delivery_gbp': 'sum'
}).sum(axis=1).reset_index().rename(columns={0: 'annual_sales'})

existing = stores.merge(catchment, on='store_id').merge(sales, on='store_id')
existing['sales_per_sqft'] = existing['annual_sales'] / existing['sqft']
existing['rent_annual'] = existing['rent_gbp_month'] * 12
existing['rent_pct_sales'] = existing['rent_annual'] / existing['annual_sales'] * 100

print("=== EXISTING STORE BENCHMARKS ===")
print(existing[['store_id', 'store_name', 'city', 'format', 'sqft', 'annual_sales', 'sales_per_sqft', 'rent_annual', 'rent_pct_sales']].round(1).to_string(index=False))

print("\n=== CANDIDATE SITES ===")
cs['annual_rent'] = cs['quoted_rent_gbp_month'] * 12
print(cs[['site_id', 'site_name', 'city', 'location_type', 'sqft', 'quoted_rent_gbp_month', 'annual_rent', 'est_fitout_gbp', 'daily_footfall_street', 'office_workers_500m', 'students_1km', 'competitor_cafes_500m']].to_string(index=False))

