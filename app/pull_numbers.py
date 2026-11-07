"""Pull key numbers for the executive report."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import pandas as pd
import numpy as np
from data_engine import (
    load_stores, load_daily_sales, load_transactions,
    load_delivery_terms, load_waste, load_staff_monthly,
    load_catchment, load_candidate_sites, load_reviews,
    build_store_pnl, get_commission_rate
)

pnl    = build_store_pnl()
daily  = load_daily_sales()
stores = load_stores()
txn    = load_transactions()
waste  = load_waste()
staff  = load_staff_monthly()
terms  = load_delivery_terms()
cands  = load_candidate_sites()
catch  = load_catchment()
reviews = load_reviews()

# ── Chain totals ──────────────────────────────────────────────────────────────
total_sales  = pnl["total_net_sales_gbp"].sum()
total_profit = pnl["net_profit_gbp"].sum()
total_margin = total_profit / total_sales * 100
total_labour = pnl["labour_cost_gbp"].sum()
total_waste  = pnl["waste_cost_gbp"].sum()
total_del_cost = pnl["total_delivery_cost_gbp"].sum()

print("=== CHAIN TOTALS ===")
print(f"Total net sales:   £{total_sales:,.0f}")
print(f"Total net profit:  £{total_profit:,.0f}")
print(f"Net margin:        {total_margin:.1f}%")
print(f"Total labour cost: £{total_labour:,.0f} ({total_labour/total_sales*100:.1f}% of sales)")
print(f"Total waste cost:  £{total_waste:,.0f} ({total_waste/total_sales*100:.1f}% of sales)")
print(f"Total delivery cost: £{total_del_cost:,.0f}")

# ── Per-store margins ─────────────────────────────────────────────────────────
print("\n=== STORE MARGINS (avg monthly) ===")
store_summary = pnl.groupby("store_id").agg(
    sales=("total_net_sales_gbp","sum"),
    profit=("net_profit_gbp","sum"),
    labour=("labour_cost_gbp","sum"),
    rent=("rent_gbp","sum"),
    waste=("waste_cost_gbp","sum"),
    del_cost=("total_delivery_cost_gbp","sum"),
    margin=("net_margin_pct","mean"),
).reset_index()
store_summary = store_summary.merge(stores[["store_id","store_name","location_type"]], on="store_id")
store_summary["rent_pct"] = store_summary["rent"] / store_summary["sales"] * 100
store_summary["labour_pct"] = store_summary["labour"] / store_summary["sales"] * 100
print(store_summary[["store_name","sales","profit","margin","rent_pct","labour_pct"]].sort_values("margin").to_string(index=False))

# ── Piccadilly deep dive ──────────────────────────────────────────────────────
pic = store_summary[store_summary["store_id"]=="S07"].iloc[0]
print(f"\n=== PICCADILLY ===")
print(f"Annual sales: £{pic['sales']:,.0f}")
print(f"Annual profit: £{pic['profit']:,.0f}")
print(f"Avg margin: {pic['margin']:.1f}%")
print(f"Rent % of sales: {pic['rent_pct']:.1f}%")
print(f"Labour % of sales: {pic['labour_pct']:.1f}%")

# ── Leeds Briggate vs Trinity ─────────────────────────────────────────────────
print("\n=== LEEDS: BRIGGATE vs TRINITY ===")
leeds_monthly = pnl[pnl["store_id"].isin(["S03","S12"])].copy()
leeds_monthly = leeds_monthly.merge(stores[["store_id","store_name"]], on="store_id")
print(leeds_monthly.groupby(["store_id","store_name"])[["total_net_sales_gbp","net_profit_gbp","net_margin_pct"]].mean().round(0))

# Monthly sales trend for Briggate
brig = pnl[pnl["store_id"]=="S03"].sort_values("month")
print("\nBriggate monthly sales:")
print(brig[["month","total_net_sales_gbp","net_profit_gbp","net_margin_pct"]].to_string(index=False))

# ── Delivery ──────────────────────────────────────────────────────────────────
print("\n=== DELIVERY ===")
monthly_del = daily.groupby("month").agg(
    total=("total_net_sales_gbp","sum"),
    del_rev=("net_sales_delivery_gbp","sum"),
    del_receipts=("receipts_delivery","sum"),
).reset_index()
monthly_del["del_share"] = monthly_del["del_rev"] / monthly_del["total"] * 100
print(monthly_del[["month","del_share","del_receipts"]].to_string(index=False))

# Delivery order values from sample
del_txn = txn[txn["channel"]=="Delivery"].copy()
print(f"\nDelivery orders in sample: {len(del_txn)}")
print(f"Avg order value: £{del_txn['net_gbp'].mean():.2f}")
print(f"Median order value: £{del_txn['net_gbp'].median():.2f}")
print("\nBy partner:")
print(del_txn.groupby("delivery_partner")["net_gbp"].describe()[["count","mean","50%","min"]].round(2))

# Break-even at 33% (Dashly post-April)
commission = 0.33
packaging = 0.45
wage = 12.50
staff_cost = (4/60) * wage * 1.13
fixed = packaging + staff_cost
breakeven_dashly = fixed / (1 - commission)

commission_rusheats = 0.30
breakeven_rusheats = fixed / (1 - commission_rusheats)

dashly_orders = del_txn[del_txn["delivery_partner"]=="Dashly"]["net_gbp"]
rusheats_orders = del_txn[del_txn["delivery_partner"]=="RushEats"]["net_gbp"]

print(f"\nBreak-even basket (Dashly 33%): £{breakeven_dashly:.2f}")
print(f"Break-even basket (RushEats 30%): £{breakeven_rusheats:.2f}")
print(f"Dashly orders below break-even: {(dashly_orders < breakeven_dashly).mean()*100:.1f}%")
print(f"RushEats orders below break-even: {(rusheats_orders < breakeven_rusheats).mean()*100:.1f}%")
print(f"All delivery orders below £8: {(del_txn['net_gbp'] < 8).mean()*100:.1f}%")

# Annual delivery revenue (full dataset)
annual_del_rev = daily["net_sales_delivery_gbp"].sum()
annual_del_receipts = daily["receipts_delivery"].sum()
avg_order_value_full = annual_del_rev / annual_del_receipts
print(f"\nAnnual delivery revenue (full): £{annual_del_rev:,.0f}")
print(f"Annual delivery orders (full): {annual_del_receipts:,.0f}")
print(f"Avg delivery order value (full): £{avg_order_value_full:.2f}")

# ── Waste ──────────────────────────────────────────────────────────────────────
print("\n=== WASTE ===")
waste_by_store = waste.groupby("store_id").agg(
    total_wasted_cost=("est_cost_wasted_gbp","sum"),
    units_wasted=("units_wasted","sum"),
    units_prepared=("units_prepared","sum"),
).reset_index()
waste_by_store["waste_rate"] = waste_by_store["units_wasted"] / waste_by_store["units_prepared"] * 100
waste_by_store = waste_by_store.merge(stores[["store_id","store_name"]], on="store_id")
print(waste_by_store[["store_name","total_wasted_cost","waste_rate"]].sort_values("waste_rate",ascending=False).to_string(index=False))

# ── Staff turnover ─────────────────────────────────────────────────────────────
print("\n=== STAFF TURNOVER ===")
staff_sum = staff.groupby("store_id").agg(
    total_leavers=("leavers","sum"),
    avg_headcount=("headcount","mean"),
    avg_score=("staff_survey_score_10","mean"),
).reset_index()
staff_sum["annualised_turnover_pct"] = staff_sum["total_leavers"] / staff_sum["avg_headcount"] * 100
staff_sum = staff_sum.merge(stores[["store_id","store_name"]], on="store_id")
print(staff_sum[["store_name","total_leavers","avg_headcount","annualised_turnover_pct","avg_score"]].sort_values("annualised_turnover_pct",ascending=False).to_string(index=False))

# ── Reviews ───────────────────────────────────────────────────────────────────
print("\n=== REVIEWS ===")
print(f"Total reviews: {len(reviews)}")
print(f"Avg rating: {reviews['rating'].mean():.2f}")
print(f"1-2 star: {(reviews['rating']<=2).mean()*100:.1f}%")

# App v3.0 impact: before March 2026 vs after
reviews["review_date"] = pd.to_datetime(reviews["review_date"])
pre_app  = reviews[reviews["review_date"] < "2026-03-02"]["rating"].mean()
post_app = reviews[(reviews["review_date"] >= "2026-03-02") & (reviews["review_date"] < "2026-04-13")]["rating"].mean()
post_fix = reviews[reviews["review_date"] >= "2026-04-13"]["rating"].mean()
print(f"\nAvg rating BEFORE App v3.0 (pre Mar 2):  {pre_app:.2f}")
print(f"Avg rating AFTER App v3.0 (Mar 2 – Apr 13): {post_app:.2f}")
print(f"Avg rating AFTER App v3.1 hotfix (post Apr 13): {post_fix:.2f}")

# Oat milk: Jan 12 2026
pre_oat  = reviews[reviews["review_date"] < "2026-01-12"]["rating"].mean()
post_oat = reviews[reviews["review_date"] >= "2026-01-12"]["rating"].mean()
print(f"\nAvg rating BEFORE oat milk charge: {pre_oat:.2f}")
print(f"Avg rating AFTER oat milk charge: {post_oat:.2f}")

# ── Candidate sites ────────────────────────────────────────────────────────────
print("\n=== CANDIDATE SITES ===")
print(cands[["site_name","city","location_type","quoted_rent_gbp_month","office_workers_500m","daily_footfall_street","est_fitout_gbp"]].to_string(index=False))

