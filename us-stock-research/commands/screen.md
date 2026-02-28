---
description: Screen stocks by quantitative criteria (value, growth, quality, momentum, dividend, GARP)
argument-hint: "[strategy or custom criteria, e.g. 'value', 'growth P/E<25 ROE>15%']"
---

# Stock Screening Command

Find stocks matching specific quantitative criteria and rank them by composite score.

## Workflow

### Step 1: Parse Input

Extract from the user's input:
- **Strategy name** — value, growth, quality, momentum, dividend, GARP, or custom
- **Custom filters** — any specific metric thresholds (e.g., "P/E < 20", "revenue growth > 15%")
- **Universe** — S&P 500 (default), specific sector, or custom ticker list

If not provided, ask:
- "What type of screen? (value / growth / quality / momentum / dividend / GARP / custom)"
- "Which universe? (S&P 500 default, or specify a sector or ticker list)"

### Step 2: Load Stock Screening Skill

Use `skill: "stock-screening"` to execute the screen:

1. **Define universe** — resolve ticker list for the chosen universe
2. **Fetch bulk data** — `python scripts/yahoo_finance.py --screen TICK1,TICK2,... --json`
3. **Apply filters** — hard cutoffs per strategy preset or custom criteria
4. **Rank results** — composite percentile score
5. **Generate output** — ranked watchlist table with top 5 mini-profiles

### Step 3: Deliver Output

Provide:
1. **Ranked watchlist table** — top 10-20 passing stocks with key metrics
2. **Mini-profiles** — 3-4 line summary for top 5 results
3. **Follow-up suggestions** — offer `/earnings`, `/dcf`, or `/comps` on top picks

## Quality Checklist

- [ ] Universe and filters clearly stated in output
- [ ] Data fetched live via yfinance (not from memory)
- [ ] Missing data documented (which tickers excluded and why)
- [ ] Results ranked by composite score
- [ ] Top 5 have mini-profiles with risk caveats
- [ ] Data source and timestamp included
