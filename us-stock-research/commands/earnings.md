---
description: Analyze quarterly earnings results and generate a post-earnings research report
argument-hint: "[company name or ticker] [quarter, e.g. Q4 2025]"
---

# Earnings Analysis Command

Create a structured post-earnings analysis report covering beat/miss, segment performance,
margin trends, guidance changes, and thesis impact.

## Workflow

### Step 1: Parse Input

Extract from the user's input:
- **Company name or ticker**
- **Quarter** (e.g., Q3 2025, Q2 FY25)

If not provided, ask:
- "What company's earnings would you like to analyze?"
- "Which quarter? (e.g., Q4 2025)"

### Step 2: Verify Timeliness

**CRITICAL**: Before proceeding, verify data is current:
1. Search for "[Company] latest earnings results [current year]"
2. Confirm the earnings release is within the last 3 months
3. If data is stale, inform the user and search for the most recent quarter

### Step 3: Load Earnings Analysis Skill

Use `skill: "earnings-analysis"` to generate the report:

1. **Fetch quantitative data** — yfinance (earnings, financials) + SEC EDGAR (10-Q)
2. **Fetch qualitative data** — earnings call transcript, analyst reactions via MCP search
3. **Beat/miss analysis** — revenue and EPS vs consensus, quality of beat
4. **Margin & segment analysis** — 4-8 quarter trends, segment breakdown
5. **Guidance assessment** — raised / maintained / lowered, vs consensus
6. **Generate report** — 5-8 page structured Markdown report

### Step 4: Deliver Output

Provide:
1. **Markdown report** — saved to `~/.openclaw/workspace/reports/{TICKER}_Earnings_Q{N}_{YEAR}.md`
2. **Quick summary** — beat/miss on key metrics, guidance changes, thesis impact
3. **Follow-up offer** — update thesis (`/thesis`), refresh DCF (`/dcf`), or update comps (`/comps`)

## Quality Checklist

- [ ] Earnings data is from the correct and latest quarter
- [ ] Beat/miss quantified with specific dollar and percentage figures
- [ ] Margin trends shown for 4+ quarters
- [ ] Guidance change clearly categorized
- [ ] Earnings call transcript searched and key quotes extracted
- [ ] All numbers sourced and dated
- [ ] Thesis impact stated if user has an active thesis
