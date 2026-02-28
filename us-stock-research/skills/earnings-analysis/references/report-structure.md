# Earnings Analysis Report Structure

Template for the standard (5-8 page) earnings analysis report.

---

## Report Template

```markdown
# {COMPANY_NAME} ({TICKER}) — Q{N} FY{YEAR} Earnings Analysis

**Date:** {ANALYSIS_DATE}
**Earnings Date:** {EARNINGS_DATE}
**Report Type:** Post-Earnings Analysis

---

## Headline

{One sentence summary — lead with the most important fact}

## Key Takeaways

1. **{Takeaway 1}** — {Supporting data point}
2. **{Takeaway 2}** — {Supporting data point}
3. **{Takeaway 3}** — {Supporting data point}

## Beat / Miss Summary

| Metric | Actual | Estimate | Surprise | Surprise % |
|--------|--------|----------|----------|------------|
| EPS (GAAP) | ${X.XX} | ${X.XX} | ${X.XX} | +X.X% |
| EPS (Non-GAAP) | ${X.XX} | ${X.XX} | ${X.XX} | +X.X% |
| Revenue | ${X.XB} | ${X.XB} | ${X.XM} | +X.X% |

**Quality of Beat:** {Revenue-driven / Margin-driven / One-time items / Mixed}

## Financial Summary

### Income Statement Trends (Last 4 Quarters)

| Metric | Q{N-3} | Q{N-2} | Q{N-1} | Q{N} | QoQ Δ | YoY Δ |
|--------|--------|--------|--------|------|-------|-------|
| Revenue ($M) | | | | | | |
| Gross Profit ($M) | | | | | | |
| Operating Income ($M) | | | | | | |
| Net Income ($M) | | | | | | |
| EPS (Diluted) | | | | | | |

### Margin Trends

| Metric | Q{N-3} | Q{N-2} | Q{N-1} | Q{N} | Trend |
|--------|--------|--------|--------|------|-------|
| Gross Margin | | | | | ↑/↓/→ |
| Operating Margin | | | | | ↑/↓/→ |
| Net Margin | | | | | ↑/↓/→ |
| EBITDA Margin | | | | | ↑/↓/→ |

## Segment Breakdown

{If company reports segments — table with revenue, growth, and margin per segment}

| Segment | Revenue ($M) | YoY Growth | % of Total | Margin (if disclosed) |
|---------|-------------|------------|------------|----------------------|
| | | | | |

**Key segment observations:** {Which segments drove the quarter?}

## Guidance Update

| Metric | Prior Guidance | New Guidance | Consensus | vs Consensus |
|--------|---------------|-------------|-----------|-------------|
| Revenue | {range} | {range} | ${X.XB} | Above/Below/In-line |
| EPS | {range} | {range} | ${X.XX} | Above/Below/In-line |

**Guidance Assessment:** {Raised / Maintained / Lowered}
**Interpretation:** {What does this signal about management's confidence?}

## Balance Sheet Snapshot

| Metric | Current Q | Prior Q | Change |
|--------|----------|---------|--------|
| Cash & Equivalents ($M) | | | |
| Total Debt ($M) | | | |
| Net Debt ($M) | | | |
| Inventory ($M) | | | |
| Shares Outstanding (M) | | | |

## Cash Flow Highlights

| Metric | Current Q | YoY |
|--------|----------|-----|
| Operating Cash Flow ($M) | | |
| Capital Expenditures ($M) | | |
| Free Cash Flow ($M) | | |
| FCF Margin | | |

## Management Commentary Highlights

{Key quotes from earnings call — 3-5 most important statements}

> "{Quote 1}" — {Speaker, Title}

> "{Quote 2}" — {Speaker, Title}

**Management Tone:** {Confident / Cautious / Defensive / Mixed}
**Key themes:** {List 2-3 themes from the call}

## Price Reaction

| Timeframe | Price | Change |
|-----------|-------|--------|
| Pre-earnings close | ${X.XX} | — |
| After-hours (earnings) | ${X.XX} | {+/-X.X%} |
| Next day close | ${X.XX} | {+/-X.X%} |

**Market interpretation:** {Why did the stock react this way?}

## Investment Implications

### For Current Holders
{What should you do? Hold, add, trim?}

### For Potential Buyers
{Does this quarter make the stock more or less attractive?}

### Thesis Impact
{If there's an active thesis — how do these results affect each thesis pillar?}

## Risks & Watchpoints

- {Risk 1 — new or updated from this quarter}
- {Risk 2}
- {Watchpoint for next quarter}

## Data Sources

- yfinance: {metrics fetched, timestamp}
- SEC EDGAR: {filing referenced, URL}
- Earnings call transcript: {source, URL}
- Analyst estimates: {source}

---
*Analysis generated {DATE}. All data verified as of {TIMESTAMP}.*
```

## Quick Take Template (1-2 Pages)

For casual inquiries, use an abbreviated version:

```markdown
# {TICKER} Q{N} Quick Take

**{Beat/Miss}** — EPS ${X.XX} vs est ${X.XX} (+X.X%), Revenue ${X.XB} vs est ${X.XB} (+X.X%)

**Three things that matter:**
1. {Most important observation}
2. {Second most important}
3. {Third}

**Guidance:** {Raised/Maintained/Lowered} — {one sentence on new guidance vs consensus}

**Stock reaction:** {+/-X.X%} after hours — {one sentence on why}

**Bottom line:** {One sentence investment implication}

*Source: yfinance + MCP search, {DATE}*
```
