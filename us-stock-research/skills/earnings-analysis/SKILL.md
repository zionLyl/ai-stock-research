---
name: earnings-analysis
description: >
  Post-earnings quarterly analysis for US-listed companies. Use when the user asks to analyze
  a company's earnings results, review quarterly performance, assess guidance changes, or
  understand earnings beats/misses. Triggers on: "analyze earnings", "how did X do this quarter",
  "earnings report", "quarterly results", "beat or miss", "guidance update", "earnings call".
---

# Earnings Analysis

Generate a comprehensive post-earnings analysis report combining quantitative data from yfinance
and SEC filings with qualitative insights from earnings call transcripts and analyst commentary.
Output a structured Markdown report following the template in `references/report-structure.md`.

## Workflow Overview

See `references/workflow.md` for the detailed step-by-step process. Summary:

```
1. Identify → Which company, which quarter
2. Fetch quantitative → yfinance + SEC EDGAR
3. Fetch qualitative → Earnings call transcript + news
4. Analyze → Beat/miss, trends, segments, guidance
5. Synthesize → Investment implications + thesis impact
6. Output → Structured Markdown report
```

## Data Requirements

### Quantitative Data (yfinance + SEC EDGAR)

| Data Point | Primary Source | Fallback |
|---|---|---|
| EPS (actual vs estimate) | yfinance `.earnings` | MCP search |
| Revenue (actual vs estimate) | yfinance `.earnings` | MCP search |
| Income statement (quarterly) | yfinance `.quarterly_income_stmt` | SEC 10-Q |
| Balance sheet | yfinance `.quarterly_balance_sheet` | SEC 10-Q |
| Cash flow statement | yfinance `.quarterly_cashflow` | SEC 10-Q |
| Historical earnings (4-8 quarters) | yfinance `.earnings_history` | SEC filings |
| Analyst estimates (next Q) | yfinance `.analyst_price_targets` | MCP search |
| Price reaction | yfinance `.history(period='5d')` | — |

### Qualitative Data (MCP Search + Web Fetch)

| Data Point | Source Strategy |
|---|---|
| Earnings call transcript | MCP search: "[TICKER] Q[N] [YEAR] earnings call transcript" |
| Management guidance quotes | Extract from transcript |
| Analyst reactions | MCP search: "[TICKER] earnings analyst reaction [DATE]" |
| Segment detail | SEC 10-Q or earnings call transcript |
| Key risks discussed | Transcript + 10-Q risk factors |

**CRITICAL:** Always search for the earnings call transcript. It contains the most valuable
qualitative data — management tone, forward guidance specifics, competitive positioning comments.
If a full transcript isn't available, search for earnings call summaries.

## Analysis Framework

### 1. Beat/Miss Assessment

```
EPS Beat/Miss:
  Actual EPS - Consensus Estimate = Surprise ($)
  (Actual - Estimate) / |Estimate| × 100 = Surprise (%)

Revenue Beat/Miss:
  Same calculation as EPS

Quality of Beat:
  - Revenue-driven (organic growth) → High quality
  - Margin-driven (cost cutting) → Medium quality
  - Tax/one-time items → Low quality
  - Share buyback-driven EPS beat → Note separately
```

### 2. Margin Trend Analysis

Track 4-8 quarters of:
- Gross margin
- Operating margin (EBIT margin)
- Net margin
- EBITDA margin

Flag:
- Margin expansion/contraction trends (≥50bp change QoQ is notable)
- Divergence between gross and operating margins (signals SG&A discipline or lack thereof)
- One-time items distorting margins (restructuring, impairment, legal)

### 3. Segment Analysis

If the company reports segments:
- Revenue and growth rate per segment
- Contribution to total revenue (%)
- Margin by segment (if disclosed)
- Which segments drove the beat/miss

### 4. Guidance Assessment

```
Guidance Change Categories:
  Raised    → New midpoint > prior midpoint
  Maintained → No change (or trivially small)
  Lowered   → New midpoint < prior midpoint
  Initiated → First time guiding for this period
  Withdrawn → Guidance removed (usually bearish signal)

Context:
  - Compare new guidance range vs consensus
  - "Beat and raise" = strongest positive signal
  - "Beat and lower" = concerning (unsustainable performance)
  - "Miss and raise" = possible one-time issue
  - "Miss and lower" = most bearish combination
```

### 5. Balance Sheet Health Check

Quick check on:
- Cash + short-term investments vs prior quarter
- Total debt and net debt position
- Inventory changes (for hardware/manufacturing)
- Accounts receivable DSO trends
- Share count changes (buybacks)

### 6. Cash Flow Quality

- Operating cash flow vs net income ratio (should be >1.0 on average)
- Free cash flow trend
- CapEx intensity (CapEx / Revenue)
- Cash conversion cycle changes

### 7. Forward-Looking Signals

Extract from earnings call:
- Management tone (confident, cautious, defensive)
- New product launches or pipeline updates
- Competitive dynamics mentions
- Macro sensitivity commentary
- Capital allocation priorities (buybacks, dividends, M&A, CapEx)

## Report Output

Generate a structured Markdown report following `references/report-structure.md`.

**File naming:** `{TICKER}_Earnings_Q{N}_{YEAR}.md`
**Location:** `~/.openclaw/workspace/reports/`

### Report Length Guidelines

| Depth | Length | When to Use |
|---|---|---|
| Quick Take | 1-2 pages | User asks "how did X do?" casually |
| Standard | 5-8 pages | Default for `/earnings TICK` command |
| Deep Dive | 10-15 pages | User explicitly requests deep analysis |

Default to **Standard** unless otherwise specified.

## Earnings Season Patterns

When analyzing during earnings season (Jan-Feb, Apr-May, Jul-Aug, Oct-Nov):

- **Pre-earnings:** Focus on expectations, whisper numbers, key metrics to watch
- **Day-of:** Quick take on numbers + initial price reaction
- **Post-earnings (1-3 days):** Full standard analysis with analyst reactions
- **Post-earnings (1+ week):** Include estimate revision trends

## Company-Specific Considerations

### Mega-Cap Tech (AAPL, MSFT, GOOGL, AMZN, META, NVDA)
- Segment reporting is critical (cloud, advertising, devices, etc.)
- CapEx and AI investment commentary gets outsized market attention
- Guide on specific segments, not just top-line
- Check for currency impact (large international revenue)

### Financials (Banks, Insurance)
- Net interest income and NIM trends
- Provision for credit losses (signals economic outlook)
- Trading revenue (volatile, less predictable)
- Book value and tangible book value per share

### Healthcare / Biotech
- Pipeline updates (FDA approvals, trial results)
- Patent cliff exposure
- Revenue by drug/product
- R&D spending as % of revenue

### Retail / Consumer
- Same-store sales (comparable sales growth)
- E-commerce penetration
- Inventory levels vs sales growth (inventory build = risk)
- Consumer sentiment indicators

## Quality Checklist

- [ ] Correct quarter and fiscal year identified (fiscal ≠ calendar for many companies)
- [ ] EPS and revenue beat/miss calculated and verified from 2 sources
- [ ] Margin trends shown for 4+ quarters
- [ ] Guidance change clearly categorized (raised/maintained/lowered)
- [ ] Earnings call transcript searched and key quotes extracted
- [ ] Price reaction noted (earnings day and +1 day)
- [ ] Balance sheet quick check completed
- [ ] All numbers sourced and dated
- [ ] Thesis impact clearly stated (if user has an active thesis)
- [ ] "So what?" conclusion with actionable implication

## Integration with Other Skills

- **thesis-tracker:** After earnings analysis, offer to update the investment thesis
- **dcf-valuation:** Earnings results may warrant DCF assumption updates
- **comps-analysis:** Changed guidance affects forward multiples — offer to refresh comps
- **portfolio-monitor:** If the stock is in the portfolio, note P&L impact
