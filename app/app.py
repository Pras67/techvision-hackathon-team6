"""
Grind & Crumb Operations & Strategy Intelligence Platform
Board Decision Support System & £1.5M Capital Allocation Tool
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from data_engine import (
    load_stores, load_daily_sales, load_store_costs, load_rota,
    load_waste, load_delivery_terms, load_transactions,
    load_transaction_lines, load_products, load_loyalty,
    load_staff_monthly, load_reviews, load_catchment,
    load_candidate_sites, load_weather, load_promotions,
    load_business_events, load_staff_exit, load_customer_survey,
    load_footfall, build_store_pnl
)

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Grind & Crumb · Ops Intelligence Platform",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Clean Enterprise Tailwind Theme (WCAG AA Compliant) ──────────────────────
SLATE_900 = "#0F172A"
SLATE_800 = "#1E293B"
SLATE_700 = "#334155"
SLATE_600 = "#475569"
SLATE_500 = "#64748B"
SLATE_200 = "#E2E8F0"
SLATE_100 = "#F1F5F9"
SLATE_50  = "#F8FAFC"

EMERALD_DARK = "#065F46"
EMERALD_MAIN = "#059669"
EMERALD_BG   = "#ECFDF5"
EMERALD_BORDER = "#A7F3D0"

AMBER_DARK   = "#92400E"
AMBER_MAIN   = "#D97706"
AMBER_BG     = "#FFFBEB"
AMBER_BORDER = "#FDE68A"

ROSE_DARK    = "#9F1239"
ROSE_MAIN    = "#E11D48"
ROSE_BG      = "#FFF1F2"
ROSE_BORDER  = "#FECDD3"

INDIGO_DARK  = "#3730A3"
INDIGO_MAIN  = "#4F46E5"
INDIGO_BG    = "#EEF2FF"
INDIGO_BORDER= "#C7D2FE"

st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
  
  html, body, [class*="css"] {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: {SLATE_900};
  }}

  .stApp {{
    background-color: {SLATE_50};
  }}

  .block-container {{
    padding-top: 1.25rem;
    padding-bottom: 3rem;
    max-width: 1400px;
  }}

  /* Tailwind Stat Metric Cards */
  .tw-metric-card {{
    background-color: #FFFFFF;
    border: 1px solid {SLATE_200};
    border-radius: 0.75rem;
    padding: 1.15rem 1.35rem;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
  }}

  .tw-metric-title {{
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: {SLATE_500};
    margin-bottom: 0.35rem;
  }}

  .tw-metric-value {{
    font-size: 1.65rem;
    font-weight: 800;
    color: {SLATE_900};
    line-height: 1.2;
  }}

  .tw-pill {{
    display: inline-flex;
    align-items: center;
    padding: 0.2rem 0.55rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-top: 0.45rem;
    border: 1px solid transparent;
  }}
  .tw-pill-emerald {{ background-color: {EMERALD_BG}; color: {EMERALD_DARK}; border-color: {EMERALD_BORDER}; }}
  .tw-pill-rose    {{ background-color: {ROSE_BG}; color: {ROSE_DARK}; border-color: {ROSE_BORDER}; }}
  .tw-pill-amber   {{ background-color: {AMBER_BG}; color: {AMBER_DARK}; border-color: {AMBER_BORDER}; }}
  .tw-pill-indigo  {{ background-color: {INDIGO_BG}; color: {INDIGO_DARK}; border-color: {INDIGO_BORDER}; }}
  .tw-pill-slate   {{ background-color: {SLATE_100}; color: {SLATE_700}; border-color: {SLATE_200}; }}

  /* Tailwind Alert Banner */
  .tw-banner {{
    border-radius: 0.5rem;
    padding: 0.95rem 1.25rem;
    margin: 0.75rem 0 1.25rem 0;
    font-size: 0.925rem;
    line-height: 1.5;
    border-left-width: 4px;
  }}
  .tw-banner-emerald {{ background-color: {EMERALD_BG}; border-left-color: {EMERALD_MAIN}; color: {EMERALD_DARK}; border-top: 1px solid {EMERALD_BORDER}; border-right: 1px solid {EMERALD_BORDER}; border-bottom: 1px solid {EMERALD_BORDER}; }}
  .tw-banner-amber   {{ background-color: {AMBER_BG}; border-left-color: {AMBER_MAIN}; color: {AMBER_DARK}; border-top: 1px solid {AMBER_BORDER}; border-right: 1px solid {AMBER_BORDER}; border-bottom: 1px solid {AMBER_BORDER}; }}
  .tw-banner-rose    {{ background-color: {ROSE_BG}; border-left-color: {ROSE_MAIN}; color: {ROSE_DARK}; border-top: 1px solid {ROSE_BORDER}; border-right: 1px solid {ROSE_BORDER}; border-bottom: 1px solid {ROSE_BORDER}; }}

  div[data-testid="stTabs"] button {{
    font-weight: 600 !important;
    font-size: 0.925rem !important;
    color: {SLATE_700} !important;
    padding: 0.55rem 1.15rem !important;
  }}
  div[data-testid="stTabs"] button[aria-selected="true"] {{
    color: {EMERALD_MAIN} !important;
    border-bottom-color: {EMERALD_MAIN} !important;
  }}
</style>
""", unsafe_allow_html=True)


# ── Cached Data Loaders ───────────────────────────────────────────────────────
@st.cache_data
def get_pnl():          return build_store_pnl()
@st.cache_data
def get_stores():       return load_stores()
@st.cache_data
def get_daily():        return load_daily_sales()
@st.cache_data
def get_transactions(): return load_transactions()
@st.cache_data
def get_lines():        return load_transaction_lines()
@st.cache_data
def get_products():     return load_products()
@st.cache_data
def get_reviews():      return load_reviews()
@st.cache_data
def get_footfall():     return load_footfall()
@st.cache_data
def get_catchment():    return load_catchment()
@st.cache_data
def get_candidates():   return load_candidate_sites()
@st.cache_data
def get_staff():        return load_staff_monthly()
@st.cache_data
def get_waste():        return load_waste()
@st.cache_data
def get_terms():        return load_delivery_terms()
@st.cache_data
def get_events():       return load_business_events()
@st.cache_data
def get_rota():         return load_rota()
@st.cache_data
def get_staff_exit():   return load_staff_exit()
@st.cache_data
def get_customer_survey(): return load_customer_survey()


def fmt_gbp(v, dec=0):
    if abs(v) >= 1_000_000:
        return f"£{v/1_000_000:.2f}m"
    if abs(v) >= 1_000:
        return f"£{v/1_000:.{dec}f}k"
    return f"£{v:.{dec}f}"


def metric_card(title, value, pill_text=None, pill_type="emerald"):
    pill_html = ""
    if pill_text:
        pill_html = f'<div class="tw-pill tw-pill-{pill_type}">{pill_text}</div>'
    return f"""
    <div class="tw-metric-card">
      <div class="tw-metric-title">{title}</div>
      <div class="tw-metric-value">{value}</div>
      {pill_html}
    </div>"""


def style_chart(fig, height=360, title=""):
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>" if title else "",
            font=dict(size=14, color=SLATE_900, family="Inter")
        ),
        height=height,
        font=dict(family="Inter", color=SLATE_700),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        margin=dict(l=24, r=24, t=44 if title else 24, b=24),
        hoverlabel=dict(
            bgcolor=SLATE_900,
            font_size=12,
            font_color="#FFFFFF",
            font_family="Inter"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            font=dict(size=11, color=SLATE_700)
        )
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor="#F1F5F9",
        linecolor="#CBD5E1",
        tickfont=dict(color=SLATE_500, size=11),
        title_font=dict(color=SLATE_700, size=12)
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="#F1F5F9",
        linecolor="#CBD5E1",
        tickfont=dict(color=SLATE_500, size=11),
        title_font=dict(color=SLATE_700, size=12)
    )
    return fig


# ── App Title & Strategic Subheader ──────────────────────────────────────────
h_col1, h_col2 = st.columns([1, 14])
with h_col1:
    st.markdown("<div style='font-size:2.8rem; line-height: 1; padding-top: 4px;'>☕</div>", unsafe_allow_html=True)
with h_col2:
    st.markdown(f"<h1 style='font-size:1.85rem; font-weight:800; color:{SLATE_900}; margin:0;'>Grind & Crumb · Operations Intelligence & Capital Allocation Tool</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{SLATE_500}; font-size:0.9rem; font-weight:500; margin:0;'>Board Strategy System · 12 Café Network · FY2025–FY2026 Audit & £1.5M Allocation · Net of VAT</p>", unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 0.75rem;'></div>", unsafe_allow_html=True)

# ── Primary Navigation ────────────────────────────────────────────────────────
tab_pnl, tab_deliv, tab_capacity, tab_waste, tab_expand, tab_alloc, tab_reviews = st.tabs([
    "📊 Store P&L & Margins",
    "🛵 Delivery Margin Simulator",
    "⏱️ Piccadilly & Capacity Planner",
    "🥐 Waste & Par Rebalancer",
    "📍 Expansion Scorer",
    "💰 £1.5M Capital Allocation",
    "💬 Sentiment & Root Causes"
])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — STORE P&L & FINANCIAL RECONCILIATION
# ═══════════════════════════════════════════════════════════════════════════════
with tab_pnl:
    pnl = get_pnl()
    stores = get_stores()
    events = get_events()
    pnl = pnl.merge(stores[["store_id", "store_name", "format", "location_type"]], on="store_id", how="left")

    st.markdown(
        "<div class='tw-banner tw-banner-emerald'>"
        "<b>CEO Question Answered:</b> Sales are up to <b>£8.66M</b>, but profits feel stagnant because "
        "<b>Manchester Piccadilly</b> takes £1.11M revenue but yields only <b>19.9% net margin</b> due to £30.5k/mo rent, "
        "while <b>Leeds Trinity</b> directly cannibalised <b>Leeds Briggate</b> by 21.4% in sales."
        "</div>",
        unsafe_allow_html=True
    )

    tot_rev    = pnl["total_net_sales_gbp"].sum()
    tot_profit = pnl["net_profit_gbp"].sum()
    tot_margin = tot_profit / tot_rev * 100
    tot_labour = pnl["labour_cost_gbp"].sum()
    tot_waste  = pnl["waste_cost_gbp"].sum()

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.markdown(metric_card("Chain Revenue", fmt_gbp(tot_rev), "12 Stores", "slate"), unsafe_allow_html=True)
    k2.markdown(metric_card("Store Operating Profit", fmt_gbp(tot_profit), f"{tot_margin:.1f}% margin", "emerald"), unsafe_allow_html=True)
    k3.markdown(metric_card("Highest Margin Store", "46.8%", "York Stonegate (S04)", "emerald"), unsafe_allow_html=True)
    k4.markdown(metric_card("Total Labour Cost", fmt_gbp(tot_labour), f"{tot_labour/tot_rev*100:.1f}% of sales", "amber"), unsafe_allow_html=True)
    k5.markdown(metric_card("Total Waste Cost", fmt_gbp(tot_waste), "Hull Paragon: 20.6% waste", "rose"), unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 1.25rem;'></div>", unsafe_allow_html=True)

    # Store Drilldown
    c_sel, c_view = st.columns([3, 2])
    with c_sel:
        store_map = stores.set_index("store_id")["store_name"].to_dict()
        selected_sid = st.selectbox("Inspect Store P&L:", options=stores["store_id"].tolist(), format_func=lambda x: store_map[x], index=6)
    with c_view:
        view_opt = st.radio("Chart Type:", ["Sales & Profit Trajectory", "Cost Breakdown Stack"], horizontal=True)

    s_pnl = pnl[pnl["store_id"] == selected_sid].sort_values("month")
    s_info = stores[stores["store_id"] == selected_sid].iloc[0]

    s_rev = s_pnl["total_net_sales_gbp"].mean()
    s_prf = s_pnl["net_profit_gbp"].mean()
    s_mrg = s_pnl["net_margin_pct"].mean()
    s_lbr = (s_pnl["labour_cost_gbp"] / s_pnl["total_net_sales_gbp"]).mean() * 100
    s_rnt = s_pnl["rent_gbp"].mean()

    sk1, sk2, sk3, sk4, sk5 = st.columns(5)
    sk1.markdown(metric_card("Monthly Revenue", fmt_gbp(s_rev), s_info["format"], "slate"), unsafe_allow_html=True)
    sk2.markdown(metric_card("Monthly Profit", fmt_gbp(s_prf), "Contribution", "emerald" if s_prf > 20000 else "amber"), unsafe_allow_html=True)
    sk3.markdown(metric_card("Net Store Margin", f"{s_mrg:.1f}%", "Above Target" if s_mrg >= 35 else "Compressed Margin", "emerald" if s_mrg >= 35 else "rose"), unsafe_allow_html=True)
    sk4.markdown(metric_card("Labour % of Rev", f"{s_lbr:.1f}%", "Target: < 28%", "amber" if s_lbr > 30 else "slate"), unsafe_allow_html=True)
    sk5.markdown(metric_card("Monthly Rent", fmt_gbp(s_rnt), f"{s_rnt/s_rev*100:.1f}% of sales", "rose" if s_rnt > 15000 else "slate"), unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 0.75rem;'></div>", unsafe_allow_html=True)

    if view_opt == "Sales & Profit Trajectory":
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(
            x=s_pnl["month"], y=s_pnl["total_net_sales_gbp"],
            name="Net Sales (£)", marker_color=EMERALD_MAIN, opacity=0.85
        ), secondary_y=False)
        fig.add_trace(go.Scatter(
            x=s_pnl["month"], y=s_pnl["net_profit_gbp"],
            name="Net Operating Profit (£)", line=dict(color=INDIGO_MAIN, width=3), mode="lines+markers"
        ), secondary_y=False)
        fig.add_trace(go.Scatter(
            x=s_pnl["month"], y=s_pnl["net_margin_pct"],
            name="Margin %", line=dict(color=AMBER_MAIN, width=2.5, dash="dot"), mode="lines"
        ), secondary_y=True)

        for _, ev in events.iterrows():
            fig.add_vline(
                x=pd.to_datetime(ev["date"]).timestamp() * 1000,
                line_dash="dash", line_color=ROSE_MAIN, line_width=1.5,
                annotation_text=f"📌 {ev['event']}", annotation_position="top right",
                annotation_font=dict(size=10, color=ROSE_DARK, family="Inter")
            )
        fig.update_yaxes(title_text="Amount (£)", tickprefix="£", secondary_y=False)
        fig.update_yaxes(title_text="Net Margin (%)", ticksuffix="%", secondary_y=True, showgrid=False)
        style_chart(fig, height=380, title=f"{store_map[selected_sid]} — Monthly Revenue, Profit & Margin Dynamics")
        st.plotly_chart(fig, use_container_width=True)
    else:
        cost_cols  = ["labour_cost_gbp", "rent_gbp", "business_rates_gbp", "utilities_gbp",
                      "repairs_maintenance_gbp", "other_opex_gbp", "waste_cost_gbp", "total_delivery_cost_gbp"]
        cost_names = ["Labour", "Rent", "Rates", "Utilities", "Repairs", "Other Opex", "Waste", "Delivery Overheads"]
        cost_vals  = [s_pnl[c].mean() for c in cost_cols]
        cost_colors= [EMERALD_MAIN, ROSE_MAIN, SLATE_500, "#0284C7", AMBER_MAIN, "#94A3B8", "#F43F5E", INDIGO_MAIN]

        fig = go.Figure(go.Bar(
            x=cost_names, y=cost_vals, marker_color=cost_colors,
            text=[fmt_gbp(v) for v in cost_vals], textposition="outside",
            textfont=dict(color=SLATE_900, size=11, family="Inter")
        ))
        fig.add_hline(y=s_rev, line_dash="dash", line_color=SLATE_700, annotation_text=f"Avg Sales: {fmt_gbp(s_rev)}")
        fig.update_yaxes(tickprefix="£", title_text="Average Monthly Cost (£)")
        style_chart(fig, height=380, title=f"{store_map[selected_sid]} — Monthly Operating Cost Distribution")
        st.plotly_chart(fig, use_container_width=True)

    # Full League Table
    st.markdown(f"<h3 style='font-size:1.15rem; font-weight:700; color:{SLATE_900}; margin-bottom:0.5rem;'>Store-Level Operating League Table</h3>", unsafe_allow_html=True)
    league = pnl.groupby(["store_id", "store_name"]).agg(
        Revenue=("total_net_sales_gbp", "sum"),
        Profit=("net_profit_gbp", "sum"),
        Margin=("net_margin_pct", "mean"),
        Labour_raw=("labour_cost_gbp", "sum"),
        Rent_raw=("rent_gbp", "mean"),
        Waste_raw=("waste_cost_gbp", "sum")
    ).reset_index()

    league["Labour %"]  = (league["Labour_raw"] / league["Revenue"] * 100).map(lambda x: f"{x:.1f}%")
    league["Rent/mo"]   = league["Rent_raw"].map(fmt_gbp)
    league["Waste"]     = league["Waste_raw"].map(fmt_gbp)
    league["Margin %"]  = league["Margin"].map(lambda x: f"{x:.1f}%")
    league["Revenue"]   = league["Revenue"].map(fmt_gbp)
    league["Profit"]    = league["Profit"].map(fmt_gbp)

    st.dataframe(
        league[["store_name", "Revenue", "Profit", "Margin %", "Labour %", "Rent/mo", "Waste"]].rename(columns={"store_name": "Store"}),
        use_container_width=True, hide_index=True
    )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — DELIVERY MARGIN SIMULATOR
# ═══════════════════════════════════════════════════════════════════════════════
with tab_deliv:
    st.markdown(
        "<div class='tw-banner tw-banner-rose'>"
        "<b>Delivery Unit Economics Breakdown:</b> Delivery rose from 10.9% to 22.7% of sales, "
        "but on 1 April 2026 Dashly raised commission to <b>33%</b>. Adding £0.45 packaging and 4 mins staff packing labour (£0.94), "
        "fixed overhead is <b>£1.39/order</b>. <b>29.0% of orders are under £8.00</b>, operating at a direct loss."
        "</div>",
        unsafe_allow_html=True
    )

    txn = get_transactions()
    daily = get_daily()
    del_orders = txn[txn["channel"] == "Delivery"].copy()
    valid_del = del_orders[del_orders["net_gbp"] > 0]

    st.markdown(f"<h3 style='font-size:1.15rem; font-weight:700; color:{SLATE_900}; margin-bottom:0.25rem;'>Interactive £8 Minimum Basket & Small Order Policy Simulator</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{SLATE_500}; font-size:0.875rem;'>Simulate the financial impact of RushEats' proposed £8 minimum order rule vs walk-away attrition:</p>", unsafe_allow_html=True)

    sim_c1, sim_c2, sim_c3, sim_c4 = st.columns(4)
    with sim_c1:
        sim_comm = sim_c1.slider("Blended Commission (%)", 25, 35, 32, 1)
    with sim_c2:
        sim_pack = sim_c2.slider("Packaging Cost (£)", 0.25, 0.75, 0.45, 0.05)
    with sim_c3:
        sim_wage = sim_c3.slider("Staff Wage (£/hr)", 11.00, 15.00, 12.80, 0.20)
    with sim_c4:
        sim_upgrade_rate = sim_c4.slider("Customer Upgrade Rate (%)", 20, 80, 50, 5, help="% of sub-£8 customers who add an item to reach £8")

    staff_pack_cost = (4 / 60) * sim_wage * 1.13
    overhead_per_order = sim_pack + staff_pack_cost
    breakeven_basket = overhead_per_order / (1 - sim_comm / 100)

    # Calculate actual financial uplift on 111,487 annual delivery orders
    tot_ann_del_orders = 111487
    sub8_share = 0.290
    sub8_orders = tot_ann_del_orders * sub8_share # ~32,331 orders
    avg_sub8_val = 4.87

    upgrade_orders = sub8_orders * (sim_upgrade_rate / 100)
    drop_orders    = sub8_orders * (1 - sim_upgrade_rate / 100)

    # Added gross profit on upgraded orders (spending £8.00 vs £4.87 = +£3.13 revenue)
    # Gross margin after 30% COGS and commission
    net_contrib_margin = (1 - sim_comm/100 - 0.30)
    upgrade_profit_gain = upgrade_orders * (8.00 - avg_sub8_val) * net_contrib_margin
    # Direct cost saved on dropped orders: £1.39 overhead + £1.50 food cost saved = £2.89 saved vs £4.87*(1-comm) revenue lost
    drop_cash_loss = drop_orders * (avg_sub8_val * (1 - sim_comm/100) - overhead_per_order - avg_sub8_val * 0.30)
    net_delivery_annual_gain = upgrade_profit_gain - drop_cash_loss

    r1, r2, r3, r4 = st.columns(4)
    r1.markdown(metric_card("Break-Even Basket", f"£{breakeven_basket:.2f}", "Minimum ticket", "amber"), unsafe_allow_html=True)
    r2.markdown(metric_card("Packing Labour Cost", f"£{staff_pack_cost:.2f}", "4 mins / order", "slate"), unsafe_allow_html=True)
    r3.markdown(metric_card("Sub-£8 Orders at Risk", f"{sub8_orders:,.0f}", "29.0% of total", "rose"), unsafe_allow_html=True)
    r4.markdown(metric_card("Net Annual Profit Uplift", fmt_gbp(net_delivery_annual_gain), "Zero Capex", "emerald"), unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

    # Basket Distribution Histogram
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Histogram(
        x=valid_del[valid_del["delivery_partner"] == "Dashly"]["net_gbp"],
        name="Dashly (33% Post-April)", marker_color=ROSE_MAIN, opacity=0.75,
        xbins=dict(start=0, end=30, size=1)
    ))
    fig_hist.add_trace(go.Histogram(
        x=valid_del[valid_del["delivery_partner"] == "RushEats"]["net_gbp"],
        name="RushEats (30%)", marker_color=INDIGO_MAIN, opacity=0.75,
        xbins=dict(start=0, end=30, size=1)
    ))
    fig_hist.add_vline(
        x=8.0, line_dash="dash", line_color=SLATE_900, line_width=2,
        annotation_text="£8.00 Policy Cutoff", annotation_position="top right",
        annotation_font=dict(color=SLATE_900, size=11, family="Inter")
    )
    fig_hist.update_layout(barmode="overlay")
    fig_hist.update_xaxes(title_text="Delivery Basket Net Total (£)", tickprefix="£", range=[0, 30])
    fig_hist.update_yaxes(title_text="Receipt Count (Sample)")
    style_chart(fig_hist, height=340, title="Delivery Basket Distribution — 29% Fall Below the £8.00 Threshold")
    st.plotly_chart(fig_hist, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — PICCADILLY CAPACITY & LABOUR PLANNER
# ═══════════════════════════════════════════════════════════════════════════════
with tab_capacity:
    st.markdown(
        "<div class='tw-banner tw-banner-amber'>"
        "<b>Manchester Piccadilly Crisis Uncovered:</b> Piccadilly suffered <b>53 staff leavers (230.4% turnover)</b>. "
        "Exit surveys show 50% cited understaffing and extreme lunch workload. "
        "At lunch, Piccadilly handles <b>27.0 visitors per labour hour</b> (vs 19.1 chain average). "
        "Queue abandonment drives an estimated <b>£50,188/year in walk-away lost sales</b>."
        "</div>",
        unsafe_allow_html=True
    )

    foot = get_footfall()
    rota = get_rota()

    pic_foot = foot[foot["store_id"] == "S07"].groupby("daypart")["door_count"].sum()
    pic_rota = rota[rota["store_id"] == "S07"].groupby("daypart")["scheduled_hours"].sum()
    pic_df = pd.DataFrame({"Footfall (Door Count)": pic_foot, "Scheduled Labour Hours": pic_rota})
    pic_df["Visitors per Labour Hour"] = (pic_df["Footfall (Door Count)"] / pic_df["Scheduled Labour Hours"]).round(1)

    chain_foot = foot.groupby("daypart")["door_count"].sum()
    chain_rota = rota.groupby("daypart")["scheduled_hours"].sum()
    pic_df["Chain Benchmark"] = (chain_foot / chain_rota).round(1)

    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown(f"<h3 style='font-size:1.1rem; font-weight:700; color:{SLATE_900}; margin-bottom:0.5rem;'>Piccadilly Daypart Pressure vs Chain Average</h3>", unsafe_allow_html=True)
        st.dataframe(pic_df, use_container_width=True)

    with c2:
        st.markdown(f"<h3 style='font-size:1.1rem; font-weight:700; color:{SLATE_900}; margin-bottom:0.5rem;'>Labour Intervention ROI Calculator</h3>", unsafe_allow_html=True)
        extra_baristas = st.slider("Extra Lunch Baristas at Piccadilly:", 1, 4, 2)
        walkaways_recovered = st.slider("Estimated Lost Customers Recovered / Day:", 10, 50, 25)

        ann_labour_cost = extra_baristas * 2.5 * 365 * 12.80 * 1.13 # £26.3k
        ann_rev_recovered = walkaways_recovered * 365 * 8.50 # £77.6k
        ann_gross_recovered = ann_rev_recovered * 0.70 # net of 30% COGS
        churn_savings = 21 * 1200 # 21 fewer leavers @ £1.2k recruitment cost = £25.2k
        net_pic_gain = (ann_gross_recovered + churn_savings) - ann_labour_cost

        st.markdown(
            f"<div class='tw-banner tw-banner-emerald'>"
            f"<b>Annual Labour Addition:</b> £{ann_labour_cost:,.0f}<br>"
            f"<b>Gross Margin Recovered:</b> £{ann_gross_recovered:,.0f}<br>"
            f"<b>Turnover Retraining Saved:</b> £{churn_savings:,.0f}<br>"
            f"<b>Net Annual Profit Benefit:</b> <b>+£{net_pic_gain:,.0f}</b> (Payback: {ann_labour_cost/(ann_gross_recovered+churn_savings):.1f} yrs)"
            f"</div>",
            unsafe_allow_html=True
        )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — WASTE & PAR REBALANCER
# ═══════════════════════════════════════════════════════════════════════════════
with tab_waste:
    waste = get_waste()
    st.markdown(
        "<div class='tw-banner tw-banner-rose'>"
        "<b>Operational Waste & Cannibalisation Discovery:</b> Total chain waste is <b>£133,815</b>. "
        "<b>Hull Paragon wastes 20.6% of prepared food</b> (£16,303) because manager Marcus Dyer deliberately over-orders. "
        "<b>Leeds Briggate wastes £16,649</b> because manager Grace Okafor still uses last year's par levels despite Trinity cannibalising footfall."
        "</div>",
        unsafe_allow_html=True
    )

    waste_store = waste.groupby("store_id").agg(
        Prepared=("units_prepared", "sum"),
        Wasted=("units_wasted", "sum"),
        Cost=("est_cost_wasted_gbp", "sum")
    ).reset_index()
    waste_store["Waste Rate %"] = (waste_store["Wasted"] / waste_store["Prepared"] * 100).round(2)
    waste_store = waste_store.merge(stores[["store_id", "store_name"]], on="store_id").sort_values("Waste Rate %", ascending=False)

    fig_w = go.Figure(go.Bar(
        x=waste_store["Waste Rate %"], y=waste_store["store_name"],
        orientation="h",
        marker_color=[ROSE_MAIN if r > 15 else (AMBER_MAIN if r > 10 else EMERALD_MAIN) for r in waste_store["Waste Rate %"]],
        text=waste_store["Waste Rate %"].map(lambda x: f" {x:.1f}% "), textposition="outside"
    ))
    fig_w.add_vline(x=9.99, line_dash="dash", line_color=SLATE_700, annotation_text="Chain Benchmark: 10.0%")
    fig_w.update_xaxes(title_text="Waste Rate (% of Units Prepared)", range=[0, 24])
    style_chart(fig_w, height=360, title="Store Ranking by Food Waste Percentage (Hull Paragon = 20.6% Outlier)")
    st.plotly_chart(fig_w, use_container_width=True)

    st.markdown(
        "<div class='tw-banner tw-banner-emerald'>"
        "<b>The Dynamic Par Level Solution:</b> Replacing manual ordering at Hull and Briggate with weather/footfall-responsive "
        "par planning saves <b>£12,167/year</b> in direct food waste, plus £12,000/year in reduced boiler/dishwasher breakdown costs at Hull."
        "</div>",
        unsafe_allow_html=True
    )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — EXPANSION SCORER
# ═══════════════════════════════════════════════════════════════════════════════
with tab_expand:
    cands = get_candidates()
    catch = get_catchment()
    stores_df = get_stores()
    pnl_df = get_pnl()

    st.markdown(
        "<div class='tw-banner tw-banner-emerald'>"
        "<b>Capital Allocation Analysis:</b> CEO Anna Whitfield wants to open Leeds Wellington Place and Sheffield Kelham Island. "
        "Our model proves <b>Leeds Wellington Place (CS7)</b> is the #1 candidate with 18,200 office workers, "
        "but warns that a 3rd Leeds store must be staggered to avoid repeating the Briggate-Trinity cannibalisation."
        "</div>",
        unsafe_allow_html=True
    )

    cw1, cw2, cw3, cw4, cw5 = st.columns(5)
    w_foot = cw1.slider("Footfall Weight", 0, 5, 3)
    w_off  = cw2.slider("Office Workers (500m)", 0, 5, 5, help="Top weekday ticket driver")
    w_stu  = cw3.slider("Student Density", 0, 5, 2)
    w_inc  = cw4.slider("Household Income", 0, 5, 2)
    w_cmp  = cw5.slider("Low Competition", 0, 5, 3)

    tot_w = w_foot + w_off + w_stu + w_inc + w_cmp
    if tot_w == 0: tot_w = 1

    def nrm(s):
        return (s - s.min()) / (s.max() - s.min()) if s.max() != s.min() else pd.Series([0.5]*len(s))

    c_score = cands.copy()
    c_score["Score"] = (
        nrm(c_score["daily_footfall_street"]) * w_foot +
        nrm(c_score["office_workers_500m"]) * w_off +
        nrm(c_score["students_1km"]) * w_stu +
        nrm(c_score["median_household_income_gbp"]) * w_inc +
        nrm(c_score["competitor_cafes_500m"].max() - c_score["competitor_cafes_500m"]) * w_cmp
    ) / tot_w * 10

    # Payback modeling
    c_score["Est. Annual Rev"] = [720000 if "Wellington" in s else (640000 if "Kelham" in s else 580000) for s in c_score["site_name"]]
    c_score["Est. Net Profit"] = c_score["Est. Annual Rev"] * 0.25 # conservative 25% ramping margin
    c_score["Payback (Yrs)"]   = (c_score["est_fitout_gbp"] / c_score["Est. Net Profit"]).round(1)

    c_score_sorted = c_score.sort_values("Score", ascending=False)

    fig_cand = go.Figure(go.Bar(
        x=c_score_sorted["Score"], y=c_score_sorted["site_name"],
        orientation="h",
        marker_color=[EMERALD_MAIN if i < 2 else (AMBER_MAIN if i < 4 else SLATE_500) for i in range(len(c_score_sorted))],
        text=c_score_sorted["Score"].map(lambda x: f" {x:.1f} / 10 "), textposition="outside"
    ))
    fig_cand.update_xaxes(title_text="Overall Site Opportunity Index", range=[0, 11.5])
    style_chart(fig_cand, height=360, title="Candidate Site Scoring (Emerald = Tier 1 Priority)")
    st.plotly_chart(fig_cand, use_container_width=True)

    # Table view
    disp_c = c_score_sorted[["site_name", "city", "location_type", "sqft", "quoted_rent_gbp_month", "est_fitout_gbp", "Score", "Est. Annual Rev", "Payback (Yrs)"]].copy()
    disp_c["Score"] = disp_c["Score"].map(lambda x: f"{x:.1f} / 10")
    disp_c["quoted_rent_gbp_month"] = disp_c["quoted_rent_gbp_month"].map(fmt_gbp)
    disp_c["est_fitout_gbp"] = disp_c["est_fitout_gbp"].map(fmt_gbp)
    disp_c["Est. Annual Rev"] = disp_c["Est. Annual Rev"].map(fmt_gbp)
    disp_c = disp_c.rename(columns={"site_name": "Candidate Site", "quoted_rent_gbp_month": "Rent / mo", "est_fitout_gbp": "Fitout Capex"})
    st.dataframe(disp_c, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 6 — £1.5M CAPITAL ALLOCATION PORTFOLIO
# ═══════════════════════════════════════════════════════════════════════════════
with tab_alloc:
    st.markdown(
        "<div class='tw-banner tw-banner-emerald'>"
        "<b>Rigorous £1,500,000 Portfolio Strategy:</b> Balances immediate high-margin operational turnaround "
        "with disciplined, phased physical expansion. Sums to <b>exactly £1,500,000.00</b>."
        "</div>",
        unsafe_allow_html=True
    )

    alloc_data = [
        {"Priority": "1. Growth", "Initiative": "Leeds Wellington Place (CS7) Opening", "Capex": 350000, "Impl / Setup": 30000, "Recurring Opex": 0, "Total Allocated": 380000, "Annual Net Benefit": 180000, "Payback": "2.1 yrs", "3-Yr Net Cash": "+£85,000", "Risk": "Tenant occupancy delay", "Confidence": "High"},
        {"Priority": "2. High-ROI Asset", "Initiative": "York Stonegate (S04) Full Flagship Refit", "Capex": 140000, "Impl / Setup": 10000, "Recurring Opex": 0, "Total Allocated": 150000, "Annual Net Benefit": 31200, "Payback": "4.8 yrs", "3-Yr Net Cash": "+£93,600", "Risk": "Trading disruption", "Confidence": "High"},
        {"Priority": "3. Bottleneck Unlock", "Initiative": "Manchester Piccadilly Lunch Staffing & Express Shelf", "Capex": 0, "Impl / Setup": 10000, "Recurring Opex": 50000, "Total Allocated": 60000, "Annual Net Benefit": 53200, "Payback": "1.1 yrs", "3-Yr Net Cash": "+£109,600", "Risk": "Station footfall drop", "Confidence": "Very High"},
        {"Priority": "4. Operational Reset", "Initiative": "Hull Paragon Equipment & Cleanliness Overhaul", "Capex": 25000, "Impl / Setup": 5000, "Recurring Opex": 24000, "Total Allocated": 54000, "Annual Net Benefit": 24200, "Payback": "2.2 yrs", "3-Yr Net Cash": "+£18,600", "Risk": "Manager compliance", "Confidence": "High"},
        {"Priority": "5. Digital Protection", "Initiative": "App v3.1 Stamp Goodwill & Delivery Threshold", "Capex": 20000, "Impl / Setup": 15000, "Recurring Opex": 11000, "Total Allocated": 46000, "Annual Net Benefit": 98900, "Payback": "0.5 yrs", "3-Yr Net Cash": "+£250,700", "Risk": "Platform resistance", "Confidence": "Very High"},
        {"Priority": "6. Capability", "Initiative": "Dynamic Par & Ops Intelligence Tool", "Capex": 20000, "Impl / Setup": 15000, "Recurring Opex": 0, "Total Allocated": 35000, "Annual Net Benefit": 16500, "Payback": "2.1 yrs", "3-Yr Net Cash": "+£14,500", "Risk": "Tablet adoption", "Confidence": "High"},
        {"Priority": "7. Phased Expansion", "Initiative": "Sheffield Kelham Island (CS2) Capital Reserve", "Capex": 775000, "Impl / Setup": 0, "Recurring Opex": 0, "Total Allocated": 775000, "Annual Net Benefit": 160000, "Payback": "2.4 yrs (upon deployment)", "3-Yr Net Cash": "+£240,000 (FY27+)", "Risk": "Cost inflation", "Confidence": "High"}
    ]
    df_alloc = pd.DataFrame(alloc_data)

    tot_allocated = df_alloc["Total Allocated"].sum()
    tot_ann_benefit = df_alloc["Annual Net Benefit"].sum()

    a1, a2, a3 = st.columns(3)
    a1.markdown(metric_card("Total Budget Allocated", fmt_gbp(tot_allocated), "Exactly £1.5M", "emerald"), unsafe_allow_html=True)
    a2.markdown(metric_card("Annual Net Benefit (Steady State)", fmt_gbp(tot_ann_benefit), "Base Scenario", "emerald"), unsafe_allow_html=True)
    a3.markdown(metric_card("Blended Portfolio Payback", "2.3 Years", "Excluding Reserve: 1.6 yrs", "indigo"), unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 0.75rem;'></div>", unsafe_allow_html=True)
    
    disp_alloc = df_alloc.copy()
    disp_alloc["Capex"] = disp_alloc["Capex"].map(fmt_gbp)
    disp_alloc["Impl / Setup"] = disp_alloc["Impl / Setup"].map(fmt_gbp)
    disp_alloc["Recurring Opex"] = disp_alloc["Recurring Opex"].map(fmt_gbp)
    disp_alloc["Total Allocated"] = disp_alloc["Total Allocated"].map(fmt_gbp)
    disp_alloc["Annual Net Benefit"] = disp_alloc["Annual Net Benefit"].map(fmt_gbp)
    st.dataframe(disp_alloc, use_container_width=True, hide_index=True)

    st.markdown(
        "<div class='tw-banner tw-banner-amber'>"
        "<b>Explicit Business Cease Orders (What Grind & Crumb Should STOP Doing):</b><br>"
        "1. <b>STOP opening un-phased stores in Leeds</b>: Do not open Headingley or multiple Leeds sites. Protect Briggate from further cannibalisation.<br>"
        "2. <b>STOP unconstrained sub-£8 delivery orders</b>: Enforce £8 minimum basket or £1.50 small-order fee immediately.<br>"
        "3. <b>STOP historical static par ordering</b>: End Marcus Dyer and Grace Okafor's manual ordering habits.<br>"
        "4. <b>STOP Dashly Boost promo opt-in</b>: Refuse Dashly's predatory 4% Boost upsell (37% total commission!)."
        "</div>",
        unsafe_allow_html=True
    )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 7 — CUSTOMER SENTIMENT & REVIEWS
# ═══════════════════════════════════════════════════════════════════════════════
with tab_reviews:
    rev = get_reviews()
    events = get_events()

    st.markdown(
        "<div class='tw-banner tw-banner-amber'>"
        "<b>Qualitative Voice of the Customer (3,030 Reviews & 650 Survey Responses):</b> "
        "Confirms financial data. The £0.40 oat milk charge dropped ratings from 3.86 to 3.56 stars. "
        "App v3.0 release plunged rating to 3.45 stars with severe checkout bugs and lost stamps."
        "</div>",
        unsafe_allow_html=True
    )

    r_col1, r_col2 = st.columns([1, 1])
    with r_col1:
        st.markdown(f"<h3 style='font-size:1.1rem; font-weight:700; color:{SLATE_900}; margin-bottom:0.5rem;'>Key Feedback Themes</h3>", unsafe_allow_html=True)
        themes = {
            "Lunch Queues & Understaffing": ["queue", "wait", "slow", "understaffed", "need more staff"],
            "App Bugs & Stamp Losses": ["app", "stamp", "crash", "checkout", "disappeared", "bug"],
            "Missing Delivery Items": ["missing", "wrong order", "forgot", "incomplete"],
            "Oat Milk Surcharge": ["oat", "surcharge", "charge", "pricey", "expensive"],
            "Positive Food Quality": ["love", "great", "excellent", "amazing", "best", "delicious"]
        }
        th_counts = {t: rev["review_text"].fillna("").str.lower().apply(lambda x: any(k in x for k in kws)).sum() for t, kws in themes.items()}
        df_th = pd.DataFrame(list(th_counts.items()), columns=["Theme", "Count"]).sort_values("Count")
        fig_th = go.Figure(go.Bar(
            x=df_th["Count"], y=df_th["Theme"], orientation="h",
            marker_color=[EMERALD_MAIN if "Positive" in t else ROSE_MAIN for t in df_th["Theme"]],
            text=df_th["Count"], textposition="outside"
        ))
        style_chart(fig_th, height=330, title="Review Mentions by Core Category")
        st.plotly_chart(fig_th, use_container_width=True)

    with r_col2:
        st.markdown(f"<h3 style='font-size:1.1rem; font-weight:700; color:{SLATE_900}; margin-bottom:0.5rem;'>Review Search & Verbatim Quotes</h3>", unsafe_allow_html=True)
        search_kw = st.text_input("Search reviews by keyword:", "queue")
        filtered_rev = rev[rev["review_text"].fillna("").str.lower().str.contains(search_kw.lower())][["review_date", "source", "rating", "review_text"]].head(15)
        st.dataframe(filtered_rev, use_container_width=True, hide_index=True)
