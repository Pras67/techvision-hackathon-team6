# Grind & Crumb Hackathon — Data Audit & Quality Log (`data_issues.md`)

**Date:** July 2025 – June 2026 dataset review  
**Audit Purpose:** Comprehensive validation of 21 raw datasets, reconciling against financial accounting standards, logging anomalies, impossible values, and specifying resolution methodologies.

---

## 1. Master Dataset Inventory & Schema Audit

| # | File Name | Row Count | Column Count | Primary / Foreign Keys | Date Range | Missing / Null Values | Integrity / Anomaly Notes |
|---|---|---|---|---|---|---|---|
| 1 | `stores.csv` | 12 | 11 | `store_id` (PK) | Opened: 2017-09-01 to 2025-09-15 | `refit_year`: 7 nulls | Stores S04, S06, S07, S09, S10, S11, S12 have never received a capex refit. Rent spans £4.8k to £30.5k/mo. |
| 2 | `products.csv` | 38 | 9 | `product_id` (PK) | Seasonal dates on 4 SKUs | `available_from`: 34 nulls, `available_to`: 35 nulls | Floating-point precision artifacts in `delivery_price_gbp` (e.g. £3.5500000000000003). Non-seasonal items have null dates (all-year availability). |
| 3 | `daily_store_sales.csv` | 4,292 | 8 | `date` + `store_id` (Composite PK) | 2025-07-01 to 2026-06-30 | None (0 nulls) | **Ground Truth Financial Spine**. Total chain revenue: **£8,656,692.49** (In-store: £6.23M, App: £0.99M, Delivery: £1.43M). S12 has 289 rows (opened 15 Sep 2025). |
| 4 | `transactions.csv` | 143,093 | 11 | `receipt_id` (PK), `store_id`, `customer_id` | 2025-07-01 07:00 to 2026-06-30 17:54 | `delivery_partner`: 131,914 nulls; `customer_id`: 90,678 nulls; `payment_method`: 1,728 nulls | **10% random sample**. 64 duplicate rows (128 total). 570 refund receipts with `-RF` suffix carrying negative `net_gbp`. |
| 5 | `transaction_lines.csv` | 238,624 | 9 | `receipt_id` + `line_no` (Composite PK), `product_id` | N/A (joins on `receipt_id`) | `milk_option`: 131,733 nulls (non-milk beverages & food items) | 106 duplicate lines (212 total). 1,665 negative line items, 100% belonging to `product_id == 'MEALDEAL'` bundle discounts. |
| 6 | `footfall.csv` | 12,876 | 4 | `date` + `store_id` + `daypart` (Composite PK) | 2025-07-01 to 2026-06-30 | None (0 nulls) | 3 dayparts per store-day (Morning 07-11, Lunch 11-14, Afternoon 14-18). Total door count across chain: 3,140,820 visitors. |
| 7 | `weather.csv` | 2,555 | 5 | `date` + `city` (Composite PK) | 2025-07-01 to 2026-06-30 | None (0 nulls) | Covers 7 municipal cities. Used for footfall and hot/cold drink elasticity correlation. |
| 8 | `loyalty_customers.csv` | 9,025 | 6 | `customer_id` (PK), `home_store_id` | Signup: 2021-09-01 to 2026-06-29 | `age_band`: 631 nulls (unrecorded) | 25 duplicate customer rows (50 total). `marketing_opt_in` is text/boolean. |
| 9 | `staff_rota_weekly.csv` | 1,875 | 5 | `week_start` + `store_id` + `daypart` (Composite PK) | 2025-06-30 to 2026-06-29 | None (0 nulls) | 53 calendar weeks. Total scheduled hours across chain = 168,898 hrs. Total raw labour cost = £2,574,117.20. Week 1 starts June 30; Week 53 extends into July 2026. |
| 10 | `staff_monthly.csv` | 142 | 6 | `month` + `store_id` (Composite PK) | 2025-07 to 2026-06 | None (0 nulls) | 142 store-months (12 stores x 12 months, minus 2 pre-opening months for S12). Tracks leavers, starters, survey score. |
| 11 | `waste_log.csv` | 12,876 | 6 | `date` + `store_id` + `category` (Composite PK) | 2025-07-01 to 2026-06-30 | `units_wasted`: 129 nulls | **Format anomaly**: 273 rows in October 2025 are formatted as `DD/MM/YYYY` instead of `YYYY-MM-DD`. Total waste cost = £133,815.11. |
| 12 | `store_costs_monthly.csv` | 142 | 7 | `month` + `store_id` (Composite PK) | 2025-07 to 2026-06 | None (0 nulls) | Rent: £1,423,550.00; Business Rates: £313,181.00; Utilities: £214,052.71; Repairs & Maintenance: £110,705.48; Other Opex: £111,014.77. |
| 13 | `capex.csv` | 4 | 4 | `store_id` + `month` | 2022-06 to 2025-08 | None (0 nulls) | Historical refits (S05: £125k, S01: £140k, S03: £210k) and S12 Trinity fitout (£385k). |
| 14 | `promotions.csv` | 6 | 8 | `promo_id` (PK) | 2025-09-22 to 2026-06-30 | None (0 nulls) | UTF-8 encoding corruption in promo description (`Â£7.50`). Semicolon-delimited target store list. |
| 15 | `delivery_partner_terms.csv` | 3 | 6 | `partner` + `valid_from` (Composite PK) | 2025-07-01 to 2026-04-01 | `valid_to`: 2 nulls (open-ended contracts) | Dashly increased commission from 27% to 33% on 2026-04-01. RushEats fixed at 30%. Packaging cost £0.45/order. |
| 16 | `customer_reviews.csv` | 3,030 | 6 | `review_id` (PK) | 2025-07-01 to 2026-06-30 | `review_text`: 91 nulls | `store_name_raw` is unstandardized free text (e.g. "Manc Piccadilly Station", "SU kiosk", "Stonegate, York"). |
| 17 | `customer_survey.csv` | 650 | 10 | `response_id` (PK) | 2026-05-05 to 2026-05-25 | None (0 nulls) | Post-App v3.0 survey capturing loyalty churn, app feedback, and oat milk surcharge sentiment. |
| 18 | `staff_exit_survey.csv` | 115 | 9 | `response_id` (PK), `store_id` | 2025-07 to 2026-06 | None (0 nulls) | 115 staff exits across 12 stores with verbatim feedback on rota, pay, workload, and understaffing. |
| 19 | `store_catchment.csv` | 12 | 7 | `store_id` (PK) | N/A (Census / Catchment) | None (0 nulls) | Footfall, office workers within 500m, student density, income, competitor cafés. |
| 20 | `candidate_sites.csv` | 7 | 13 | `site_id` (PK) | N/A (Candidate Sites) | None (0 nulls) | 7 candidate sites with quoted rents, fitout estimates, and demographic profiles. |
| 21 | `business_events.csv` | 5 | 3 | `date` + `event` | 2025-09-15 to 2026-04-13 | None (0 nulls) | UTF-8 encoding issue (`Â£0.40`). Key corporate events: Trinity opening, Oat milk fee, App v3.0, NLW hike, App v3.1 fix. |

---

## 2. Identified Data Anomalies & Resolution Log

### Anomaly 1: `waste_log.csv` Mixed Date Formats
- **Description**: Rows for October 2025 (273 rows) are recorded as `DD/MM/YYYY` (e.g., `01/10/2025` to `31/10/2025`), while all other 12,603 rows are formatted as `YYYY-MM-DD`. Standard ISO datetime parsing either crashes or mistakenly parses October 1st as January 10th.
- **Handling**: Implemented conditional format parser: detect rows matching `^\d{4}-\d{2}-\d{2}$` and parse ISO; for non-matching rows, parse using `dayfirst=True`. Reconciled back to exact monthly buckets.

### Anomaly 2: `transactions.csv` and `transaction_lines.csv` Duplicate Records
- **Description**: 64 exact duplicate receipts in `transactions.csv` (128 rows total) and 106 duplicate lines in `transaction_lines.csv` (212 rows total).
- **Handling**: Deduplicated using `df.drop_duplicates()`. Reaffirmed fundamental ground rule: `transactions.csv` is strictly a 10% sample used for basket, channel, and item distributions; all financial totals are drawn from `daily_store_sales.csv`.

### Anomaly 3: `loyalty_customers.csv` Duplicate Customer IDs
- **Description**: 25 customer records appear twice (50 rows total) with identical customer IDs, signup dates, and attributes.
- **Handling**: Applied deduplication on `customer_id` prior to loyalty tenure and customer cohort analysis.

### Anomaly 4: Negative Values & Refunds in Transactions
- **Description**: 570 receipts in `transactions.csv` possess negative gross and net amounts, carrying the suffix `-RF` (e.g., `R0000321-RF`). In `transaction_lines.csv`, 1,665 lines have negative line totals; all 1,665 belong to `product_id == 'MEALDEAL'`.
- **Handling**: Negative transaction lines are meal deal bundle discounts, not errors; they represent legitimate margin deductions. `-RF` records represent refunds/returns. Handled by categorizing refunds appropriately when calculating gross sales vs net sales, and ensuring basket distribution charts filter on positive purchase baskets while including net refund adjustments in cash totals.

### Anomaly 5: Missing `units_wasted` in `waste_log.csv`
- **Description**: 129 entries have null `units_wasted`, but `est_cost_wasted_gbp` is populated (e.g. £11.79, £9.83).
- **Handling**: When computing waste cost, `est_cost_wasted_gbp` is directly used (no data lost). For volume metrics, `units_wasted` is imputed by dividing `est_cost_wasted_gbp` by the average unit cost of waste for that specific store and category.

### Anomaly 6: Rota Calendar Boundaries & Labour Month Allocation
- **Description**: `staff_rota_weekly.csv` records 53 Monday-start weeks. Week 1 starts on `2025-06-30` (Monday), containing 1 day of June 2025 and 6 days of July 2025. Week 53 starts on `2026-06-29` (Monday), containing 2 days of June 2026 and 5 days of July 2026.
- **Handling**: Implemented daily prorated allocation: each weekly rota row is divided by 7 to determine daily scheduled hours, then grouped by calendar month. This prevents overstating June 2025 or distorting July 2026.

### Anomaly 7: Unstructured Store Names in Customer Reviews
- **Description**: `store_name_raw` in `customer_reviews.csv` contains informal colloquial names (e.g. `"SU kiosk"`, `"Manc Piccadilly Station"`, `"leeds - briggate"`, `"Division St"`).
- **Handling**: Built an exhaustive mapping dictionary covering all 12 store aliases, capturing 98.4% of review locations deterministically, with unmapped items logged for transparency.

### Anomaly 8: UTF-8 / Windows-1252 Garbled Currency Encodings
- **Description**: `business_events.csv` and `promotions.csv` contain `Â£0.40` and `Â£7.50` due to Windows-1252 / UTF-8 multi-byte misinterpretation.
- **Handling**: Sanitized text via `.replace('Â£', '£')` across all presentation and visualization layers.

---

## 3. Financial Reconciliation (Ground Truth)

All metrics verified against the 12-month operating dataset (1 July 2025 – 30 June 2026):
- **Total Chain Net Revenue**: **£8,656,692.49** [Measured]
  - In-Store: £6,232,705.84 (72.0%)
  - App Click & Collect: £992,623.74 (11.5%)
  - Delivery: £1,431,362.91 (16.5%)
- **Total Chain Store Costs**:
  - Labour Cost (Scheduled Hours × Wage × 1.13): **£2,574,117.20** [Measured]
  - Fixed Store Costs (Rent + Rates + Utilities + Maintenance + Other): **£2,172,503.96** [Measured]
    - Base Rent: £1,423,550.00 (16.4% of total sales)
    - Business Rates: £313,181.00
    - Utilities: £214,052.71
    - Repairs & Maintenance: £110,705.48
    - Other Store Opex: £111,014.77
  - Food & Beverage Waste: **£133,815.11** [Measured]
  - Direct Delivery Costs (Commission + Packaging + 4 min packing labour): **£579,203.14** [Measured/Assumed]
- **Store-Level Operating Profit**: **£3,196,953.08** [Measured]
- **Chain Net Margin**: **36.93%** (Store-Level, net of VAT, excluding Head Office & Tax) [Measured]
