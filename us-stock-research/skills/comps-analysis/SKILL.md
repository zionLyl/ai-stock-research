---
name: comps-analysis
description: >
  Comparable company analysis for US equities. Use when the user wants to compare a stock
  against peers, assess relative valuation, find trading multiples, or benchmark operating
  metrics. Triggers on: "comp", "comps", "comparable", "peers", "relative valuation",
  "how does X trade vs peers", "peer group", "multiples comparison", "valuation benchmarking".
---

# Comparable Company Analysis

Build a rigorous peer comparison covering operating metrics, valuation multiples, and
statistical benchmarks. Output both an Excel comps table via `scripts/excel_builder.py`
and a Markdown summary with key findings.

## Philosophy

Comps analysis answers: "Is this stock cheap or expensive relative to similar companies?"
The quality depends entirely on **peer group selection** and **metric normalization**.
A bad peer group produces misleading conclusions — invest the time to get this right.

## Workflow

### Step 0: Identify the Target and Context

Confirm with the user:
- **Target company** (ticker)
- **Purpose** — general valuation context, M&A valuation, or screening filter?
- **Depth** — quick comp table (5-7 peers) or comprehensive analysis (10-15 peers)?
- **Pre-existing peer group?** — does the user have specific companies in mind?

### Step 1: Select the Peer Group

**Selection criteria (in priority order):**

1. **Business model similarity** — same core business (not just same GICS sector)
2. **Revenue scale** — within 0.3x-3x of target revenue (flexible for thin industries)
3. **Growth profile** — similar growth rates (high-growth vs mature matters more than sector)
4. **Geographic mix** — primarily US revenue or similar international exposure
5. **End market overlap** — serving the same customers

**Peer sourcing methods:**

| Method | How |
|---|---|
| yfinance peers | `yahoo_finance.py {TICKER} --json` → extract peer tickers from `.info` |
| Sector search | MCP search: "{COMPANY} competitors" or "{INDUSTRY} publicly traded companies" |
| SEC filings | 10-K often names competitors in "Competition" section |
| User input | User specifies companies directly |

**Target peer group size:**
- Quick analysis: 5-7 peers
- Standard analysis: 8-12 peers
- Comprehensive: 12-20 peers (only if the industry is large enough)

**Peer exclusion rules:**
- Remove companies with market cap <$500M (illiquid, less reliable data)
- Remove companies with fundamentally different business models despite same sector
- Remove recent IPOs (<2 years) unless specifically relevant
- Note any excluded companies and why

### Step 2: Fetch Peer Data

For each peer in the group:

```bash
python scripts/yahoo_finance.py {PEER_TICKER} --json
```

Collect for every company:

**Identification:**
- Company name, ticker, market cap, enterprise value
- Sector, industry, brief description

**Operating metrics:**
- Revenue (TTM and last fiscal year)
- Revenue growth (YoY)
- Gross margin, operating margin, EBITDA margin, net margin
- ROE, ROA, ROIC
- Revenue per employee (if meaningful)

**Valuation multiples:**
- P/E (trailing and forward)
- EV/Revenue
- EV/EBITDA
- P/FCF (Price to Free Cash Flow)
- PEG ratio

**Balance sheet:**
- Net debt / EBITDA
- Current ratio
- Debt / equity

### Step 3: Industry-Specific Metrics

Layer in metrics relevant to the industry. See `references/schemas.md` for detailed schemas.

| Industry | Additional Metrics |
|---|---|
| SaaS / Cloud | EV/ARR, Rule of 40, NRR (if available), gross margin |
| E-commerce / Marketplace | GMV growth, take rate, customer acquisition cost |
| Semiconductors | Inventory days, gross margin (cyclical indicator), R&D intensity |
| Banks / Financials | P/TBV, NIM, efficiency ratio, CET1 ratio, ROA |
| REITs | P/FFO, P/AFFO, dividend yield, NAV premium/discount |
| Biotech / Pharma | EV/pipeline value, R&D as % revenue, patent cliff timeline |
| Retail | Same-store sales, inventory turnover, revenue per sqft |
| Industrials | Book-to-bill ratio, backlog, order growth |

### Step 4: Normalize and Clean Data

**Calendarization:** If peers have different fiscal year-ends, normalize to same calendar period.
Use TTM (trailing twelve months) as the standard.

**Outlier handling:**
- Calculate median and interquartile range (IQR) for each metric
- Flag values >1.5× IQR from the median as outliers
- Do NOT remove outliers — flag them and note the reason (turnaround, distressed, hyper-growth)
- If a company has negative earnings, exclude from P/E calculation but include in EV/Revenue

**Missing data:**
- Mark as "N/A" — never estimate or impute
- If >30% of peers are missing a metric, drop that metric from the analysis

### Step 5: Calculate Statistical Benchmarks

For each metric, compute:

| Statistic | Purpose |
|---|---|
| Mean | General reference (sensitive to outliers) |
| Median | Primary benchmark (robust to outliers) |
| 25th percentile | "Cheap" boundary for valuation multiples |
| 75th percentile | "Expensive" boundary for valuation multiples |
| Min / Max | Range endpoints |

**The target company's percentile rank** for each metric tells the valuation story.

### Step 6: Derive Implied Valuation

Using peer median multiples, calculate implied value for the target:

```
Implied EV (from EV/EBITDA) = Target EBITDA × Peer Median EV/EBITDA
Implied EV (from EV/Revenue) = Target Revenue × Peer Median EV/Revenue
Implied Price (from P/E) = Target EPS × Peer Median P/E

Equity Value = Implied EV + Cash - Debt
Implied Share Price = Equity Value / Diluted Shares
```

Build a valuation range using 25th/median/75th percentile multiples:

| Method | 25th Pctl | Median | 75th Pctl |
|---|---|---|---|
| EV/EBITDA | ${low} | ${mid} | ${high} |
| EV/Revenue | ${low} | ${mid} | ${high} |
| P/E | ${low} | ${mid} | ${high} |

### Step 7: Assess Premium/Discount Justification

If the target trades at a premium or discount to peers, explain **why:**

**Justifiable premiums:**
- Higher growth rate
- Better margins (operating leverage)
- Stronger competitive moat
- Superior management track record
- Better balance sheet

**Justifiable discounts:**
- Slower growth
- Margin pressure
- Execution risk
- Regulatory overhang
- Concentrated revenue (customer/product)

### Step 8: Generate Outputs

#### Excel Comps Table

```bash
python scripts/excel_builder.py {TICKER} comps
```

Populate with all peer data. The Excel template includes:
- **Operating Metrics sheet** — revenue, growth, margins, returns for all peers
- **Valuation Multiples sheet** — all multiples with statistical summaries
- **Notes sheet** — data sources, dates, methodology notes

**File:** `~/.openclaw/workspace/reports/{TICKER}_Comps_{DATE}.xlsx`

#### Markdown Summary

```markdown
# {TICKER} Comparable Company Analysis

**Date:** {DATE} | **Peer Group:** {N} companies | **Industry:** {Industry}

## Peer Group

| Company | Ticker | Market Cap | Revenue | Growth | EBITDA Margin |
|---------|--------|-----------|---------|--------|---------------|

## Valuation Summary

| Multiple | Target | Peer Median | Percentile | Premium/Discount |
|----------|--------|-------------|------------|-----------------|
| EV/EBITDA | X.Xx | X.Xx | Xth | +/-X% |
| EV/Revenue | X.Xx | X.Xx | Xth | +/-X% |
| P/E | X.Xx | X.Xx | Xth | +/-X% |

## Implied Valuation Range

| Method | Low (25th) | Mid (Median) | High (75th) |
|--------|-----------|-------------|-------------|

**Weighted implied value:** ${X.XX} ({+/-X.X%} vs current)

## Key Observations
1. {Most important relative valuation insight}
2. {Operating metric standout — positive or negative}
3. {Premium/discount justification assessment}
```

## Quality Checklist

- [ ] Peer group has 5+ companies with genuine business model similarity
- [ ] Peer group selection rationale documented
- [ ] All data sourced from yfinance with timestamps
- [ ] TTM metrics used for consistent comparison
- [ ] Outliers flagged (not removed) with explanations
- [ ] Statistical benchmarks calculated (median, 25th, 75th)
- [ ] Implied valuation range derived from multiple methods
- [ ] Premium/discount vs peers explained with specific reasons
- [ ] Industry-specific metrics included
- [ ] Excel file generated and saved
- [ ] Missing data marked as N/A (never estimated)

## Integration with Other Skills

- **dcf-valuation:** Comps-derived exit multiples feed into DCF terminal value
- **earnings-analysis:** Post-earnings comps refresh shows re-rating potential
- **stock-screening:** Comps benchmarks inform screening thresholds
- **thesis-tracker:** Relative valuation is a key thesis pillar
