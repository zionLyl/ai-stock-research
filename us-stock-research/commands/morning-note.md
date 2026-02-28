---
description: Generate a pre-market daily briefing with market data, portfolio alerts, and today's calendar
argument-hint: ""
---

# Morning Note Command

Generate a concise pre-market briefing for quick consumption (2-3 minute read). Covers
overnight moves, coverage universe alerts, today's calendar, and thesis-aware watchpoints.

## Workflow

### Step 1: Determine Coverage Universe

1. Load holdings from `memory/portfolio.md` (if exists)
2. Load active theses from `memory/thesis_*.md` files
3. Combine into coverage universe: holdings + thesis watchlist tickers
4. If no prior data exists, ask: "What tickers should I cover in your morning note?"

### Step 2: Fetch Data in Parallel

Use `skill: "morning-note"` to generate the briefing:

1. **Market snapshot** — S&P 500, Nasdaq, VIX, 10Y yield, USD, oil, gold via yfinance
2. **International markets** — Nikkei, Hang Seng, Shanghai, Europe via yfinance
3. **Coverage universe** — current/pre-market prices for all tracked tickers
4. **News scan** — MCP search for market news, earnings today, economic calendar
5. **Per-ticker news** — MCP search for overnight news on each coverage ticker

### Step 3: Assemble Note

Generate structured morning note:
- **Market snapshot table** — indices, macro, overnight international
- **Coverage universe alerts** — only tickers with material news or moves (skip quiet ones)
- **Today's calendar** — earnings reporters, economic data releases, Fed speakers
- **Watchpoints** — top 2-3 things to pay attention to today

### Step 4: Thesis Cross-Reference

- Flag news that affects active thesis pillars
- Note any catalyst dates that have arrived
- Alert on price targets or stop-losses that are close

### Step 5: Deliver Output

Provide:
1. **Morning note** — structured Markdown, designed for 2-3 minute read
2. **No filler** — every item should be actionable or informative

## Quality Checklist

- [ ] All market data fetched live (today's date)
- [ ] Coverage universe tickers checked for overnight news
- [ ] Earnings and economic calendar verified for today
- [ ] Thesis-aware alerts cross-referenced
- [ ] Note is concise — no padding or generic commentary
- [ ] Timestamp included
