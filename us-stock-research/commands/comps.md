---
description: Run comparable company analysis to assess relative valuation against peers
argument-hint: "[company name or ticker] [optional: peer tickers]"
---

# Comparable Company Analysis Command

Build a peer comparison covering operating metrics, valuation multiples, and implied
valuation range from peer median multiples.

## Workflow

### Step 1: Parse Input

Extract from the user's input:
- **Target company** (ticker)
- **Specific peers** (if provided, e.g., "comp AAPL vs MSFT GOOGL META")
- **Depth** — quick comp table (default) or comprehensive analysis

If not provided, ask:
- "What company would you like to compare against peers?"

### Step 2: Load Comps Analysis Skill

Use `skill: "comps-analysis"` to build the analysis:

1. **Select peer group** — 5-12 companies based on business model, revenue scale, growth profile
   - Use yfinance peers, SEC filings competitors section, and MCP search
   - User-specified peers override auto-selection
2. **Fetch peer data** — `python scripts/yahoo_finance.py {PEERS} --json` for each
3. **Build comp table** — operating metrics + valuation multiples for all peers
4. **Add industry-specific metrics** — SaaS Rule of 40, bank P/TBV, REIT P/FFO, etc.
5. **Calculate benchmarks** — median, 25th/75th percentile, target's percentile rank
6. **Derive implied valuation** — peer median multiples × target metrics = implied price
7. **Assess premium/discount** — explain why target trades above or below peers
8. **Generate outputs** — Excel comps table + Markdown summary

### Step 3: Deliver Output

Provide:
1. **Excel comps table** — saved to `~/.openclaw/workspace/reports/{TICKER}_Comps_{DATE}.xlsx`
2. **Markdown summary** — peer group, valuation summary, implied range, key observations
3. **Verdict** — cheap, fair, or expensive relative to peers, and why

## Quality Checklist

- [ ] Peer group has 5+ companies with genuine business model similarity
- [ ] Peer selection rationale documented
- [ ] TTM metrics used for consistency
- [ ] Outliers flagged with explanations (not removed)
- [ ] Statistical benchmarks calculated (median, 25th, 75th)
- [ ] Implied valuation range from multiple methods
- [ ] Industry-specific metrics included
- [ ] Premium/discount justified with specific reasons
