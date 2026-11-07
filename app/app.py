"""
Grind & Crumb Intelligence Tool
Hackathon submission — Tailwind Modern Redesign
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

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
    load_business_events, build_store_pnl, load_footfall
)

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Grind & Crumb · Executive Intelligence",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Tailwind Modern Palette ──────────────────────────────────────────────────
# Deep slate for high contrast & crisp legibility
COLOR_SLATE_900 = "#0F172A"
COLOR_SLATE_700 = "#334155"
COLOR_SLATE_500 = "#64748B"
COLOR_SLATE_100 = "#F1F5F9"
COLOR_SLATE_50  = "#F8FAFC"

# Accents (Tailwind Emerald, Amber, Rose, Indigo)
COLOR_EMERALD   = "#059669"
COLOR_EMERALD_BG= "#ECFDF5"
COLOR_AMBER     = "#D97706"
COLOR_AMBER_BG  = "#FFFBEB"
COLOR_ROSE      = "#E11D48"
COLOR_ROSE_BG   = "#FFF1F2"
COLOR_INDIGO    = "#4F46E5"
COLOR_INDIGO_BG = "#EEF2FF"

# ── Global Tailwind-Style CSS ────────────────────────────────────────────────
st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
  
  html, body, [class*="css"] {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: {COLOR_SLATE_900};
  }}
  
  .stApp {{
    background-color: {COLOR_SLATE_50};
  }}

  .block-container {{
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1350px;
  }}

  /* Tailwind Card Style for Metrics */
  .tw-card {{
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 0.75rem;
    padding: 1.25rem 1.5rem;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px -1px rgba(0, 0, 0, 0.05);
    transition: all 0.2s ease-in-out;
  }}
  .tw-card:hover {{
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
  }}

  .tw-label {{
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: {COLOR_SLATE_500};
    margin-bottom: 0.35rem;
  }}

  .tw-value {{
    font-size: 1.75rem;
    font-weight: 800;
    color: {COLOR_SLATE_900};
    line-height: 1.2;
  }}

  .tw-badge {{
    display: inline-flex;
    align-items: center;
    padding: 0.2rem 0.55rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-top: 0.45rem;
  }}
  .tw-badge.emerald {{ background-color: {COLOR_EMERALD_BG}; color: {COLOR_EMERALD}; }}
  .tw-badge.rose    {{ background-color: {COLOR_ROSE_BG}; color: {COLOR_ROSE}; }}
  .tw-badge.amber   {{ background-color: {COLOR_AMBER_BG}; color: {COLOR_AMBER}; }}
  .tw-badge.slate   {{ background-color: {COLOR_SLATE_100}; color: {COLOR_SLATE_700}; }}

  /* Tailwind Alert Callout Boxes */
  .tw-alert {{
    border-radius: 0.5rem;
    padding: 1rem 1.25rem;
    margin: 1rem 0 1.25rem 0;
    font-size: 0.925rem;
    line-height: 1.5;
    border-left-width: 4px;
  }}
  .tw-alert-emerald {{
    background-color: {COLOR_EMERALD_BG};
    border-left-color: {COLOR_EMERALD};
    color: #064E3B;
  }}
  .tw-alert-amber {{
    background-color: {COLOR_AMBER_BG};
    border-left-color: {COLOR_AMBER};
    color: #78350F;
  }}
  .tw-alert-rose {{
    background-color: {COLOR_ROSE_BG};
    border-left-color: {COLOR_ROSE};
    color: #881337;
  }}

  /* Tab styling */
  div[data-testid="stTabs"] button {{
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    color: {COLOR_SLATE_700} !important;
    padding: 0.6rem 1.2rem !important;
  }}
  div[data-testid="stTabs"] button[aria-selected="true"] {{
    color: {COLOR_EMERALD} !important;
    border-bottom-color: {COLOR_EMERALD} !important;
  }}

  /* Dataframe contrast */
  div[data-testid="stDataFrame"] {{
    border: 1px solid #E2E8F0;
    border-radius: 0.5rem;
    overflow: hidden;
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
def get_weather():      return load_weather()


# ── Formatting Helpers ────────────────────────────────────────────────────────
def fmt_gbp(v, dec=0):
    if abs(v) >= 1_000_000:
        return f"£{v/1_000_000:.2f}m"
    if abs(v) >= 1_000:
        return f"£{v/1_000:.{dec}f}k"
    return f"£{v:.{dec}f}"


def metric_card(label, value, badge_text=None, badge_type="emerald"):
    badge_html = ""
    if badge_text:
        badge_html = f'<div class="tw-badge {badge_type}">{badge_text}</div>'
    return f"""
    <div class="tw-card">
      <div class="tw-label">{label}</div>
      <div class="tw-value">{value}</div>
      {badge_html}
    </div>"""


def apply_chart_theme(fig, height=360, title=""):
    """Applies a clean, high-contrast, modern Tailwind aesthetic to Plotly figures."""
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>" if title else "",
            font=dict(size=14, color=COLOR_SLATE_900, family="Inter")
        ),
        height=height,
        font=dict(family="Inter", color=COLOR_SLATE_700),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        margin=dict(l=24, r=24, t=44 if title else 24, b=24),
        hoverlabel=dict(
            bgcolor=COLOR_SLATE_900,
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
            font=dict(size=12, color=COLOR_SLATE_700)
        )
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor="#F1F5F9",
        linecolor="#CBD5E1",
        tickfont=dict(color=COLOR_SLATE_500, size=11),
        title_font=dict(color=COLOR_SLATE_700, size=12)
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="#F1F5F9",
        linecolor="#CBD5E1",
        tickfont=dict(color=COLOR_SLATE_500, size=11),
        title_font=dict(color=COLOR_SLATE_700, size=12)
    )
    return fig


# ── App Header ────────────────────────────────────────────────────────────────
col_logo, col_title = st.columns([1, 11])
with col_logo:
    st.markdown("<div style='font-size:2.8rem; line-height: 1; padding-top: 6px;'>☕</div>", unsafe_allow_html=True)
with col_title:
    st.markdown(f"<h1 style='font-size:1.9rem; font-weight:800; color:{COLOR_SLATE_900}; margin:0; padding-top:2px;'>Grind & Crumb · Executive Intelligence Platform</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{COLOR_SLATE_500}; font-size:0.925rem; font-weight:500; margin:0;'>Board Strategy & £1.5M Capital Allocation Model · 12 Stores · FY2025–FY2026 (Net of VAT)</p>", unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

# ── Navigation Tabs ───────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Store Profitability & P&L",
    "🛵 Delivery Economics",
    "📍 Site Expansion Scorer",
    "💬 Sentiment & Reviews",
])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — STORE PROFITABILITY
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    pnl    = get_pnl()
    stores = get_stores()
    events = get_events()

    pnl = pnl.merge(stores[["store_id","store_name","format","location_type"]], on="store_id", how="left")

    st.markdown(
        "<div class='tw-alert tw-alert-emerald'>"
        "<b>Strategic Overview:</b> Top-line chain revenue reached <b>£8.66M</b> with <b>£3.24M</b> store net profit (37.4% margin). "
        "However, profitability is heavily concentrated: <b>Manchester Piccadilly</b> takes £1.11M revenue but delivers only <b>20.2% margin</b> "
        "due to a crippling £30.5k/month rent bill. Meanwhile, <b>Leeds Trinity</b> has cannibalized <b>Leeds Briggate</b> by 20% in revenue."
        "</div>",
        unsafe_allow_html=True
    )

    # ── Chain-Wide KPI Ribbon ─────────────────────────────────────────────────
    total_sales  = pnl["total_net_sales_gbp"].sum()
    total_profit = pnl["net_profit_gbp"].sum()
    total_margin = total_profit / total_sales * 100
    total_labour = pnl["labour_cost_gbp"].sum()
    total_waste  = pnl["waste_cost_gbp"].sum()

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.markdown(metric_card("Chain Revenue", fmt_gbp(total_sales), "12 Stores", "slate"), unsafe_allow_html=True)
    k2.markdown(metric_card("Net Store Profit", fmt_gbp(total_profit), f"{total_margin:.1f}% margin", "emerald"), unsafe_allow_html=True)
    k3.markdown(metric_card("Top Performer Margin", "46.8%", "York Stonegate", "emerald"), unsafe_allow_html=True)
    k4.markdown(metric_card("Total Labour Cost", fmt_gbp(total_labour), f"{total_labour/total_sales*100:.1f}% of rev", "amber"), unsafe_allow_html=True)
    k5.markdown(metric_card("Total Waste Cost", fmt_gbp(total_waste), "Hull Paragon: 20.6% waste", "rose"), unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # ── Interactive Store Drill-Down ──────────────────────────────────────────
    st.markdown(f"<h3 style='font-size:1.2rem; font-weight:700; color:{COLOR_SLATE_900}; margin-bottom:0.75rem;'>Store Deep-Dive Analysis</h3>", unsafe_allow_html=True)

    col_sel, col_mode = st.columns([3, 2])
    with col_sel:
        store_names = stores.set_index("store_id")["store_name"].to_dict()
        selected_store = st.selectbox(
            "Select store to inspect financial trajectory:",
            options=stores["store_id"].tolist(),
            format_func=lambda x: store_names[x],
            index=6  # Manchester Piccadilly (S07)
        )
    with col_mode:
        view_mode = st.radio("Chart visualization:", ["Monthly Trend (Sales vs Profit)", "Cost Structure Breakdown"], horizontal=True)

    store_pnl  = pnl[pnl["store_id"] == selected_store].sort_values("month")
    store_info = stores[stores["store_id"] == selected_store].iloc[0]

    # Store individual metrics
    avg_margin = store_pnl["net_margin_pct"].mean()
    avg_sales  = store_pnl["total_net_sales_gbp"].mean()
    avg_profit = store_pnl["net_profit_gbp"].mean()
    avg_labour = (store_pnl["labour_cost_gbp"] / store_pnl["total_net_sales_gbp"]).mean() * 100
    avg_rent   = store_pnl["rent_gbp"].mean()

    sk1, sk2, sk3, sk4, sk5 = st.columns(5)
    sk1.markdown(metric_card("Monthly Revenue", fmt_gbp(avg_sales), store_info["format"], "slate"), unsafe_allow_html=True)
    sk2.markdown(metric_card("Monthly Profit", fmt_gbp(avg_profit), "Store Contribution", "emerald" if avg_profit > 20000 else "amber"), unsafe_allow_html=True)
    sk3.markdown(metric_card("Net Margin", f"{avg_margin:.1f}%", "Chain Rank" if avg_margin > 35 else "Underperforming", "emerald" if avg_margin >= 35 else "rose"), unsafe_allow_html=True)
    sk4.markdown(metric_card("Labour % of Rev", f"{avg_labour:.1f}%", "Benchmark: 28%", "amber" if avg_labour > 30 else "slate"), unsafe_allow_html=True)
    sk5.markdown(metric_card("Monthly Rent", fmt_gbp(avg_rent), f"{avg_rent/avg_sales*100:.1f}% of sales", "rose" if avg_rent > 15000 else "slate"), unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 0.75rem;'></div>", unsafe_allow_html=True)

    if view_mode == "Monthly Trend (Sales vs Profit)":
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Clear contrast: Emerald bars for sales, Deep Indigo for profit line, Amber dashed for margin
        fig.add_trace(go.Bar(
            x=store_pnl["month"], y=store_pnl["total_net_sales_gbp"],
            name="Net Sales",
            marker_color=COLOR_EMERALD,
            opacity=0.85
        ), secondary_y=False)

        fig.add_trace(go.Scatter(
            x=store_pnl["month"], y=store_pnl["net_profit_gbp"],
            name="Net Profit (£)",
            line=dict(color=COLOR_INDIGO, width=3),
            mode="lines+markers",
            marker=dict(size=6, color=COLOR_INDIGO)
        ), secondary_y=False)

        fig.add_trace(go.Scatter(
            x=store_pnl["month"], y=store_pnl["net_margin_pct"],
            name="Net Margin %",
            line=dict(color=COLOR_AMBER, width=2.5, dash="dot"),
            mode="lines"
        ), secondary_y=True)

        # Annotated vertical events
        store_events = events[(events["date"] >= store_pnl["month"].min()) & (events["date"] <= store_pnl["month"].max())]
        for _, ev in store_events.iterrows():
            fig.add_vline(
                x=pd.to_datetime(ev["date"]).timestamp() * 1000,
                line_dash="dash", line_color=COLOR_ROSE, line_width=1.5,
                annotation_text=f"📌 {ev['event']}",
                annotation_position="top right",
                annotation_font=dict(size=10, color=COLOR_ROSE, family="Inter")
            )

        fig.update_yaxes(title_text="Amount (£)", tickprefix="£", secondary_y=False)
        fig.update_yaxes(title_text="Net Margin (%)", ticksuffix="%", secondary_y=True, showgrid=False)
        apply_chart_theme(fig, height=390, title=f"{store_names[selected_store]} — Monthly Financial Trajectory")
        st.plotly_chart(fig, use_container_width=True)

    else:
        cost_cols  = ["labour_cost_gbp", "rent_gbp", "business_rates_gbp", "utilities_gbp",
                      "repairs_maintenance_gbp", "other_opex_gbp", "waste_cost_gbp", "total_delivery_cost_gbp"]
        cost_names = ["Labour", "Rent", "Rates", "Utilities", "Repairs", "Other Opex", "Waste", "Delivery Costs"]
        cost_vals  = [store_pnl[c].mean() for c in cost_cols]
        cost_palette = [COLOR_EMERALD, COLOR_ROSE, COLOR_SLATE_500, "#0284C7", COLOR_AMBER, "#94A3B8", "#F43F5E", COLOR_INDIGO]

        fig = go.Figure(go.Bar(
            x=cost_names, y=cost_vals,
            marker_color=cost_palette,
            text=[fmt_gbp(v) for v in cost_vals],
            textposition="outside",
            textfont=dict(color=COLOR_SLATE_900, size=11, family="Inter")
        ))
        fig.add_hline(
            y=avg_sales, line_dash="dash", line_color=COLOR_SLATE_700,
            annotation_text=f"Avg Monthly Sales: {fmt_gbp(avg_sales)}",
            annotation_position="top right",
            annotation_font=dict(color=COLOR_SLATE_700, size=11)
        )
        fig.update_yaxes(tickprefix="£", title_text="Average Monthly Cost (£)")
        apply_chart_theme(fig, height=390, title=f"{store_names[selected_store]} — Operating Cost Breakdown")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # ── All-Store Performance Comparison Table ────────────────────────────────
    st.markdown(f"<h3 style='font-size:1.2rem; font-weight:700; color:{COLOR_SLATE_900}; margin-bottom:0.75rem;'>Full Chain Performance League Table</h3>", unsafe_allow_html=True)

    league = pnl.groupby(["store_id", "store_name"]).agg(
        Revenue=("total_net_sales_gbp", "sum"),
        Profit=("net_profit_gbp", "sum"),
        Margin=("net_margin_pct", "mean"),
        Labour_raw=("labour_cost_gbp", "sum"),
        Rent_raw=("rent_gbp", "mean"),
        Waste_raw=("waste_cost_gbp", "sum"),
    ).reset_index()

    league["Labour %"] = (league["Labour_raw"] / league["Revenue"] * 100).map(lambda x: f"{x:.1f}%")
    league["Rent / mo"] = league["Rent_raw"].map(fmt_gbp)
    league["Waste (£)"] = league["Waste_raw"].map(fmt_gbp)
    league["Margin %"] = league["Margin"].map(lambda x: f"{x:.1f}%")
    league["Revenue (£)"] = league["Revenue"].map(fmt_gbp)
    league["Net Profit (£)"] = league["Profit"].map(fmt_gbp)

    display_table = league[["store_name", "Revenue (£)", "Net Profit (£)", "Margin %", "Labour %", "Rent / mo", "Waste (£)"]].rename(
        columns={"store_name": "Store Location"}
    )
    st.dataframe(display_table, use_container_width=True, hide_index=True)

    # ── Margin Ranking Horizontal Bar Chart ───────────────────────────────────
    margin_df = pnl.groupby(["store_id","store_name"])["net_margin_pct"].mean().reset_index().sort_values("net_margin_pct")
    margin_df["bar_color"] = margin_df["net_margin_pct"].apply(
        lambda x: COLOR_ROSE if x < 25 else (COLOR_AMBER if x < 35 else COLOR_EMERALD)
    )

    fig_rank = go.Figure(go.Bar(
        x=margin_df["net_margin_pct"],
        y=margin_df["store_name"],
        orientation="h",
        marker_color=margin_df["bar_color"],
        text=margin_df["net_margin_pct"].map(lambda x: f" {x:.1f}% "),
        textposition="outside",
        textfont=dict(color=COLOR_SLATE_900, size=11, family="Inter")
    ))
    fig_rank.add_vline(
        x=35, line_dash="dash", line_color=COLOR_SLATE_500, line_width=1.5,
        annotation_text="35% Target Margin",
        annotation_position="top right",
        annotation_font=dict(size=11, color=COLOR_SLATE_700)
    )
    fig_rank.update_xaxes(ticksuffix="%", title_text="Average Store Net Margin (%)", range=[0, 56])
    apply_chart_theme(fig_rank, height=400, title="Store Ranking by Net Profit Margin (Rose < 25% | Amber 25-35% | Emerald > 35%)")
    st.plotly_chart(fig_rank, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — DELIVERY ECONOMICS
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown(
        "<div class='tw-alert tw-alert-rose'>"
        "<b>Delivery Profitability Warning:</b> Delivery expanded from <b>10.9% to 22.7% of total sales</b> in 12 months. "
        "However, Dashly unilaterally hiked commission from <b>27% to 33%</b> on 1 April 2026. Combined with packaging (£0.45) "
        "and 4 minutes of barista prep time, <b>29% of delivery orders (< £8) operate at a direct loss</b>."
        "</div>",
        unsafe_allow_html=True
    )

    txn = get_transactions()
    terms = get_terms()
    daily = get_daily()

    monthly_all = daily.groupby("month").agg(
        total=("total_net_sales_gbp", "sum"),
        delivery=("net_sales_delivery_gbp", "sum"),
        instore=("net_sales_instore_gbp", "sum"),
        app=("net_sales_app_gbp", "sum"),
    ).reset_index()
    monthly_all["delivery_share"] = monthly_all["delivery"] / monthly_all["total"] * 100

    col_del_chart, col_del_stats = st.columns([2, 1])

    with col_del_chart:
        fig_del = make_subplots(specs=[[{"secondary_y": True}]])
        fig_del.add_trace(go.Bar(
            x=monthly_all["month"], y=monthly_all["instore"],
            name="In-Store", marker_color=COLOR_EMERALD, opacity=0.85
        ), secondary_y=False)
        fig_del.add_trace(go.Bar(
            x=monthly_all["month"], y=monthly_all["app"],
            name="Click & Collect App", marker_color=COLOR_INDIGO, opacity=0.75
        ), secondary_y=False)
        fig_del.add_trace(go.Bar(
            x=monthly_all["month"], y=monthly_all["delivery"],
            name="Delivery (Platforms)", marker_color=COLOR_AMBER, opacity=0.85
        ), secondary_y=False)
        fig_del.add_trace(go.Scatter(
            x=monthly_all["month"], y=monthly_all["delivery_share"],
            name="Delivery Share %", line=dict(color=COLOR_ROSE, width=3), mode="lines+markers"
        ), secondary_y=True)

        fig_del.add_vline(
            x=pd.to_datetime("2026-04-01").timestamp() * 1000,
            line_dash="dash", line_color=COLOR_ROSE, line_width=1.5,
            annotation_text="Dashly Commission 27% ➔ 33%",
            annotation_position="top left",
            annotation_font=dict(color=COLOR_ROSE, size=10)
        )
        fig_del.update_layout(barmode="stack")
        fig_del.update_yaxes(title_text="Revenue (£)", tickprefix="£", secondary_y=False)
        fig_del.update_yaxes(title_text="Delivery Share (%)", ticksuffix="%", secondary_y=True, showgrid=False)
        apply_chart_theme(fig_del, height=360, title="Sales by Channel with Growing Delivery Penetration")
        st.plotly_chart(fig_del, use_container_width=True)

    with col_del_stats:
        del_orders_sample = txn[txn["channel"] == "Delivery"].copy()
        tot_del_orders    = len(del_orders_sample)
        avg_basket        = del_orders_sample["net_gbp"].mean()
        orders_sub_8      = (del_orders_sample["net_gbp"] < 8.0).mean() * 100

        st.markdown(metric_card("Delivery Share of Sales", f"{monthly_all['delivery_share'].iloc[-1]:.1f}%", "June 2026 peak", "amber"), unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom:0.6rem;'></div>", unsafe_allow_html=True)
        st.markdown(metric_card("Average Delivery Order", f"£{avg_basket:.2f}", "Net of VAT", "slate"), unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom:0.6rem;'></div>", unsafe_allow_html=True)
        st.markdown(metric_card("Orders Under £8.00", f"{orders_sub_8:.1f}%", "Unprofitable threshold", "rose"), unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # ── Interactive Break-Even Simulator ──────────────────────────────────────
    st.markdown(f"<h3 style='font-size:1.2rem; font-weight:700; color:{COLOR_SLATE_900}; margin-bottom:0.25rem;'>Unit Economics & Minimum Basket Calculator</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{COLOR_SLATE_500}; font-size:0.875rem;'>Model how platform commissions, packaging fees, and barista wages impact the breakeven order value:</p>", unsafe_allow_html=True)

    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        commission_input = st.slider("Platform Commission Rate (%)", 20, 40, 33, 1, help="Dashly = 33%, RushEats = 30%")
    with sc2:
        packaging_input  = st.slider("Packaging Cost per Order (£)", 0.20, 1.00, 0.45, 0.05)
    with sc3:
        wage_input       = st.slider("Barista Hourly Wage (£)", 10.50, 15.00, 12.50, 0.25)

    staff_cost_calc = (4 / 60) * wage_input * 1.13  # 4 minutes prep + employer NI/pension (1.13)
    fixed_overhead  = packaging_input + staff_cost_calc
    breakeven_calc  = fixed_overhead / (1 - (commission_input / 100))

    basket_axis = np.linspace(1, 20, 100)
    profit_curve = basket_axis * (1 - commission_input / 100) - fixed_overhead

    fig_be = go.Figure()
    fig_be.add_trace(go.Scatter(
        x=basket_axis, y=profit_curve,
        mode="lines",
        line=dict(color=COLOR_EMERALD, width=3),
        name="Order Contribution (£)"
    ))
    fig_be.add_hline(y=0, line_dash="solid", line_color=COLOR_SLATE_500, line_width=1)
    fig_be.add_vline(
        x=breakeven_calc, line_dash="dash", line_color=COLOR_ROSE, line_width=2,
        annotation_text=f"Breakeven: £{breakeven_calc:.2f}",
        annotation_position="top left",
        annotation_font=dict(color=COLOR_ROSE, size=11, family="Inter")
    )
    fig_be.add_vline(
        x=8.0, line_dash="dot", line_color=COLOR_AMBER, line_width=1.5,
        annotation_text="RushEats £8.00 Threshold",
        annotation_position="bottom right",
        annotation_font=dict(color=COLOR_AMBER, size=11, family="Inter")
    )
    fig_be.update_xaxes(title_text="Customer Basket Value (£)", tickprefix="£")
    fig_be.update_yaxes(title_text="Contribution Margin (£)", tickprefix="£")
    apply_chart_theme(fig_be, height=330, title="Order Contribution Margin Curve vs Basket Size")
    st.plotly_chart(fig_be, use_container_width=True)

    # ── Basket Value Distribution ─────────────────────────────────────────────
    st.markdown(f"<h3 style='font-size:1.2rem; font-weight:700; color:{COLOR_SLATE_900}; margin-bottom:0.5rem;'>Order Basket Value Distribution (Dashly vs RushEats)</h3>", unsafe_allow_html=True)

    # Clean positive values for clear distribution
    valid_del_orders = del_orders_sample[del_orders_sample["net_gbp"] > 0]

    fig_hist = go.Figure()
    fig_hist.add_trace(go.Histogram(
        x=valid_del_orders[valid_del_orders["delivery_partner"] == "Dashly"]["net_gbp"],
        name="Dashly (33% Comm.)",
        marker_color=COLOR_ROSE,
        opacity=0.7,
        xbins=dict(start=0, end=30, size=1)
    ))
    fig_hist.add_trace(go.Histogram(
        x=valid_del_orders[valid_del_orders["delivery_partner"] == "RushEats"]["net_gbp"],
        name="RushEats (30% Comm.)",
        marker_color=COLOR_INDIGO,
        opacity=0.7,
        xbins=dict(start=0, end=30, size=1)
    ))
    fig_hist.add_vline(
        x=8.0, line_dash="dash", line_color=COLOR_SLATE_900, line_width=2,
        annotation_text="£8.00 Min Basket Cutoff",
        annotation_position="top right",
        annotation_font=dict(color=COLOR_SLATE_900, size=11)
    )
    fig_hist.update_layout(barmode="overlay")
    fig_hist.update_xaxes(title_text="Receipt Net Value (£)", tickprefix="£", range=[0, 30])
    fig_hist.update_yaxes(title_text="Order Frequency")
    apply_chart_theme(fig_hist, height=340, title="Delivery Basket Distribution — 29% of Orders Fall in the Negative Margin Zone")
    st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown(
        "<div class='tw-alert tw-alert-amber'>"
        "<b>Recommendation:</b> Enforce an <b>£8.00 minimum basket</b> on Dashly and RushEats. "
        "Assuming a conservative 50% walk-away rate and 50% upgrading basket size to £8.00, "
        "this unlocks an estimated <b>£52,000 net profit uplift</b> chain-wide with zero capital expenditure."
        "</div>",
        unsafe_allow_html=True
    )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — EXPANSION SCORER
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    candidates = get_candidates()
    catchment  = get_catchment()
    stores_df  = get_stores()
    pnl_df     = get_pnl()

    st.markdown(
        "<div class='tw-alert tw-alert-emerald'>"
        "<b>Capital Allocation Analysis (£1.5M Fund):</b> CEO Anna Whitfield instinctively favors Kelham Island (Sheffield) "
        "and Wellington Place (Leeds). Our empirical catchment model objectively evaluates all 7 prospective sites against "
        "store benchmarks to eliminate geographical bias and maximize capital payback."
        "</div>",
        unsafe_allow_html=True
    )

    # ── Interactive Scoring Weights ───────────────────────────────────────────
    st.markdown(f"<h3 style='font-size:1.2rem; font-weight:700; color:{COLOR_SLATE_900}; margin-bottom:0.25rem;'>Candidate Site Scoring Model</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{COLOR_SLATE_500}; font-size:0.875rem;'>Calibrate demographic weighting criteria based on strategic priorities:</p>", unsafe_allow_html=True)

    w1, w2, w3, w4, w5 = st.columns(5)
    w_footfall = w1.slider("Pedestrian Footfall", 0, 5, 3)
    w_office   = w2.slider("Office Workers (500m)", 0, 5, 5, help="Single biggest predictor of high weekday ticket volume")
    w_students = w3.slider("Student Population", 0, 5, 2)
    w_income   = w4.slider("Household Income", 0, 5, 2)
    w_comp     = w5.slider("Low Competition", 0, 5, 3)

    total_weight = w_footfall + w_office + w_students + w_income + w_comp
    if total_weight == 0: total_weight = 1

    def min_max(s):
        return (s - s.min()) / (s.max() - s.min()) if s.max() != s.min() else pd.Series([0.5]*len(s))

    cand = candidates.copy()
    cand["s_foot"] = min_max(cand["daily_footfall_street"])
    cand["s_off"]  = min_max(cand["office_workers_500m"])
    cand["s_stu"]  = min_max(cand["students_1km"])
    cand["s_inc"]  = min_max(cand["median_household_income_gbp"])
    cand["s_comp"] = min_max(cand["competitor_cafes_500m"].max() - cand["competitor_cafes_500m"])

    cand["Score"] = (
        cand["s_foot"] * w_footfall +
        cand["s_off"]  * w_office +
        cand["s_stu"]  * w_students +
        cand["s_inc"]  * w_income +
        cand["s_comp"] * w_comp
    ) / total_weight * 10

    # Benchmark revenue modeling
    store_rev_total = pnl_df.groupby("store_id")["total_net_sales_gbp"].sum().reset_index()
    store_rev_total.columns = ["store_id", "ann_rev"]
    bench_stores = stores_df.merge(catchment, on="store_id").merge(store_rev_total, on="store_id")

    office_bench = bench_stores[bench_stores["location_type"] == "Office district"]["ann_rev"].mean()
    highst_bench = bench_stores[bench_stores["location_type"] == "High street"]["ann_rev"].mean()
    transit_bench= bench_stores[bench_stores["location_type"] == "Transit"]["ann_rev"].mean()

    def calc_site_rev(row):
        lt = row["location_type"]
        base = office_bench if lt == "Office district" else (transit_bench if lt == "Transit" else highst_bench)
        bench_foot = bench_stores[bench_stores["location_type"] == lt]["daily_footfall_street"].mean() if lt in bench_stores["location_type"].values else 30000
        ratio = row["daily_footfall_street"] / bench_foot if bench_foot > 0 else 1
        return base * min(max(ratio, 0.7), 1.4)

    cand["est_rev"] = cand.apply(calc_site_rev, axis=1)
    chain_margin_ex_piccadilly = pnl_df[pnl_df["store_id"] != "S07"]["net_margin_pct"].mean() / 100
    cand["est_profit"]  = cand["est_rev"] * chain_margin_ex_piccadilly
    cand["payback_yrs"] = cand["est_fitout_gbp"] / cand["est_profit"].replace(0, np.nan)

    cand_ranked = cand.sort_values("Score", ascending=False)

    # Ranking Chart
    cand_colors = [COLOR_EMERALD if i < 2 else (COLOR_AMBER if i < 4 else COLOR_SLATE_500) for i in range(len(cand_ranked))]
    fig_sites = go.Figure(go.Bar(
        x=cand_ranked["Score"],
        y=cand_ranked["site_name"],
        orientation="h",
        marker_color=cand_colors,
        text=cand_ranked["Score"].map(lambda x: f" {x:.1f} / 10 "),
        textposition="outside",
        textfont=dict(color=COLOR_SLATE_900, size=11, family="Inter")
    ))
    fig_sites.update_xaxes(title_text="Composite Opportunity Index (0–10)", range=[0, 11.5])
    apply_chart_theme(fig_sites, height=360, title="Site Expansion Scoring Hierarchy (Emerald = Tier 1 Priority)")
    st.plotly_chart(fig_sites, use_container_width=True)

    # Tabular Breakdown
    disp_sites = cand_ranked[["site_name", "city", "location_type", "sqft", "quoted_rent_gbp_month", "est_fitout_gbp", "Score", "est_rev", "est_profit", "payback_yrs"]].copy()
    disp_sites["Score"]         = disp_sites["Score"].map(lambda x: f"{x:.1f} / 10")
    disp_sites["Est. Revenue"]  = disp_sites["est_rev"].map(fmt_gbp)
    disp_sites["Est. Profit"]   = disp_sites["est_profit"].map(fmt_gbp)
    disp_sites["Payback"]       = disp_sites["payback_yrs"].map(lambda x: f"{x:.1f} yrs")
    disp_sites["Rent / mo"]     = disp_sites["quoted_rent_gbp_month"].map(fmt_gbp)
    disp_sites["Fitout Capital"]= disp_sites["est_fitout_gbp"].map(fmt_gbp)

    disp_sites = disp_sites.rename(columns={
        "site_name": "Proposed Location",
        "city": "City",
        "location_type": "Format Type",
        "sqft": "Sq Ft"
    })
    st.dataframe(disp_sites[["Proposed Location", "City", "Format Type", "Sq Ft", "Rent / mo", "Fitout Capital", "Score", "Est. Revenue", "Est. Profit", "Payback"]], use_container_width=True, hide_index=True)

    # ── Head to Head: Wellington Place vs Kelham Island ───────────────────────
    st.markdown("<div style='margin-bottom: 1.25rem;'></div>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='font-size:1.2rem; font-weight:700; color:{COLOR_SLATE_900}; margin-bottom:0.75rem;'>CEO Shortlist Head-to-Head: Wellington Place vs Kelham Island</h3>", unsafe_allow_html=True)

    wp = cand[cand["site_name"] == "Leeds Wellington Place"].iloc[0]
    ki = cand[cand["site_name"] == "Sheffield Kelham Island"].iloc[0]

    h2h_data = pd.DataFrame({
        "Key Site Metric": [
            "Composite Model Score", "Office Workers (500m)", "Street Footfall / Day",
            "Median Household Income", "Competitor Cafés Nearby", "Monthly Quoted Rent",
            "Fitout Capex Budget", "Estimated Payback Time"
        ],
        "Leeds Wellington Place (Recommended)": [
            f"{wp['Score']:.1f} / 10", f"{wp['office_workers_500m']:,}", f"{wp['daily_footfall_street']:,}",
            f"£{wp['median_household_income_gbp']:,}", f"{wp['competitor_cafes_500m']}", fmt_gbp(wp['quoted_rent_gbp_month']),
            fmt_gbp(wp['est_fitout_gbp']), f"{wp['payback_yrs']:.1f} years"
        ],
        "Sheffield Kelham Island (Runner-Up)": [
            f"{ki['Score']:.1f} / 10", f"{ki['office_workers_500m']:,}", f"{ki['daily_footfall_street']:,}",
            f"£{ki['median_household_income_gbp']:,}", f"{ki['competitor_cafes_500m']}", fmt_gbp(ki['quoted_rent_gbp_month']),
            fmt_gbp(ki['est_fitout_gbp']), f"{ki['payback_yrs']:.1f} years"
        ]
    })
    st.dataframe(h2h_data, use_container_width=True, hide_index=True)

    st.markdown(
        "<div class='tw-alert tw-alert-emerald'>"
        "<b>Capital Verdict:</b> Allocate <b>£350,000 for Leeds Wellington Place</b> immediately. "
        "With 18,200 office workers (plus 2,000 arriving autumn 2026), it captures the exact office demographic "
        "driving Spinningfields' lucrative weekday trade. Reserve remaining funds (£400k) for <b>Kelham Island in 12–18 months</b>."
        "</div>",
        unsafe_allow_html=True
    )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — SENTIMENT & REVIEWS
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    reviews = get_reviews()
    events  = get_events()

    st.markdown(
        "<div class='tw-alert tw-alert-amber'>"
        "<b>Qualitative Root Causes (3,030 Customer Reviews):</b> Corroborates financial findings. "
        "The introduction of the <b>£0.40 oat milk charge</b> dropped ratings by 0.30 stars, while <b>App v3.0 release</b> "
        "caused severe checkout freezes and stamp losses (rating fell to 3.45). "
        "Lunchtime queue abandonment at Manchester Piccadilly is the #1 complaint."
        "</div>",
        unsafe_allow_html=True
    )

    STORE_MAP = {
        "piccadilly": "S07", "manc piccadilly": "S07", "manchester piccadilly": "S07", "piccadilly station": "S07",
        "briggate": "S03", "leeds briggate": "S03", "leeds - briggate": "S03", "leeds trinity": "S12",
        "division street": "S01", "division st": "S01", "sheffield division street": "S01",
        "sheffield station": "S02", "sheff station": "S02", "su kiosk": "S11", "sheffield uni": "S11",
        "nq": "S05", "northern quarter": "S05", "manchester northern quarter": "S05", "spinningfields": "S06",
        "stonegate": "S04", "york stonegate": "S04", "york": "S04", "stonegate, york": "S04",
        "harrogate": "S09", "harrogate james street": "S09", "james street": "S09",
        "nottingham": "S08", "hockley": "S08", "nottingham hockley": "S08",
        "hull": "S10", "hull paragon": "S10",
    }

    def map_store_id(raw):
        if pd.isna(raw): return None
        cl = raw.strip().lower()
        for k, v in STORE_MAP.items():
            if k in cl: return v
        return None

    reviews["store_id"] = reviews["store_name_raw"].apply(map_store_id)

    THEMES = {
        "Lunch Queues & Understaffing": ["queue", "wait", "slow", "understaffed", "need more staff", "short-staffed", "long wait"],
        "App Bugs & Stamp Losses":      ["app", "stamp", "crash", "checkout", "disappeared", "bug", "glitch", "v3"],
        "Missing Delivery Items":       ["missing", "wrong order", "forgot", "incomplete", "wasn't there"],
        "Oat Milk Surcharge":           ["oat", "oat milk", "surcharge", "charge", "price", "pricey", "expensive"],
        "Positive Feedback":            ["love", "great", "excellent", "amazing", "lovely", "best", "delicious"]
    }

    def extract_themes(txt):
        if pd.isna(txt): return []
        tl = txt.lower()
        return [t for t, kws in THEMES.items() if any(kw in tl for kw in kws)]

    reviews["themes"] = reviews["review_text"].apply(extract_themes)
    reviews["month"]  = reviews["review_date"].dt.to_period("M").dt.to_timestamp()

    rk1, rk2, rk3, rk4 = st.columns(4)
    rk1.markdown(metric_card("Total Verified Reviews", f"{len(reviews):,}", "Google/TripAdvisor/Apps", "slate"), unsafe_allow_html=True)
    rk2.markdown(metric_card("Average Chain Rating", f"{reviews['rating'].mean():.2f} / 5.0", "Benchmark: 4.0+", "amber"), unsafe_allow_html=True)
    rk3.markdown(metric_card("Negative Reviews (1–2★)", f"{(reviews['rating'] <= 2).mean()*100:.1f}%", "Mainly app & queues", "rose"), unsafe_allow_html=True)
    rk4.markdown(metric_card("Positive Reviews (4–5★)", f"{(reviews['rating'] >= 4).mean()*100:.1f}%", "Product quality strong", "emerald"), unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

    # ── Monthly Rating Trajectory ─────────────────────────────────────────────
    monthly_rev = reviews.groupby("month").agg(
        avg_rating=("rating", "mean"),
        count=("rating", "count")
    ).reset_index()

    fig_rev = make_subplots(specs=[[{"secondary_y": True}]])
    fig_rev.add_trace(go.Bar(
        x=monthly_rev["month"], y=monthly_rev["count"],
        name="Review Volume", marker_color=COLOR_SLATE_100, opacity=0.9
    ), secondary_y=True)
    fig_rev.add_trace(go.Scatter(
        x=monthly_rev["month"], y=monthly_rev["avg_rating"],
        name="Average Star Rating", line=dict(color=COLOR_EMERALD, width=3), mode="lines+markers"
    ), secondary_y=False)

    for _, ev in events.iterrows():
        if ev["date"] >= reviews["review_date"].min() and ev["date"] <= reviews["review_date"].max():
            fig_rev.add_vline(
                x=pd.to_datetime(ev["date"]).timestamp() * 1000,
                line_dash="dash", line_color=COLOR_AMBER, line_width=1.5,
                annotation_text=ev["event"],
                annotation_position="top right",
                annotation_font=dict(color=COLOR_AMBER, size=10)
            )

    fig_rev.update_yaxes(title_text="Rating (1 to 5 Stars)", range=[2.8, 4.8], secondary_y=False)
    fig_rev.update_yaxes(title_text="Monthly Volume", secondary_y=True, showgrid=False)
    apply_chart_theme(fig_rev, height=340, title="Customer Rating Trend Over Time With Key Milestone Events")
    st.plotly_chart(fig_rev, use_container_width=True)

    # ── Theme Frequency & Store Ratings ───────────────────────────────────────
    col_th, col_sr = st.columns([1, 1])

    with col_th:
        theme_tally = {t: reviews["themes"].apply(lambda ts: t in ts).sum() for t in THEMES}
        df_th = pd.DataFrame(list(theme_tally.items()), columns=["Issue Category", "Mentions"]).sort_values("Mentions")
        th_palette = [COLOR_EMERALD if "Positive" in t else COLOR_ROSE for t in df_th["Issue Category"]]

        fig_th = go.Figure(go.Bar(
            x=df_th["Mentions"], y=df_th["Issue Category"],
            orientation="h",
            marker_color=th_palette,
            text=df_th["Mentions"],
            textposition="outside",
            textfont=dict(color=COLOR_SLATE_900, size=11, family="Inter")
        ))
        fig_th.update_xaxes(title_text="Total Customer Feedback Mentions")
        apply_chart_theme(fig_th, height=330, title="Primary Feedback Themes Identified in Text")
        st.plotly_chart(fig_th, use_container_width=True)

    with col_sr:
        sr_df = reviews.dropna(subset=["store_id"]).groupby("store_id").agg(
            avg_r=("rating", "mean"), count_r=("rating", "count")
        ).reset_index().merge(stores[["store_id", "store_name"]], on="store_id").sort_values("avg_r")

        sr_palette = [COLOR_ROSE if r < 3.4 else (COLOR_AMBER if r < 3.8 else COLOR_EMERALD) for r in sr_df["avg_r"]]

        fig_sr = go.Figure(go.Bar(
            x=sr_df["avg_r"], y=sr_df["store_name"],
            orientation="h",
            marker_color=sr_palette,
            text=sr_df["avg_r"].map(lambda x: f" {x:.2f}★ "),
            textposition="outside",
            textfont=dict(color=COLOR_SLATE_900, size=11, family="Inter")
        ))
        fig_sr.update_xaxes(title_text="Average Customer Rating", range=[2.0, 4.6])
        apply_chart_theme(fig_sr, height=330, title="Store Reputation Ranking by Star Rating")
        st.plotly_chart(fig_sr, use_container_width=True)

    # ── Review Search / Explorer ──────────────────────────────────────────────
    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='font-size:1.2rem; font-weight:700; color:{COLOR_SLATE_900}; margin-bottom:0.5rem;'>Raw Review Explorer</h3>", unsafe_allow_html=True)

    f1, f2 = st.columns(2)
    with f1:
        f_theme = st.selectbox("Filter by Category Theme:", ["All Mentions"] + list(THEMES.keys()))
    with f2:
        f_stars = st.multiselect("Filter Star Ratings:", [1, 2, 3, 4, 5], default=[1, 2])

    rev_filtered = reviews.copy()
    if f_theme != "All Mentions":
        rev_filtered = rev_filtered[rev_filtered["themes"].apply(lambda ts: f_theme in ts)]
    if f_stars:
        rev_filtered = rev_filtered[rev_filtered["rating"].isin(f_stars)]

    disp_revs = rev_filtered[["review_date", "source", "store_name_raw", "rating", "review_text"]].sort_values("review_date", ascending=False).head(30)
    disp_revs.columns = ["Date", "Channel Source", "Store Mentioned", "Star Rating", "Review Text Content"]
    st.dataframe(disp_revs, use_container_width=True, hide_index=True)
