# Grind & Crumb — Assumptions, Data Limitations & Methodology (`assumptions_and_limitations.md`)

**Document Purpose:** Independent verification and reconciliation document outlining mathematical assumptions, sample-to-population conversions, boundary conditions, and identified data limitations.

---

## 1. Ground Rules & Modeling Assumptions

1. **Tax Treatment**:
   - All monetary figures (menu prices, delivery prices, costs, and net revenues) are treated as **net of Value Added Tax (VAT)**, strictly in accordance with hackathon brief specifications.
   - Standard 20% UK VAT does not need to be deducted from reported store-level receipts.

2. **Labour Cost Formulation**:
   - Formula: `Labour Cost (£) = Scheduled Rota Hours × Average Hourly Wage (£) × 1.13` [Measured/Assumed].
   - The `1.13` multiplier accounts for UK employer on-costs, specifically Employer National Insurance Contributions (13.8% above secondary threshold) and mandatory employer workplace pension contributions, less statutory employment allowance buffers.
   - Wage rate inflation following the 1 April 2026 National Living Wage (NLW) hike (+6.7%) is natively reflected in `staff_rota_weekly.csv` wage rates increasing from ~£12.00–£12.40 to ~£12.80–£13.20.

3. **Delivery Economics & Cost Structure**:
   - Platform Commissions:
     - **Dashly**: 27.0% from 1 July 2025 through 31 March 2026; 33.0% from 1 April 2026 onward [Measured from contract terms & partner emails].
     - **RushEats**: 30.0% fixed throughout the operating year [Measured].
   - Direct Delivery Packaging: **£0.45 per order** borne by Grind & Crumb [Measured].
   - Staff Packing Labour: **4 minutes of barista labour per delivery order** [Brief specification].
     - Value: `(4 / 60) × £12.50 × 1.13 = £0.9417 per delivery order` [Assumed average wage proxy].
   - Combined Fixed Delivery Overhead per Order: `£0.45 + £0.9417 = £1.3917 per order` [Measured/Assumed].
   - Delivery Break-Even Formula: `Break-Even Basket (£) = Fixed Overhead (£1.3917) / (1 - Platform Commission Rate)`.
     - At Dashly 33% commission: `£1.3917 / 0.67 = £2.08` direct delivery overhead break-even.
     - With ~30% Food COGS included: `£1.3917 / (1 - 0.33 - 0.30) = £3.76` true operating break-even ticket.

4. **Sample vs. Full Dataset Integrity**:
   - `transactions.csv` (143,093 rows) and `transaction_lines.csv` (238,624 rows) are strictly a **10% random sample** of total customer receipts.
   - **Ground Rule Adherence**:
     - Channel totals, store revenues, and monthly sales are calculated **exclusively from `daily_store_sales.csv`** (4,292 rows, £8,656,692.49 total sales) [Measured].
     - The 10% sample is utilized solely to extract distributions, ratios, and percentages (e.g., % of delivery orders under £8.00 = 29.0%, partner split RushEats 62.4% / Dashly 37.6%, oat milk adoption share = 23.8% to 31.2%).
     - Sample metrics are explicitly labeled as **[Sampled]** when cited.

5. **Exclusions**:
   - In accordance with hackathon rules, Central Head Office overheads, senior executive compensation, central IT server costs, and corporate income taxes are excluded. All store comparisons evaluate store-level contribution profit.

---

## 2. Identified Data Limitations & Reconciliations

| Dataset | Observed Limitation | Impact on Analysis | Technical Resolution |
|---|---|---|---|
| `waste_log.csv` | October 2025 rows (273 rows) formatted as `DD/MM/YYYY` instead of `YYYY-MM-DD`. | Naive ISO datetime parsing crashes or maps October dates into January. | Applied conditional format parsing: ISO regex check with `dayfirst=True` fallback for anomalous rows. |
| `waste_log.csv` | 129 entries have null `units_wasted`. | Distorts physical food waste counts if unhandled. | `est_cost_wasted_gbp` is fully populated. Imputed missing units using store-category unit waste cost. Cost metrics rely on verified £ figures. |
| `transactions.csv` | 570 records feature `-RF` suffix and negative values. | Represents customer refunds and product returns. | Maintained refund records in net sales totals to reflect true accounting cash flow; excluded negative artifacts from basket size distribution curves. |
| `transaction_lines.csv` | 1,665 lines have negative totals, all associated with `product_id == 'MEALDEAL'`. | Represents bundled meal deal promotional discounts. | Validated as intentional promotional mechanics; properly accounted for as promotional margin reductions rather than inventory errors. |
| `staff_rota_weekly.csv` | 53 calendar weeks. Week 1 starts 2025-06-30 (1 day in June 2025); Week 53 extends into July 2026. | Assigning weekly rota by week start date distorts monthly boundary labour allocations. | Implemented daily pro-rated allocation (dividing weekly scheduled hours by 7 and mapping to exact calendar dates). |
| `customer_reviews.csv` | Free-text unstructured store names (`store_name_raw`). | Prevents direct relational SQL joins against `stores.csv`. | Constructed robust alias dictionary mapping 98.4% of review strings deterministically to official `store_id` keys. |
| `stores.csv` | S12 Leeds Trinity opened on 15 September 2025 (9.5 months of operation). | Simple 12-month aggregations make Trinity appear smaller than established standard stores. | Annualized Trinity metrics or evaluated on average monthly run-rate post-launch (£49.9k/mo revenue). |

---

## 3. Data Classification Key

Every figure presented in the Grind & Crumb report and pitch deck adheres to the following verification taxonomy:
- **[Measured]**: Sourced directly from full operating files (`daily_store_sales.csv`, `store_costs_monthly.csv`, `footfall.csv`, `weather.csv`, `stores.csv`). Zero estimation error.
- **[Sampled]**: Derived from the 10% receipt sample (`transactions.csv`, `transaction_lines.csv`, `loyalty_customers.csv`). Margin of error < ±0.5% at 95% confidence interval across 143,000+ records.
- **[Assumed]**: Derived from external benchmarks, business rules (e.g. 1.13 on-cost multiplier, 4-minute packing time, £1,200 barista turnover replacement cost, £1.50 average waste unit cost), or management interview context.
