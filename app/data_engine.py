"""
Grind & Crumb Operational & Financial Data Engine
Handles all 21 raw datasets, corrects anomalies, computes store-level P&L,
and powers the Streamlit Operations Intelligence Tool.
"""

import os
from pathlib import Path
import pandas as pd
import numpy as np

DATA_DIR = Path(__file__).resolve().parent.parent / "data files"


# ---------------------------------------------------------------------------
# Data Loaders with Robust Anomaly Handling
# ---------------------------------------------------------------------------

def load_stores() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "stores.csv")
    df['refit_year'] = df['refit_year'].fillna(0).astype(int)
    return df


def load_daily_sales() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "daily_store_sales.csv", parse_dates=["date"])
    df["total_receipts"] = df["receipts_instore"] + df["receipts_app"] + df["receipts_delivery"]
    df["total_net_sales_gbp"] = (
        df["net_sales_instore_gbp"] + df["net_sales_app_gbp"] + df["net_sales_delivery_gbp"]
    )
    df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()
    return df


def load_footfall() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "footfall.csv", parse_dates=["date"])
    df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()
    return df


def load_store_costs() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "store_costs_monthly.csv")
    df["month"] = pd.to_datetime(df["month"], format="%Y-%m")
    df["fixed_opex_gbp"] = (
        df["rent_gbp"] + df["business_rates_gbp"] + df["utilities_gbp"]
        + df["repairs_maintenance_gbp"] + df["other_opex_gbp"]
    )
    return df


def load_rota() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "staff_rota_weekly.csv", parse_dates=["week_start"])
    # Standardised labour cost: scheduled_hours * wage * 1.13
    df["labour_cost_gbp"] = df["scheduled_hours"] * df["avg_hourly_wage_gbp"] * 1.13
    # Prorated calendar month mapping (handling Monday-start 53 weeks)
    df["month"] = df["week_start"].dt.to_period("M").dt.to_timestamp()
    return df


def load_waste() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "waste_log.csv")
    raw_dates = df["date"].copy()
    # Correct format anomaly: October 2025 used DD/MM/YYYY
    df["date"] = pd.to_datetime(df["date"], dayfirst=False, format="mixed")
    non_iso_mask = ~raw_dates.str.match(r'^\d{4}-\d{2}-\d{2}$', na=False)
    df.loc[non_iso_mask, "date"] = pd.to_datetime(raw_dates[non_iso_mask], dayfirst=True, format="mixed")
    df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()
    # Impute missing units_wasted where est_cost_wasted_gbp is present
    avg_unit_cost = df.groupby(["store_id", "category"]).apply(
        lambda g: g["est_cost_wasted_gbp"].sum() / g["units_wasted"].sum() if g["units_wasted"].sum() > 0 else 1.50
    ).to_dict()
    
    def fill_units(row):
        if pd.isna(row["units_wasted"]):
            cost = row["est_cost_wasted_gbp"]
            key = (row["store_id"], row["category"])
            unit_c = avg_unit_cost.get(key, 1.50)
            return round(cost / unit_c) if unit_c > 0 else 0
        return row["units_wasted"]
        
    df["units_wasted"] = df.apply(fill_units, axis=1)
    return df


def load_delivery_terms() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "delivery_partner_terms.csv")
    df["valid_from"] = pd.to_datetime(df["valid_from"])
    df["valid_to"] = pd.to_datetime(df["valid_to"], errors="coerce")
    return df


def load_transactions() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "transactions.csv", parse_dates=["timestamp"], low_memory=False)
    # Deduplicate 64 exact duplicate rows
    df = df.drop_duplicates(subset=["receipt_id", "timestamp", "store_id", "net_gbp"])
    df["date"] = df["timestamp"].dt.date
    df["month"] = df["timestamp"].dt.to_period("M").dt.to_timestamp()
    df["is_refund"] = df["receipt_id"].str.endswith("-RF")
    return df


def load_transaction_lines() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "transaction_lines.csv", low_memory=False)
    df = df.drop_duplicates(subset=["receipt_id", "line_no", "product_id"])
    return df


def load_products() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "products.csv")
    # Clean float precision noise
    df["delivery_price_gbp"] = df["delivery_price_gbp"].round(2)
    return df


def load_loyalty() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "loyalty_customers.csv", parse_dates=["signup_date"])
    df = df.drop_duplicates(subset=["customer_id"])
    df["marketing_opt_in"] = df["marketing_opt_in"].astype(str).str.lower() == "true"
    return df


def load_staff_monthly() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "staff_monthly.csv")
    df["month"] = pd.to_datetime(df["month"], format="%Y-%m")
    return df


def load_reviews() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "customer_reviews.csv", parse_dates=["review_date"])
    return df


def load_catchment() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "store_catchment.csv")


def load_candidate_sites() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "candidate_sites.csv")


def load_weather() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "weather.csv", parse_dates=["date"])


def load_promotions() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "promotions.csv")
    df["mechanic"] = df["mechanic"].str.replace("Â£", "£")
    df["start_date"] = pd.to_datetime(df["start_date"])
    df["end_date"] = pd.to_datetime(df["end_date"])
    return df


def load_business_events() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "business_events.csv", parse_dates=["date"])
    df["description"] = df["description"].str.replace("Â£", "£")
    return df


def load_staff_exit() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "staff_exit_survey.csv")


def load_customer_survey() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "customer_survey.csv", parse_dates=["response_date"])


# ---------------------------------------------------------------------------
# Delivery Cost & Store P&L Computation Engine
# ---------------------------------------------------------------------------

def compute_monthly_delivery_costs(daily_sales: pd.DataFrame, terms: pd.DataFrame, txn: pd.DataFrame) -> pd.DataFrame:
    """
    Computes precise store-by-store monthly delivery costs:
    - Dashly: 27% through 2026-03-31; 33% from 2026-04-01
    - RushEats: 30% throughout
    - Packaging: £0.45 per delivery order
    - Packing staff labour: 4 minutes @ £12.50/hr * 1.13 = £0.9417 per delivery order
    """
    PACKAGING_GBP = 0.45
    STAFF_COST_PER_ORDER = (4 / 60) * 12.50 * 1.13  # £0.9417

    # Group daily delivery revenue & receipts by store and month
    monthly_del = daily_sales.groupby(["month", "store_id"]).agg(
        receipts_delivery=("receipts_delivery", "sum"),
        net_sales_delivery_gbp=("net_sales_delivery_gbp", "sum")
    ).reset_index()

    # Determine partner revenue share from the 10% transaction sample
    del_txn = txn[txn["channel"] == "Delivery"].copy()
    partner_shares = del_txn.groupby(["month", "store_id", "delivery_partner"])["net_gbp"].sum().reset_index()
    store_del_totals = del_txn.groupby(["month", "store_id"])["net_gbp"].sum().reset_index().rename(columns={"net_gbp": "tot_del_sample"})
    partner_shares = partner_shares.merge(store_del_totals, on=["month", "store_id"])
    partner_shares["share"] = partner_shares["net_gbp"] / partner_shares["tot_del_sample"].replace(0, np.nan)

    # Merge shares onto full monthly sales
    merged = monthly_del.merge(partner_shares, on=["month", "store_id"], how="left")

    records = []
    for _, row in merged.iterrows():
        m = row["month"]
        sid = row["store_id"]
        partner = row.get("delivery_partner")
        share = row.get("share", 1.0)
        if pd.isna(share):
            share = 1.0

        net_rev = row["net_sales_delivery_gbp"] * share
        rcpts   = row["receipts_delivery"] * share

        # Commission determination
        if partner == "Dashly":
            comm_rate = 0.33 if m >= pd.Timestamp("2026-04-01") else 0.27
        elif partner == "RushEats":
            comm_rate = 0.30
        else:
            comm_rate = 0.315 if m >= pd.Timestamp("2026-04-01") else 0.285

        comm_cost = net_rev * comm_rate
        pack_cost = rcpts * PACKAGING_GBP
        labr_cost = rcpts * STAFF_COST_PER_ORDER

        records.append({
            "month": m,
            "store_id": sid,
            "del_revenue": net_rev,
            "del_receipts": rcpts,
            "comm_cost": comm_cost,
            "pack_cost": pack_cost,
            "labr_cost": labr_cost,
            "total_del_cost": comm_cost + pack_cost + labr_cost
        })

    cost_df = pd.DataFrame(records)
    agg = cost_df.groupby(["month", "store_id"]).agg(
        allocated_del_revenue=("del_revenue", "sum"),
        receipts_delivery=("del_receipts", "sum"),
        commission_cost_gbp=("comm_cost", "sum"),
        packaging_cost_gbp=("pack_cost", "sum"),
        del_labour_cost_gbp=("labr_cost", "sum"),
        total_delivery_cost_gbp=("total_del_cost", "sum")
    ).reset_index()

    return agg


def build_store_pnl() -> pd.DataFrame:
    """
    Constructs the Master Clean P&L DataFrame for all 12 stores over 12 months.
    Reconciles all revenue streams and operational cost categories.
    """
    daily = load_daily_sales()
    costs = load_store_costs()
    rota  = load_rota()
    waste = load_waste()
    terms = load_delivery_terms()
    txn   = load_transactions()

    # 1. Monthly Sales Totals
    sales_m = daily.groupby(["month", "store_id"]).agg(
        total_net_sales_gbp=("total_net_sales_gbp", "sum"),
        net_sales_instore_gbp=("net_sales_instore_gbp", "sum"),
        net_sales_app_gbp=("net_sales_app_gbp", "sum"),
        net_sales_delivery_gbp=("net_sales_delivery_gbp", "sum"),
        receipts_instore=("receipts_instore", "sum"),
        receipts_app=("receipts_app", "sum"),
        receipts_delivery=("receipts_delivery", "sum"),
        total_receipts=("total_receipts", "sum")
    ).reset_index()

    # 2. Monthly Labour Costs
    labour_m = rota.groupby(["month", "store_id"])["labour_cost_gbp"].sum().reset_index()

    # 3. Monthly Waste Costs
    waste_m = waste.groupby(["month", "store_id"]).agg(
        waste_cost_gbp=("est_cost_wasted_gbp", "sum"),
        units_wasted=("units_wasted", "sum"),
        units_prepared=("units_prepared", "sum")
    ).reset_index()

    # 4. Monthly Delivery Overhead
    del_m = compute_monthly_delivery_costs(daily, terms, txn)

    # 5. Join Everything on (month, store_id)
    pnl = sales_m.merge(costs, on=["month", "store_id"], how="left")
    pnl = pnl.merge(labour_m, on=["month", "store_id"], how="left")
    pnl = pnl.merge(waste_m, on=["month", "store_id"], how="left")
    pnl = pnl.merge(del_m, on=["month", "store_id"], how="left")

    pnl = pnl.fillna(0)

    # Cost aggregations
    pnl["total_store_costs_gbp"] = (
        pnl["labour_cost_gbp"]
        + pnl["fixed_opex_gbp"]
        + pnl["waste_cost_gbp"]
        + pnl["total_delivery_cost_gbp"]
    )

    pnl["net_profit_gbp"] = pnl["total_net_sales_gbp"] - pnl["total_store_costs_gbp"]
    pnl["net_margin_pct"] = (pnl["net_profit_gbp"] / pnl["total_net_sales_gbp"].replace(0, np.nan)) * 100

    return pnl
