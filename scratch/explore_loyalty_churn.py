import pandas as pd

loyalty = pd.read_csv('data files/loyalty_customers.csv').drop_duplicates(subset=['customer_id'])
tx = pd.read_csv('data files/transactions.csv').drop_duplicates(subset=['receipt_id'])
tx['timestamp'] = pd.to_datetime(tx['timestamp'])
tx['date'] = tx['timestamp'].dt.date
tx['month'] = tx['timestamp'].dt.to_period('M')

# Merge loyalty with transactions
tx_loyalty = tx[tx['customer_id'].notna()].copy()
print(f"Total loyalty members: {len(loyalty)}")
print(f"Loyalty transactions in 10% sample: {len(tx_loyalty)} ({len(tx_loyalty)/len(tx)*100:.1f}% of sample tx)")

# Find active members by month in sample
active_per_month = tx_loyalty.groupby('month')['customer_id'].nunique()
print("\nUnique active loyalty customers per month in 10% sample:")
print(active_per_month)

# Customer level: last transaction date, first transaction date, visit count
cust_stats = tx_loyalty.groupby('customer_id').agg(
    first_tx=('timestamp', 'min'),
    last_tx=('timestamp', 'max'),
    n_tx=('receipt_id', 'count'),
    total_spend=('net_gbp', 'sum')
).reset_index()

# Check when last transaction occurred:
# Did customer have transactions in H1 (Jul-Dec 2025) but none in Q2 2026 (Apr-Jun 2026)?
h1_custs = set(tx_loyalty[tx_loyalty['timestamp'] < '2026-01-01']['customer_id'].unique())
q2_custs = set(tx_loyalty[tx_loyalty['timestamp'] >= '2026-04-01']['customer_id'].unique())
churned = h1_custs - q2_custs
print(f"\nLoyalty customers active in H1 2025: {len(h1_custs)}")
print(f"Of those, active in Q2 2026: {len(h1_custs & q2_custs)}")
print(f"Churned (no visit in Q2 2026): {len(churned)} ({len(churned)/len(h1_custs)*100:.1f}%)")

# Let's check oat milk drinkers in lines
lines = pd.read_csv('data files/transaction_lines.csv').drop_duplicates(subset=['receipt_id', 'line_no'])
oat_receipts = set(lines[lines['milk_option'] == 'Oat']['receipt_id'].unique())
tx_loyalty['had_oat'] = tx_loyalty['receipt_id'].isin(oat_receipts)
oat_drinkers = set(tx_loyalty[tx_loyalty['had_oat']]['customer_id'].unique())
non_oat_drinkers = h1_custs - oat_drinkers

print(f"\nOat milk drinkers in H1: {len(h1_custs & oat_drinkers)}, churn rate: {len((h1_custs & oat_drinkers) - q2_custs) / len(h1_custs & oat_drinkers) * 100:.1f}%")
print(f"Non-oat drinkers in H1: {len(non_oat_drinkers)}, churn rate: {len(non_oat_drinkers - q2_custs) / len(non_oat_drinkers) * 100:.1f}%")

# App users vs non-app users
app_custs = set(tx_loyalty[tx_loyalty['channel'] == 'App Click & Collect']['customer_id'].unique())
print(f"\nApp users in H1: {len(h1_custs & app_custs)}, churn rate: {len((h1_custs & app_custs) - q2_custs) / len(h1_custs & app_custs) * 100:.1f}%")
print(f"Non-app users in H1: {len(h1_custs - app_custs)}, churn rate: {len((h1_custs - app_custs) - q2_custs) / len(h1_custs - app_custs) * 100:.1f}%")

