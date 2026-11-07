"""
Deep Inspection of Anomaly Details
"""
import os
import pandas as pd
import numpy as np

DATA_DIR = r"c:\Users\prasa\Downloads\hackathon techvision\data files"

# 1. Duplicates in transactions
txn = pd.read_csv(os.path.join(DATA_DIR, "transactions.csv"), low_memory=False)
dup_txn = txn[txn.duplicated(keep=False)]
print(f"Transactions duplicate rows total: {len(dup_txn)}")
print("Sample duplicate transactions:")
print(dup_txn.head(6))

# 2. Duplicates in transaction_lines
lines = pd.read_csv(os.path.join(DATA_DIR, "transaction_lines.csv"), low_memory=False)
dup_lines = lines[lines.duplicated(keep=False)]
print(f"Lines duplicate rows total: {len(dup_lines)}")
print("Sample duplicate lines:")
print(dup_lines.head(6))

# 3. Duplicates in loyalty_customers
loyalty = pd.read_csv(os.path.join(DATA_DIR, "loyalty_customers.csv"))
dup_loyalty = loyalty[loyalty.duplicated(keep=False)]
print(f"Loyalty duplicate rows total: {len(dup_loyalty)}")
print(f"Unique duplicate customer_ids: {dup_loyalty['customer_id'].nunique()}")
print("Sample duplicate loyalty:")
print(dup_loyalty.head(6))

# 4. Negative lines in transaction_lines
neg_lines = lines[lines['line_total_gbp'] < 0]
print(f"\nBreakdown of product_id for negative line totals:")
print(neg_lines['product_id'].value_counts())
print("\nSample negative lines with receipt info:")
print(neg_lines.head(6))

# 5. Waste log nulls
waste = pd.read_csv(os.path.join(DATA_DIR, "waste_log.csv"))
waste_nulls = waste[waste['units_wasted'].isnull()]
print(f"\nWaste log nulls in units_wasted: {len(waste_nulls)}")
print(waste_nulls.head(10))
print(f"Est cost wasted when units_wasted is null: {waste_nulls['est_cost_wasted_gbp'].value_counts(dropna=False)}")

# 6. Rota week allocation across months
rota = pd.read_csv(os.path.join(DATA_DIR, "staff_rota_weekly.csv"))
rota['week_start'] = pd.to_datetime(rota['week_start'])
print(f"\nRota week_start min: {rota['week_start'].min()}, max: {rota['week_start'].max()}")
# Unique weeks
weeks = rota['week_start'].drop_duplicates().sort_values()
print(f"Total weeks: {len(weeks)}")
print(f"First 3 weeks: {list(weeks[:3])}")
print(f"Last 3 weeks: {list(weeks[-3:])}")

# 7. Products available dates and check transactions outside availability
products = pd.read_csv(os.path.join(DATA_DIR, "products.csv"))
seasonal = products[products['available_from'].notnull() | products['available_to'].notnull()]
print("\nSeasonal / restricted products:")
print(seasonal[['product_id', 'product_name', 'available_from', 'available_to', 'menu_price_gbp', 'unit_cost_gbp']])

