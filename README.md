# Grind & Crumb · Operations Intelligence Platform & Board Strategy

This repository contains the complete hackathon submission for the **Code & Consult Hackathon: Grind & Crumb Café Chain**.

It delivers:
1. **The Live Operational Intelligence Tool** (Interactive Streamlit + Plotly decision support application).
2. **The Executive Board Report** (`executive_report.md` — 2 pages summary + 2 pages appendix).
3. **The 5-Minute Pitch Script & Judge Q&A Guide** (`pitch_script.md` — with 10 evidence-backed Q&A responses).
4. **Data Audit & Anomaly Resolution Log** (`data_issues.md` — all 21 raw datasets analyzed and reconciled).
5. **Methodology & Assumptions Guide** (`assumptions_and_limitations.md`).

---

## 🚀 One-Command Quickstart (How to Run the Tool)

### Prerequisites
Python 3.10+ with standard data science packages:
```bash
pip install streamlit pandas plotly openpyxl
```

### Launch the App
Open PowerShell or your terminal in this repository folder and run:
```powershell
$env:PATH += ";C:\Users\prasa\AppData\Roaming\Python\Python314\Scripts"
cd "app"
streamlit run app.py
```
Or directly:
```bash
streamlit run app/app.py
```

The application will launch and open automatically in your browser at:  
👉 **`http://localhost:8501`**

---

## 📊 App Feature Overview

The platform is designed for Grind & Crumb's executive and operations team to use continuously after the hackathon:

| Tab | Feature & Core Capability | Strategic Decision Enabled |
|---|---|---|
| **1. Store P&L & Margins** | Monthly store-by-store P&L breakdown, revenue vs net margin, cost stack (rent, labour, waste, rates, repairs), milestone events. | Exposes that **Manchester Piccadilly (S07)** is the lowest margin store (19.9%) due to £30.5k/mo rent, while **York Stonegate (S04)** leads the chain at 46.8% margin. |
| **2. Delivery Margin Simulator** | Interactive slider model for platform commissions, packaging fees, barista wages, and customer upgrade rates. Basket histogram showing Dashly vs RushEats. | Simulates the financial impact of enforcing an **£8.00 minimum basket**, unlocking **£54,000/yr net profit** with zero capital spend. |
| **3. Piccadilly & Capacity Planner** | Footfall vs scheduled labour hour ratios by daypart (Morning, Lunch, Afternoon). Interactive lost transaction recovery calculator. | Diagnoses Piccadilly's 27 visitors/labour hour lunch bottleneck, proving that **2 additional baristas** yield **+£53,200/yr net profit** and reduce 230% staff turnover. |
| **4. Waste & Par Rebalancer** | Waste rate ranking across all 12 stores, category breakdowns, dynamic par level calibration tool. | Eliminates **£24,200/yr in food waste and maintenance drag** at Hull Paragon (20.6% waste) and Leeds Briggate. |
| **5. Expansion Scorer** | Demographic opportunity model across all 7 candidate sites with customizable weights (footfall, office density, students, income, competition). | Empirically ranks **Leeds Wellington Place (CS7)** as the #1 priority (18,200 office workers), but cautions against premature cannibalisation. |
| **6. £1.5M Capital Allocation** | Fully costed 7-line investment portfolio summing to **exactly £1,500,000.00** with conservative, base, and optimistic scenarios. | Recommends £440k in operational turnarounds, £380k in phased Wellington Place expansion, and £775k in strategic reserves. |
| **7. Sentiment & Root Causes** | Interactive keyword search across 3,030 customer reviews and 650 loyalty surveys, mapped against milestone event timelines. | Verifies the impact of App v3.0 bugs, the £0.40 oat milk charge, and lunchtime queue complaints with verbatim customer quotes. |

---

## 📑 Core Documentation Map

- [`executive_report.md`](executive_report.md) — 2-page board report answering the CEO's question, testing management claims, presenting the £1.5M allocation, and detailing appendices.
- [`pitch_script.md`](pitch_script.md) — Word-for-word 5-minute presentation script structured for high marks, including timing cues and 10 anticipated judge questions.
- [`data_issues.md`](data_issues.md) — Complete log of the 8 real data issues discovered in raw files (including October 2025 mixed dates, duplicates, refund codes, and calendar boundaries).
- [`assumptions_and_limitations.md`](assumptions_and_limitations.md) — Technical explanation of VAT treatment, labour formulas, delivery overheads, and sample-to-population conversions.

---

## 💡 Key Summary Figures (Ground Truth)

- **Total Chain Revenue**: **£8,656,692.49** [Measured]
- **Store-Level Operating Profit**: **£3,196,953.08** (36.93% margin) [Measured]
- **Total Chain Labour Cost**: **£2,574,117.20** (29.7% of sales) [Measured]
- **Total Base Rent**: **£1,423,550.00** (16.4% of sales) [Measured]
- **Total Delivery Costs**: **£579,203.14** (Commission + packaging + packing labour) [Measured/Assumed]
- **Total Food Waste**: **£133,815.11** (89,699 units) [Measured]
- **Recommended Capital Plan**: **£1,500,000.00** deployed across 7 prioritized initiatives [Measured]
- **Net Annual Steady-State Benefit**: **+£404,000 / year** [Assumed/Modelled]
- **Blended Payback Period**: **2.3 Years** [Modelled]
