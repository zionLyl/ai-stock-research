---
name: dcf-valuation
description: >
  Discounted cash flow valuation model builder for US equities. Use when the user wants to
  value a stock using DCF, estimate intrinsic value, build a financial model, or assess
  upside/downside scenarios. Triggers on: "value this stock", "DCF", "intrinsic value",
  "what is X worth", "build a model", "fair value estimate", "WACC", "terminal value".
---

# DCF Valuation

Build a complete discounted cash flow model with WACC calculation, 5-year revenue and earnings
projections, terminal value (Gordon Growth + exit multiple cross-check), and sensitivity analysis.
Output both an Excel model via `scripts/excel_builder.py` and a Markdown valuation summary.

## Prerequisites

Before building a DCF, gather:
1. **3+ years of historical financials** — via yfinance (income statement, balance sheet, cash flow)
2. **Current market data** — share price, market cap, shares outstanding, beta
3. **Analyst consensus estimates** — revenue and EPS for next 1-2 years (if available)
4. **Comparable company data** — for terminal multiple cross-check (run comps first if time allows)

## Workflow

### Step 0: Validate DCF Applicability

DCF works best for companies with:
- Positive or near-positive free cash flow
- Relatively predictable revenue streams
- Established business models

**DCF is NOT appropriate for:**
- Pre-revenue biotech/startups → use pipeline valuation or milestone analysis
- Banks/financials → use dividend discount model or excess return model
- REITs → use NAV or FFO-based valuation
- Commodity producers → use NAV based on reserve value
- Deeply distressed companies → use liquidation analysis

If the target fails this check, inform the user and suggest an alternative approach.

### Step 1: Fetch Historical Data

```bash
python scripts/yahoo_finance.py {TICKER} --financials --json
python scripts/sec_edgar.py {TICKER} --form 10-K --json
```

Build a historical table (3-5 years):
- Revenue, COGS, gross profit
- Operating expenses (SG&A, R&D)
- EBIT, EBITDA
- D&A, CapEx
- Changes in working capital
- Tax rate (effective)
- Share count

### Step 2: Calculate WACC

See `references/formulas.md` for complete formulas.

**Inputs needed:**

| Input | Source | Notes |
|---|---|---|
| Risk-free rate | 10-year US Treasury yield | Fetch via MCP search |
| Equity risk premium | 5.0-6.0% (standard range) | Use 5.5% as default |
| Beta | yfinance `.info['beta']` | If unavailable, use industry median |
| Cost of debt | Interest expense / avg total debt | From income statement + balance sheet |
| Tax rate | Effective tax rate from financials | Use normalized rate, not one-time adjusted |
| Debt/Equity ratio | From balance sheet (market values preferred) | Market cap for equity, book for debt |

**WACC assembly:**

```
Cost of Equity = Risk-Free Rate + Beta × Equity Risk Premium
After-tax Cost of Debt = Cost of Debt × (1 - Tax Rate)
WACC = (E/V) × Cost of Equity + (D/V) × After-tax Cost of Debt
```

**Typical WACC ranges (sanity check):**
- Large-cap stable: 7-9%
- Mid-cap growth: 9-12%
- Small-cap / high-beta: 12-16%
- If WACC falls outside 6-18%, double-check inputs

### Step 3: Build Revenue Projections

**Approach priority:**
1. Start with analyst consensus for Year 1-2 (if available from yfinance)
2. Apply user-specified growth rate, or
3. Use historical CAGR with gradual deceleration

**Revenue projection framework:**

```
Year 1-2: Analyst consensus or recent growth trajectory
Year 3-4: Gradual convergence toward industry growth rate
Year 5: Near terminal growth rate (but still above)
```

**Growth rate guardrails:**
- If projected growth exceeds 2× historical CAGR, flag as aggressive
- If projected growth implies market share >50%, flag as unrealistic
- Revenue deceleration is the norm — accelerating revenue needs strong justification

### Step 4: Project Free Cash Flow

Build out the full FCF projection:

```
Revenue
  - COGS (apply gross margin assumption)
= Gross Profit
  - SG&A (as % of revenue)
  - R&D (as % of revenue)
= EBIT
  - Taxes (EBIT × tax rate)
= NOPAT (Net Operating Profit After Tax)
  + D&A
  - CapEx
  - Change in Working Capital
= Unlevered Free Cash Flow (UFCF)
```

**Margin assumptions:**
- Start from current margins
- Project gradual expansion or contraction based on:
  - Historical trend
  - Management guidance
  - Competitive dynamics
  - Operating leverage potential

### Step 5: Calculate Terminal Value

Use **two methods** and cross-check:

**Method 1: Gordon Growth Model**
```
Terminal Value = FCF_Year5 × (1 + g) / (WACC - g)

Where g = terminal growth rate (typically 2-3%, aligned with nominal GDP)
```

**Method 2: Exit Multiple**
```
Terminal Value = EBITDA_Year5 × Exit EV/EBITDA Multiple

Exit multiple sourced from:
  - Current trading multiple of mature peers
  - Historical median for the sector
  - Comps analysis if available
```

**Terminal value should be 50-75% of total enterprise value.** If it exceeds 80%, the model is
too dependent on terminal assumptions — flag this to the user.

### Step 6: Discount and Bridge to Equity Value

```
Enterprise Value = Σ(UFCF_t / (1 + WACC)^t) + Terminal Value / (1 + WACC)^5

Equity Value Bridge:
  Enterprise Value
  + Cash & equivalents
  - Total debt
  - Minority interest
  - Preferred equity
  + Equity investments (if material)
  = Equity Value

Implied Share Price = Equity Value / Diluted Shares Outstanding
```

**Diluted share count:** Use treasury stock method. Include options/RSUs from 10-K note
disclosures or proxy statement.

### Step 7: Sensitivity Analysis

Build three sensitivity tables:

1. **WACC vs Terminal Growth Rate** — the standard DCF sensitivity
2. **WACC vs Exit Multiple** — for the exit multiple method
3. **Revenue Growth vs Operating Margin** — tests the operating assumptions

Each table should show the implied share price in each cell, with the base case highlighted.

### Step 8: Scenario Analysis

Build three scenarios:

| Scenario | Revenue Growth | Margin Trend | WACC | Terminal Growth | Probability |
|---|---|---|---|---|---|
| Bull | +2-3% above base | Expansion | Base - 0.5% | 3.0% | 25% |
| Base | Analyst consensus / trend | Stable | Calculated | 2.5% | 50% |
| Bear | -2-3% below base | Compression | Base + 1.0% | 2.0% | 25% |

**Probability-weighted fair value:**
```
Fair Value = (Bull Price × 25%) + (Base Price × 50%) + (Bear Price × 25%)
```

### Step 9: Generate Outputs

#### Excel Model

```bash
python scripts/excel_builder.py {TICKER} dcf
```

Populate the template with:
- Assumptions sheet (all inputs, clearly marked as editable)
- Historical + projected income statement
- Free cash flow build
- DCF valuation with EV-to-equity bridge
- Sensitivity tables

**File:** `~/.openclaw/workspace/reports/{TICKER}_DCF_{DATE}.xlsx`

#### Markdown Summary

```markdown
# {TICKER} DCF Valuation Summary

**Date:** {DATE} | **Current Price:** ${X.XX} | **Implied Fair Value:** ${X.XX}
**Upside/Downside:** {+/-X.X%}

## Valuation Range

| Scenario | Implied Value | vs Current | Probability |
|----------|--------------|------------|-------------|
| Bull     | ${X.XX}      | +X.X%      | 25%         |
| Base     | ${X.XX}      | +/-X.X%    | 50%         |
| Bear     | ${X.XX}      | -X.X%      | 25%         |
| **Weighted** | **${X.XX}** | **+/-X.X%** | — |

## Key Assumptions
{Table of critical inputs: WACC, terminal growth, revenue CAGR, terminal margin}

## What Drives the Valuation
{2-3 sentences on what matters most — typically revenue growth and terminal value}

## Key Risks to the Model
{2-3 specific model risks, not generic disclaimers}
```

## Quality Checklist

- [ ] DCF applicability validated (not a bank, pre-revenue startup, or REIT)
- [ ] Historical data sourced from yfinance + verified against SEC filing
- [ ] WACC calculated with current risk-free rate (not stale)
- [ ] WACC falls within reasonable range (6-18%)
- [ ] Revenue projections have clear rationale (not just "15% growth")
- [ ] Margin assumptions grounded in historical trend + management guidance
- [ ] Terminal value is 50-75% of enterprise value (not >80%)
- [ ] Two terminal value methods used and cross-checked
- [ ] EV-to-equity bridge includes all components (cash, debt, minorities)
- [ ] Diluted share count used (not basic)
- [ ] Sensitivity tables built for key variables
- [ ] Three scenarios with probability weights
- [ ] Excel model generated and saved
- [ ] All assumptions clearly documented and editable

## Common Mistakes

- **Using trailing data for forward projections** — always project from the most recent quarter
- **Forgetting working capital** — changes in WC are real cash flows
- **Double-counting** — D&A in both EBITDA and FCF build
- **Stale risk-free rate** — always fetch current 10-year Treasury yield
- **Circular reference** — equity value depends on WACC depends on E/V depends on equity value.
  Break the circularity by using current market weights for initial WACC, then iterate once.
- **Ignoring stock-based compensation** — SBC is a real cost. Include it in operating expenses.
