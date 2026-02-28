---
description: Build a discounted cash flow valuation model and estimate intrinsic value
argument-hint: "[company name or ticker]"
---

# DCF Valuation Command

Build a complete DCF model with WACC calculation, 5-year projections, terminal value,
sensitivity analysis, and scenario-based fair value estimate.

## Workflow

### Step 1: Parse Input

Extract from the user's input:
- **Company name or ticker**
- **Depth** — quick estimate (default) or full model with Excel output

If not provided, ask:
- "What company would you like to value?"

### Step 2: Validate Applicability

**CRITICAL**: DCF is not appropriate for all companies.
- Banks/financials → suggest dividend discount model
- REITs → suggest NAV or FFO-based valuation
- Pre-revenue biotech → suggest pipeline/milestone valuation
- Deeply distressed → suggest liquidation analysis

If DCF is inappropriate, inform the user and suggest the right approach.

### Step 3: Load DCF Valuation Skill

Use `skill: "dcf-valuation"` to build the model:

1. **Fetch historical data** — 3-5 years via yfinance + SEC EDGAR
2. **Calculate WACC** — risk-free rate, beta, equity risk premium, cost of debt
3. **Project revenue & FCF** — 5-year projections with margin assumptions
4. **Terminal value** — Gordon Growth + exit multiple cross-check
5. **EV-to-equity bridge** — add cash, subtract debt, divide by diluted shares
6. **Sensitivity analysis** — WACC vs terminal growth, WACC vs exit multiple
7. **Scenario analysis** — bull/base/bear with probability weights
8. **Generate outputs** — Excel model + Markdown valuation summary

### Step 4: Deliver Output

Provide:
1. **Excel model** — saved to `~/.openclaw/workspace/reports/{TICKER}_DCF_{DATE}.xlsx`
2. **Markdown summary** — implied fair value, upside/downside, key assumptions, risk factors
3. **Valuation verdict** — clear statement: undervalued / fairly valued / overvalued vs current price

## Quality Checklist

- [ ] DCF applicability validated
- [ ] WACC uses current risk-free rate (fetched live)
- [ ] WACC falls within 6-18% range
- [ ] Terminal value is 50-75% of enterprise value
- [ ] Two terminal value methods cross-checked
- [ ] Diluted share count used
- [ ] Sensitivity and scenario tables included
- [ ] All assumptions documented and sourced
