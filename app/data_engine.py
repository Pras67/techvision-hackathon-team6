"""
Data loading and P&L computation for Grind & Crumb.
All monetary values in GBP, net of VAT.
Key assumption: transactions.csv is a 10% sample — use daily_store_sales.csv for totals.
Labour cost = scheduled_hours × avg_hourly_wage_gbp × 1.13
"""

import pandas as pd
import numpy as np
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data files"


# ---------------------------------------------------------------------------
# Loaders (cached at call site with st.cache_data)
# ---------------------------------------------------------------------------

def load_stores():
    df = pd.read_csv(DATA_DIR / "stores.csv")
    return df


def load_daily_sales():
    df = pd.read_csv(DATA_DIR / "daily_store_sales.csv", parse_dates=["date"])
    df["total_receipts"] = df["receipts_instore"] + df["receipts_app"] + df["receipts_delivery"]
    df["total_net_sales_gbp"] = (
        df["net_sales_instore_gbp"] + df["net_sales_app_gbp"] + df["net_sales_delivery_gbp"]
    )
    df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()
    return df


def load_footfall():
    df = pd.read_csv(DATA_DIR / "footfall.csv", parse_dates=["date"])
    df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()
    return df


def load_store_costs():
    df = pd.read_csv(DATA_DIR / "store_costs_monthly.csv")
    df["month"] = pd.to_datetime(df["month"], format="%Y-%m")
    df["fixed_opex_gbp"] = (
        df["rent_gbp"] + df["business_rates_gbp"] + df["utilities_gbp"]
        + df["repairs_maintenance_gbp"] + df["other_opex_gbp"]
    )
    return df


def load_rota():
    df = pd.read_csv(DATA_DIR / "staff_rota_weekly.csv", parse_dates=["week_start"])
    df["labour_cost_gbp"] = df["scheduled_hours"] * df["avg_hourly_wage_gbp"] * 1.13
    df["month"] = df["week_start"].dt.to_period("M").dt.to_timestamp()
    return df


def load_waste():
    df = pd.read_csv(DATA_DIR / "waste_log.csv")
    # DATA ISSUE: October 2025 rows use DD/MM/YYYY; all others use YYYY-MM-DD.
    # Fix: parse mixed format with dayfirst=False, then re-parse ambiguous rows.
    df["date"] = pd.to_datetime(df["date"], dayfirst=False, format="mixed")
    # Rows where day<=12 could be mis-parsed — but since the non-ISO rows are
    # all in October (month=10) and the DD portion ranges 01-31, dayfirst=True
    # would be needed only for those rows. We detect and correct.
    mask = df["date"].dt.strftime("%Y-%m-%d") != df["date"].dt.strftime("%Y-%m-%d")  # placeholder
    # Simpler: re-parse the non-ISO subset with dayfirst=True
    non_iso = ~df["date"].apply(lambda d: True)  # reset
    raw = pd.read_csv(DATA_DIR / "waste_log.csv")["date"]
    non_iso_mask = ~raw.str.match(r'^\d{4}-\d{2}-\d{2}$', na=False)
    df.loc[non_iso_mask, "date"] = pd.to_datetime(
        raw[non_iso_mask], dayfirst=True, format="mixed"
    )
    df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()
    return df


def load_delivery_terms():
    df = pd.read_csv(DATA_DIR / "delivery_partner_terms.csv")
    df["valid_from"] = pd.to_datetime(df["valid_from"])
    df["valid_to"] = pd.to_datetime(df["valid_to"], errors="coerce")
    return df


def load_footfall():
    df = pd.read_csv(DATA_DIR / "footfall.csv")
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()
    return df


def load_transactions():
    df = pd.read_csv(DATA_DIR / "transactions.csv", parse_dates=["timestamp"])
    df["date"] = df["timestamp"].dt.date
    df["month"] = df["timestamp"].dt.to_period("M").dt.to_timestamp()
    return df


def load_transaction_lines():
    return pd.read_csv(DATA_DIR / "transaction_lines.csv")


def load_products():
    return pd.read_csv(DATA_DIR / "products.csv")


def load_loyalty():
    df = pd.read_csv(DATA_DIR / "loyalty_customers.csv", parse_dates=["signup_date"])
    return df


def load_staff_monthly():
    df = pd.read_csv(DATA_DIR / "staff_monthly.csv")
    df["month"] = pd.to_datetime(df["month"], format="%Y-%m")
    return df


def load_reviews():
    return pd.read_csv(DATA_DIR / "customer_reviews.csv", parse_dates=["review_date"])


def load_catchment():
    return pd.read_csv(DATA_DIR / "store_catchment.csv")


def load_candidate_sites():
    return pd.read_csv(DATA_DIR / "candidate_sites.csv")


def load_weather():
    return pd.read_csv(DATA_DIR / "weather.csv", parse_dates=["date"])


def load_promotions():
    df = pd.read_csv(DATA_DIR / "promotions.csv")
    df["start_date"] = pd.to_datetime(df["start_date"])
    df["end_date"] = pd.to_datetime(df["end_date"])
    return df


def load_business_events():
    df = pd.read_csv(DATA_DIR / "business_events.csv")
    df["date"] = pd.to_datetime(df["date"])
    return df


# ---------------------------------------------------------------------------
# Delivery cost engine
# ---------------------------------------------------------------------------

def get_commission_rate(partner: str, month: pd.Timestamp, terms: pd.DataFrame) -> float:
    """Return the commission rate for a partner at a given month."""
    rows = terms[terms["partner"] == partner].copy()
    for _, row in rows.iterrows():
        valid_from = row["valid_from"]
        valid_to = row["valid_to"]
        if pd.isna(valid_to):
            valid_to = pd.Timestamp("2099-01-01")
        if valid_from <= month < valid_to + pd.offsets.MonthEnd(0) + pd.Timedelta(days=1):
            return row["commission_rate"]
    return np.nan


def compute_delivery_costs_monthly(daily_sales: pd.DataFrame, terms: pd.DataFrame) -> pd.DataFrame:
    """
    Compute estimated monthly delivery costs per store.

    Delivery gross revenue is approximated as net_sales_delivery_gbp (data is net of VAT;
    commissions are charged on gross order value — we treat net≈gross here as the brief
    says all money is net of VAT).

    Staff time cost: 4 min per delivery order at the store's average hourly wage.
    We use a chain-wide average wage proxy (£12.50/hr) since rota is by store/daypart.
    """
    AVG_HOURLY_WAGE = 12.50  # reasonable proxy; NLW-era
    STAFF_TIME_PER_ORDER_HR = 4 / 60
    PACKAGING_GBP = 0.45  # from delivery_partner_terms.csv

    monthly = (
        daily_sales.groupby(["month", "store_id"])
        .agg(
            receipts_delivery=("receipts_delivery", "sum"),
            net_sales_delivery_gbp=("net_sales_delivery_gbp", "sum"),
        )
        .reset_index()
    )

    # Split by partner — transactions give us the split (10% sample, ratio holds)
    txn = load_transactions()
    txn_delivery = txn[txn["channel"] == "Delivery"].copy()
    txn_delivery["month"] = txn_delivery["month"]  # already computed

    partner_split = (
        txn_delivery.groupby(["month", "store_id", "delivery_partner"])["net_gbp"]
        .sum()
        .reset_index()
    )
    partner_total = (
        txn_delivery.groupby(["month", "store_id"])["net_gbp"]
        .sum()
        .reset_index()
        .rename(columns={"net_gbp": "total_delivery"})
    )
    partner_split = partner_split.merge(partner_total, on=["month", "store_id"])
    partner_split["share"] = partner_split["net_gbp"] / partner_split["total_delivery"]

    # Merge partner shares onto monthly delivery totals
    merged = monthly.merge(partner_split, on=["month", "store_id"], how="left")

    # For rows where partner split is available, compute commission
    commission_rows = []
    for _, row in merged.iterrows():
        partner = row.get("delivery_partner")
        m = row["month"]
        receipts = row["receipts_delivery"]
        net_sales = row["net_sales_delivery_gbp"]
        share = row.get("share", 1.0) if not pd.isna(row.get("share", np.nan)) else 1.0

        if pd.isna(partner):
            commission_rate = 0.305  # blended average across the year
        else:
            commission_rate = get_commission_rate(partner, m, terms)
            if pd.isna(commission_rate):
                commission_rate = 0.305

        allocated_net = net_sales * share
        commission_cost = allocated_net * commission_rate
        packaging_cost = receipts * share * PACKAGING_GBP
        staff_cost = receipts * share * STAFF_TIME_PER_ORDER_HR * AVG_HOURLY_WAGE * 1.13

        commission_rows.append({
            "month": m,
            "store_id": row["store_id"],
            "delivery_partner": partner,
            "allocated_delivery_revenue": allocated_net,
            "commission_cost_gbp": commission_cost,
            "packaging_cost_gbp": packaging_cost,
            "staff_time_cost_gbp": staff_cost,
            "total_delivery_cost_gbp": commission_cost + packaging_cost + staff_cost,
        })

    cost_df = pd.DataFrame(commission_rows)
    # Aggregate back to store/month total
    agg = (
        cost_df.groupby(["month", "store_id"])
        .agg(
            allocated_delivery_revenue=("allocated_delivery_revenue", "sum"),
            commission_cost_gbp=("commission_cost_gbp", "sum"),
            packaging_cost_gbp=("packaging_cost_gbp", "sum"),
            staff_time_cost_gbp=("staff_time_cost_gbp", "sum"),
            total_delivery_cost_gbp=("total_delivery_cost_gbp", "sum"),
        )
        .reset_index()
    )
    return agg


# ---------------------------------------------------------------------------
# Monthly P&L per store
# ---------------------------------------------------------------------------

def build_store_pnl() -> pd.DataFrame:
    """
    Returns a DataFrame with one row per (store_id, month) containing:
    - total_net_sales_gbp
    - labour_cost_gbp
    - fixed_opex_gbp (rent + rates + utilities + repairs + other)
    - waste_cost_gbp
    - total_delivery_cost_gbp
    - gross_profit_gbp  (sales - food_cost proxy is NOT available directly;
                         we use it as sales − all operational costs)
    - net_profit_gbp
    - net_margin_pct
    """
    daily_sales = load_daily_sales()
    store_costs = load_store_costs()
    rota = load_rota()
    waste = load_waste()
    terms = load_delivery_terms()

    # Monthly sales
    monthly_sales = (
        daily_sales.groupby(["month", "store_id"])
        .agg(
            total_net_sales_gbp=("total_net_sales_gbp", "sum"),
            receipts_instore=("receipts_instore", "sum"),
            receipts_app=("receipts_app", "sum"),
            receipts_delivery=("receipts_delivery", "sum"),
            net_sales_instore_gbp=("net_sales_instore_gbp", "sum"),
            net_sales_app_gbp=("net_sales_app_gbp", "sum"),
            net_sales_delivery_gbp=("net_sales_delivery_gbp", "sum"),
        )
        .reset_index()
    )

    # Monthly labour
    monthly_labour = (
        rota.groupby(["month", "store_id"])["labour_cost_gbp"].sum().reset_index()
    )

    # Monthly waste
    monthly_waste = (
        waste.groupby(["month", "store_id"])["est_cost_wasted_gbp"].sum()
        .reset_index()
        .rename(columns={"est_cost_wasted_gbp": "waste_cost_gbp"})
    )

    # Monthly delivery costs
    delivery_costs = compute_delivery_costs_monthly(daily_sales, terms)

    # Merge everything
    pnl = monthly_sales.merge(store_costs[["month", "store_id", "fixed_opex_gbp",
                                            "rent_gbp", "business_rates_gbp",
                                            "utilities_gbp", "repairs_maintenance_gbp",
                                            "other_opex_gbp"]],
                               on=["month", "store_id"], how="left")
    pnl = pnl.merge(monthly_labour, on=["month", "store_id"], how="left")
    pnl = pnl.merge(monthly_waste, on=["month", "store_id"], how="left")
    pnl = pnl.merge(
        delivery_costs[["month", "store_id", "total_delivery_cost_gbp",
                         "commission_cost_gbp", "packaging_cost_gbp", "staff_time_cost_gbp"]],
        on=["month", "store_id"], how="left"
    )

    pnl = pnl.fillna(0)

    pnl["total_costs_gbp"] = (
        pnl["labour_cost_gbp"]
        + pnl["fixed_opex_gbp"]
        + pnl["waste_cost_gbp"]
        + pnl["total_delivery_cost_gbp"]
    )

    pnl["net_profit_gbp"] = pnl["total_net_sales_gbp"] - pnl["total_costs_gbp"]
    pnl["net_margin_pct"] = (pnl["net_profit_gbp"] / pnl["total_net_sales_gbp"].replace(0, np.nan)) * 100

    return pnl

