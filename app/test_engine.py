"""Quick smoke-test for data_engine.py — run before the main app."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from data_engine import (
    load_stores, load_daily_sales, load_store_costs,
    load_rota, load_waste, load_delivery_terms,
    load_transactions, load_products, load_catchment,
    load_candidate_sites, load_reviews, load_staff_monthly,
    build_store_pnl
)

print("Loading stores...", load_stores().shape)
print("Loading daily_sales...", load_daily_sales().shape)
print("Loading store_costs...", load_store_costs().shape)
print("Loading rota...", load_rota().shape)
print("Loading waste...", load_waste().shape)
print("Loading delivery_terms...", load_delivery_terms().shape)
print("Loading transactions...", load_transactions().shape)
print("Loading products...", load_products().shape)
print("Loading catchment...", load_catchment().shape)
print("Loading candidate_sites...", load_candidate_sites().shape)
print("Loading reviews...", load_reviews().shape)
print("Loading staff_monthly...", load_staff_monthly().shape)
print("\nBuilding store P&L (this takes a moment)...")
pnl = build_store_pnl()
print("P&L shape:", pnl.shape)
print(pnl[["store_id","month","total_net_sales_gbp","total_costs_gbp","net_profit_gbp","net_margin_pct"]].groupby("store_id").mean(numeric_only=True).round(0))
print("\nDone.")

