---
name: portfolio-monitor
description: >
  Portfolio monitoring, P&L tracking, and alert generation for US equity holdings. Use when the
  user wants to check portfolio performance, calculate returns, review sector exposure, set
  price alerts, or get a portfolio health summary. Triggers on: "check my portfolio",
  "how are my holdings", "portfolio P&L", "position sizing", "sector exposure",
  "portfolio summary", "what's my return", "alert me if", "portfolio risk".
---

# Portfolio Monitor

Track holdings, calculate P&L, monitor alert thresholds, analyze sector exposure, and generate
portfolio performance summaries. All data fetched live via yfinance. Portfolio state persists
in `memory/portfolio.md` for cross-session tracking.

## Design Principles

- **Live data only.** Every price and metric is fetched in real-time — never use stale cached values.
- **Simple and transparent.** No black-box risk models. Show the math.
- **Alert-driven.** Don't overwhelm with data — surface only what needs attention.
- **Integration-first.** Portfolio context enriches every other skill (earnings, thesis, morning note).

## Portfolio Data Model

Portfolio state is stored in `memory/portfolio.md`:

```markdown
# Portfolio

**Last Updated:** {DATE}
**Cash Balance:** ${X,XXX} (if tracked)

## Holdings

| Ticker | Shares | Avg Cost | Date Added | Notes |
|--------|--------|----------|------------|-------|
| AAPL   | 50     | $175.20  | 2024-06-15 | Core holding |
| NVDA   | 30     | $450.00  | 2024-09-01 | AI thesis |
| MSFT   | 40     | $380.50  | 2024-03-10 | Cloud + AI |

## Alert Thresholds

| Type | Threshold | Notes |
|------|-----------|-------|
| Single stock daily move | ±5% | Any holding |
| Portfolio daily move | ±3% | Total portfolio value |
| Position concentration | >15% | Any single position |
| Sector concentration | >40% | Any single sector |

## Closed Positions

| Ticker | Shares | Avg Cost | Sell Price | Sell Date | Return |
|--------|--------|----------|-----------|-----------|--------|
```

## Workflow

### Step 0: Load or Initialize Portfolio

1. Check for existing portfolio in `memory/portfolio.md`
2. If exists, load holdings and alert thresholds
3. If not, ask the user:
   - "What stocks do you currently hold? (ticker, shares, average cost)"
   - "Would you like to set custom alert thresholds? (defaults: ±5% stock, ±3% portfolio)"
4. Save to `memory/portfolio.md`

### Step 1: Fetch Live Data

For all holdings, fetch current data:

```bash
python scripts/yahoo_finance.py {TICK1},{TICK2},... --screen --json
```

Collect per holding:
- Current price, previous close
- Day change ($ and %)
- 52-week high/low
- Market cap, sector, industry
- Beta (for risk context)
- Forward P/E (for valuation context)

### Step 2: Calculate P&L

#### Per-Position P&L

```
For each holding:
  Market Value = Shares × Current Price
  Cost Basis = Shares × Average Cost
  Unrealized P&L ($) = Market Value - Cost Basis
  Unrealized P&L (%) = (Current Price - Avg Cost) / Avg Cost × 100
  Day P&L ($) = Shares × (Current Price - Previous Close)
  Day P&L (%) = (Current Price - Previous Close) / Previous Close × 100
```

#### Portfolio-Level P&L

```
Total Market Value = Σ(Market Value per position)
Total Cost Basis = Σ(Cost Basis per position)
Total Unrealized P&L ($) = Total Market Value - Total Cost Basis
Total Unrealized P&L (%) = (Total Market Value - Total Cost Basis) / Total Cost Basis × 100
Day P&L ($) = Σ(Day P&L per position)
Day P&L (%) = Day P&L ($) / (Total Market Value - Day P&L ($)) × 100
```

### Step 3: Position & Sector Analysis

#### Position Sizing

| Ticker | Market Value | Weight (%) | Status |
|--------|-------------|-----------|--------|
| AAPL   | $X,XXX      | XX.X%     | Normal / Overweight / Alert |

**Concentration alerts:**
- Position >15% of portfolio → flag as concentrated
- Position >25% of portfolio → strong warning
- Top 3 positions >60% of portfolio → diversification concern

#### Sector Exposure

Map each holding to its GICS sector (from yfinance `.info['sector']`):

| Sector | # Holdings | Market Value | Weight (%) | Status |
|--------|-----------|-------------|-----------|--------|
| Technology | 3 | $XX,XXX | XX.X% | Normal / Alert |
| Healthcare | 1 | $X,XXX | XX.X% | Normal |

**Sector concentration alerts:**
- Single sector >40% → flag as sector-concentrated
- Single sector >50% → strong warning
- Zero exposure to defensive sectors (utilities, staples, healthcare) → note as aggressive

#### Risk Metrics

Simple, transparent risk indicators:

```
Portfolio Beta (weighted):
  β_portfolio = Σ(weight_i × β_i)
  > 1.2 = aggressive (amplifies market moves)
  0.8-1.2 = market-like
  < 0.8 = defensive

Largest Single-Day Risk (approximate):
  Worst case ≈ Σ(position_value × stock_beta × -3%)
  (Assumes a ~3% market down day, not a tail event)

Dividend Income (annual estimate):
  Σ(shares × annual dividend per share)
```

### Step 4: Check Alert Thresholds

Run through all configured alerts:

#### Stock-Level Alerts (default: ±5% daily move)

```
For each holding:
  If |day_change_%| > threshold:
    ALERT: {TICKER} moved {+/-X.X%} today ({$price})
    Context: {brief reason if available from news search}
```

#### Portfolio-Level Alerts (default: ±3% daily move)

```
If |portfolio_day_change_%| > threshold:
  ALERT: Portfolio moved {+/-X.X%} today ({+/-$X,XXX})
  Top contributors: {list top 3 contributors to the move}
```

#### Concentration Alerts

```
If any position weight > 15%:
  ALERT: {TICKER} is {XX.X%} of portfolio (threshold: 15%)
If any sector weight > 40%:
  ALERT: {SECTOR} is {XX.X%} of portfolio (threshold: 40%)
```

#### Valuation Alerts

```
If a holding's forward P/E exceeds 2× its sector median:
  NOTE: {TICKER} forward P/E of {X.Xx} is elevated vs sector median {X.Xx}

If a holding trades within 5% of 52-week high:
  NOTE: {TICKER} at ${X.XX}, within {X.X%} of 52-week high (${X.XX})

If a holding trades within 10% of 52-week low:
  NOTE: {TICKER} at ${X.XX}, within {X.X%} of 52-week low (${X.XX})
```

### Step 5: Generate Output

#### Portfolio Summary (Primary Output)

```markdown
# Portfolio Summary — {DATE}

**Total Value:** ${XX,XXX} | **Day P&L:** {+/-$X,XXX} ({+/-X.X%}) | **Total P&L:** {+/-$X,XXX} ({+/-X.X%})

## Holdings

| Ticker | Shares | Avg Cost | Current | Day Chg | Total P&L ($) | Total P&L (%) | Weight |
|--------|--------|----------|---------|---------|---------------|---------------|--------|
| AAPL   | 50     | $175.20  | $XXX.XX | +X.X%   | +$X,XXX       | +XX.X%        | XX.X%  |
| NVDA   | 30     | $450.00  | $XXX.XX | -X.X%   | +$X,XXX       | +XX.X%        | XX.X%  |
| **Total** | | | **$XX,XXX** | **+X.X%** | **+$X,XXX** | **+XX.X%** | **100%** |

## Alerts

{List any triggered alerts — or "No alerts triggered."}

## Sector Exposure

| Sector | Weight | Holdings |
|--------|--------|----------|
| Technology | XX.X% | AAPL, NVDA, MSFT |

## Portfolio Stats

| Metric | Value |
|--------|-------|
| Portfolio Beta | X.XX |
| # Positions | X |
| Largest Position | TICKER (XX.X%) |
| Est. Annual Dividends | $X,XXX |
```

#### Quick Check (Short Form)

When the user asks casually ("how's my portfolio doing?"):

```
Portfolio: $XX,XXX (+X.X% today, +XX.X% total)
Winners: NVDA +X.X%, AAPL +X.X%
Losers: MSFT -X.X%
Alerts: {any alerts or "none"}
```

### Managing Holdings

#### Adding a Position

When the user buys a stock:
1. Add to `memory/portfolio.md` holdings table
2. If already held, recalculate average cost:
   ```
   New Avg Cost = (Old Shares × Old Avg + New Shares × Buy Price) / (Old Shares + New Shares)
   ```
3. Update total share count

#### Closing a Position

When the user sells:
1. Calculate realized P&L
2. Move to Closed Positions table in `memory/portfolio.md`
3. Remove from active holdings (or reduce shares for partial sell)

#### Partial Sells

When the user sells part of a position:
1. Reduce share count (average cost stays the same)
2. Log the partial sale in Closed Positions with the sold shares and sell price

### Custom Alert Configuration

Users can customize alert thresholds:

```
"Set NVDA alert to ±3%"        → Stock-specific override
"Alert me if portfolio drops 5%" → Portfolio threshold change
"Alert if AAPL hits $200"       → Price target alert
"Alert if any position >20%"    → Concentration threshold change
```

Save all custom thresholds to `memory/portfolio.md` Alert Thresholds section.

## Periodic Review Triggers

Suggest portfolio review when:
- Any holding hasn't had its thesis updated in >90 days
- Portfolio concentration has drifted significantly from initial allocation
- A holding has doubled or halved since purchase
- 3+ months since last full portfolio review

## Quality Checklist

- [ ] All prices fetched live (not from memory/training data)
- [ ] P&L calculations verified (cost basis × shares matches)
- [ ] Day change calculated from previous close (not stale reference)
- [ ] Sector mapping from yfinance (not assumed)
- [ ] Alert thresholds checked against current data
- [ ] Portfolio beta calculated with current betas
- [ ] Concentration analysis includes both position and sector level
- [ ] Holdings table in `memory/portfolio.md` is up to date
- [ ] Closed positions logged with realized P&L

## Integration with Other Skills

- **morning-note:** Portfolio snapshot included in daily briefing
- **earnings-analysis:** Flag when a held stock reports earnings, note P&L impact
- **thesis-tracker:** Cross-reference holdings with active theses — flag unthesized positions
- **dcf-valuation:** DCF result → compare implied value to cost basis and current price
- **comps-analysis:** Relative valuation context for held positions
- **stock-screening:** Screen results flagged if already held (avoid doubling up)
