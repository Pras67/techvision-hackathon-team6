"""
Candidate Sites Detailed Evaluation Script
"""
import os
import pandas as pd
import numpy as np

DATA_DIR = r"c:\Users\prasa\Downloads\hackathon techvision\data files"

cands = pd.read_csv(os.path.join(DATA_DIR, "candidate_sites.csv"))
stores = pd.read_csv(os.path.join(DATA_DIR, "stores.csv"))
catchment = pd.read_csv(os.path.join(DATA_DIR, "store_catchment.csv"))
daily = pd.read_csv(os.path.join(DATA_DIR, "daily_store_sales.csv"))
daily['total_net'] = daily['net_sales_instore_gbp'] + daily['net_sales_app_gbp'] + daily['net_sales_delivery_gbp']
store_rev = daily.groupby('store_id')['total_net'].sum().reset_index()

existing = stores.merge(catchment, on='store_id').merge(store_rev, on='store_id')
existing['annual_rent'] = existing['rent_gbp_month'] * 12
existing['rent_to_sales'] = existing['annual_rent'] / existing['total_net'] * 100

print("EXISTING STORES BENCHMARK:")
print(existing[['store_id', 'store_name', 'location_type', 'sqft', 'daily_footfall_street', 'office_workers_500m', 'students_1km', 'competitor_cafes_500m', 'total_net', 'rent_to_sales']].to_string(index=False))

print("\nCANDIDATE SITES:")
cands['annual_rent'] = cands['quoted_rent_gbp_month'] * 12
print(cands[['site_id', 'site_name', 'city', 'location_type', 'sqft', 'quoted_rent_gbp_month', 'annual_rent', 'daily_footfall_street', 'office_workers_500m', 'students_1km', 'competitor_cafes_500m', 'est_fitout_gbp']].to_string(index=False))

# Look at Wellington Place (CS7):
# City: Leeds (Already has Briggate S03 and Trinity S12!). Opening a 3rd store in Leeds centre risks triple-cannibalisation!
# But office_workers_500m = 18,200!
# Look at Kelham Island (CS2): Sheffield (S01 Division Street, S02 Station, S11 Uni Campus).
# Look at Manchester Oxford Road (CS3): Manchester (Already has NQ S05, Spinningfields S06, Piccadilly S07).
# Look at Liverpool Bold Street (CS5): New city, 33k footfall, 16 competitors, high rent (£11.2k/mo), fitout £410k.
# Look at York Station (CS4): 39k footfall, 2 competitors, low fitout (£180k), but rent £12.9k for only 600 sqft!
