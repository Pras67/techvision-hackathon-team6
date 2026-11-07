# Grind & Crumb — CEO dashboard

A React web app that shows the CEO every store's numbers, with an AI advisor powered by Gemini.

- **Overview**: orders, average order value, walk-ins, deliveries, app orders, peak hour, revenue by channel, revenue by hour or over time, and every store side by side.
- **Finance**: gross sales, discounts, wastage, expenses, net sales, COGS, gross profit and net profit, with an expense breakdown, a profit trend and a P&L table by store.
- **AI advisor**: a chat with Gemini that sees whatever store and dates are selected, plus the team's findings.
- **Filters**: pick one store or all stores, and Day / Week / Month / All time / Custom dates. Every number updates.
- **Excel exports**: Overview, Sales, Expenses, Full P&L and the AI chat.

All data is bundled in the app (no database), so it is fast and works offline except for the AI advisor.

## Run it locally

You need Node.js 18 or newer.

```bash
npm install
cp .env.example .env      # then paste your Gemini key into .env
npm run dev
```

Open http://localhost:5173. The dashboard works without a key; only the AI advisor needs it.

## Deploy to Vercel (live link for the judges)

1. Push this folder to a GitHub repo.
2. In Vercel, choose **Add New → Project** and import the repo. Vercel detects Vite automatically.
3. In **Settings → Environment Variables**, add `GEMINI_API_KEY` (and optionally `GEMINI_MODEL`).
4. Deploy. The file `api/chat.js` becomes the `/api/chat` endpoint, so the key stays on the server and never reaches the browser.

## Project layout

```
api/chat.js            Serverless function that calls Gemini (also runs inside `npm run dev`)
scripts/build_data.py  Rebuilds src/data/*.json from the raw CSVs
src/data/              meta.json, daily.json (every store × day), insights.json (findings for the AI)
src/lib/data.js        Date ranges and all the maths (totals, profit, peak hour)
src/lib/exporter.js    Excel exports (SheetJS)
src/pages/             Home (overview), Finance, Advisor
src/components/        Sidebar, date bar, stat cards, charts
```

To rebuild the data from the CSVs: `python scripts/build_data.py path/to/csv/folder` (needs pandas).

## Data notes (be ready to explain these)

| Number | Where it comes from |
|---|---|
| Orders, walk-ins, app, delivery, net sales | `daily_store_sales.csv`: full daily totals, exact |
| Revenue by hour, peak hour | Shape of the day from the 10% receipt sample, scaled to the day's real total: estimate |
| Discounts, gross sales | Discount rate per store and month from the receipt sample: estimate |
| Wastage | `waste_log.csv`, daily and exact. It is already part of COGS, so it is shown but not subtracted twice |
| COGS | Starter P&L food cost, split across days in proportion to sales |
| Expenses | Starter P&L labour, rent, rates, utilities, repairs, other costs (spread evenly over trading days) plus delivery commission and packaging (in proportion to delivery sales and orders) |
| Gross profit | Net sales − COGS |
| Net profit | Gross profit − expenses. Any full month matches the starter P&L's store profit |

Cleaning: duplicate receipts and lines dropped; the seven £35 flat whites (York, 14 Mar 2026) corrected to £3.50; Hull's day-first dates in `waste_log.csv` parsed correctly; Leeds Trinity only shows from 15 Sep 2025, when it opened.

## Phase 2 ideas

Connect the tills and rotas live (e.g. via Firebase or the POS API), add logins for store managers, and schedule a weekly AI summary email to the CEO.
