---
name: morning-note
description: >
  Pre-market daily briefing for an individual US equity investor. Use when the user wants a
  morning summary, pre-market update, overnight developments, or daily market snapshot.
  Triggers on: "morning note", "morning briefing", "pre-market", "what happened overnight",
  "daily brief", "market update", "what should I know today".
---

# Morning Note

Generate a concise pre-market briefing designed for quick consumption (2-3 minute read).
Covers overnight market moves, key news for the user's coverage universe, today's calendar,
and actionable alerts. No filler — every sentence should be worth reading.

## Design Principles

- **Speed over depth.** The morning note is a triage tool, not an analysis report.
- **Signal over noise.** Only include items that might affect portfolio decisions today.
- **Numbers first.** Lead with data, follow with context.
- **Coverage universe first.** The user's holdings and watchlist take priority over general market.

## Workflow

### Step 1: Determine Coverage Universe

Check for existing thesis files and portfolio data:

1. Look in `memory/thesis_*.md` for active theses → these are the priority tickers
2. Check for portfolio data in `memory/portfolio.md` or most recent portfolio file
3. If no prior data exists, ask the user for their watchlist tickers
4. Default coverage: user's holdings + active thesis watchlist

### Step 2: Fetch Market Data

**Parallel data gathering — execute all simultaneously:**

#### 2a. Index Futures / Pre-Market

Fetch via yfinance:
- S&P 500 (`^GSPC`), Nasdaq 100 (`^NDX`), Dow (`^DJI`) — prior close + pre-market if available
- VIX (`^VIX`) — fear gauge
- 10-year Treasury yield (`^TNX`)
- Dollar index (`DX-Y.NYB`)
- Crude oil (`CL=F`), Gold (`GC=F`)

```bash
python scripts/yahoo_finance.py ^GSPC --json
```

#### 2b. Overnight International Markets

Fetch key international indices:
- Nikkei 225 (`^N225`)
- Hang Seng (`^HSI`)
- Shanghai Composite (`000001.SS`)
- STOXX Europe 600 (`^STOXX`)

These provide context for US open — especially if there was a major move.

#### 2c. Coverage Universe Pre-Market

For each ticker in the coverage universe:
- Previous close
- Pre-market price and change (if available)
- Any after-hours earnings reported last night

#### 2d. News Scan

Search via MCP for:
```
"US stock market today pre-market {DATE}"
"earnings reports today {DATE}"
"economic calendar {DATE}"
```

For each coverage universe ticker:
```
"{TICKER} news today"
```

Focus on:
- Earnings releases (after yesterday's close or pre-market today)
- Analyst upgrades/downgrades
- M&A announcements
- Regulatory actions
- Management changes
- Significant insider transactions

### Step 3: Assemble the Note

#### Morning Note Template

```markdown
# Morning Note — {DAY_OF_WEEK}, {MONTH} {DAY}, {YEAR}

## Market Snapshot

| Index | Prior Close | Change | Trend |
|-------|-----------|--------|-------|
| S&P 500 | {X,XXX} | {+/-X.X%} | {context} |
| Nasdaq 100 | {X,XXX} | {+/-X.X%} | {context} |
| VIX | {XX.X} | {+/-X.X} | {elevated/calm} |

| Macro | Level | Change |
|-------|-------|--------|
| 10Y Yield | {X.XX%} | {+/-Xbps} |
| USD Index | {XXX.X} | {+/-X.X%} |
| Crude Oil | ${XX.XX} | {+/-X.X%} |

**Overnight:** {1-2 sentence summary of Asia/Europe session}

## Coverage Universe Alerts

{Only include tickers with material news or moves. Skip tickers with nothing notable.}

**{TICKER}** — {Headline in bold}
{2-3 sentences: what happened, why it matters, what to watch}

**{TICKER}** — {Headline}
{2-3 sentences}

{If no coverage universe alerts: "No material overnight developments for your holdings."}

## Today's Calendar

**Earnings:**
- {TICKER} — reports {before open / after close}, consensus EPS ${X.XX}, Rev ${X.XB}
- {TICKER} — reports {timing}, consensus EPS ${X.XX}

**Economic Data:**
- {TIME ET}: {Data release} (consensus: {X}, prior: {Y})

**Fed / Central Bank:**
- {Any Fed speakers, minutes, or decisions}

**Other:**
- {Ex-dividend dates for holdings}
- {Options expiry if relevant}

## Watchpoints

1. **{Most important thing to watch today}** — {Why it matters}
2. **{Second priority}** — {Why}
3. **{Third if applicable}**

---
*Generated {TIMESTAMP}. Data: yfinance + MCP search.*
```

### Step 4: Thesis-Aware Alerts

Cross-reference news with active theses:

- If news affects a thesis pillar → flag it: "**Thesis alert:** {TICKER} {pillar} may be impacted by {news}. Consider reviewing."
- If a catalyst date has arrived → flag it: "**Catalyst today:** {TICKER} — {catalyst description}"
- If stock hits target price or stop-loss → flag it: "**Price alert:** {TICKER} at ${X.XX}, {above target / near stop-loss}"

## Timing and Context

### Best Execution Windows

| User Timezone | Ideal Generation Time | Market Context |
|---|---|---|
| US Eastern | 7:00-8:30 AM ET | Pre-market trading active |
| US Pacific | 5:00-6:00 AM PT | Before getting ready for work |
| Asia-based | Evening prior | Prepare for next day's US open |

### Day-of-Week Patterns

- **Monday:** Include weekend news roundup, Friday after-hours activity
- **Friday:** Note options expiry, weekend risk for event-driven positions
- **Earnings season (Jan/Apr/Jul/Oct):** More coverage universe earnings, heavier note
- **FOMC days:** Lead with rate decision timing and expectations
- **Quad witching:** Note derivatives expiry impact on volumes

## Customization

### Note Length by Mode

| Mode | Length | Content |
|---|---|---|
| Quick | 30 seconds read | Market snapshot + alerts only |
| Standard (default) | 2-3 minutes | Full template above |
| Extended | 5 minutes | Standard + mini-analysis for each alert |

### User Preferences

Over time, learn and adapt to:
- Which sectors the user cares about most
- Macro factors they track (rates, oil, dollar)
- Preferred level of international market detail
- Whether they want crypto/commodity context

## Quality Checklist

- [ ] All market data is from today (not stale)
- [ ] Coverage universe tickers checked for overnight news
- [ ] Earnings calendar verified for today's reporters
- [ ] Economic calendar included with consensus expectations
- [ ] Thesis-aware alerts cross-referenced
- [ ] Note is genuinely concise (no padding)
- [ ] Every item has a "why it matters" angle
- [ ] Timestamp included

## Integration with Other Skills

- **thesis-tracker:** Cross-reference news with thesis pillars and catalysts
- **earnings-analysis:** If coverage universe stock reported last night, offer deep analysis
- **portfolio-monitor:** Include portfolio P&L snapshot if holdings data available
