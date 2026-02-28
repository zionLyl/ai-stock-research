---
name: stock-screening
description: >
  Quantitative stock screening and filtering for US equities. Use when the user wants to
  find stocks matching specific criteria (value, growth, quality, momentum, special situations),
  rank securities by metrics, or build a watchlist from a universe. Triggers on: "screen stocks",
  "find stocks with", "filter by", "rank by", "cheap stocks", "high-growth companies",
  "dividend aristocrats", "watchlist ideas".
---

# Stock Screening

Systematic, data-driven stock screening using yfinance bulk data retrieval. Screen across
predefined strategies or custom criteria, rank results, and output an actionable watchlist.

## Data Pipeline

```
1. Define universe (S&P 500, sector, custom list)
2. Fetch bulk data via yahoo_finance.py --screen TICK1,TICK2,...
3. Apply filters (hard cutoffs)
4. Rank by composite score
5. Output top N candidates with key metrics
```

**Primary data source:** `scripts/yahoo_finance.py` with `--screen` flag for bulk retrieval.
Supplement with MCP search for qualitative signals (insider buying, activist involvement, catalysts).

## Workflow

### Step 0: Clarify Screen Parameters

Before screening, confirm with the user:

1. **Strategy type** — which preset or custom criteria?
2. **Universe** — full market, specific sector, or custom ticker list?
3. **Output size** — top 10? top 20? all passing?
4. **Ranking preference** — single metric or composite score?

If the user is vague ("find me some good stocks"), default to **Quality + Value composite** on the S&P 500.

### Step 1: Define the Universe

| Universe | Approach |
|---|---|
| S&P 500 | Use hardcoded list or fetch from Wikipedia via web search |
| Specific sector | Search for sector constituents, then screen |
| Custom list | User provides tickers directly |
| Thematic | Use MCP search to identify relevant companies, then screen |

**Practical limit:** yfinance handles ~50 tickers per batch efficiently. For larger universes,
batch in groups of 50 with 2-second delays between batches.

### Step 2: Apply Screening Strategy

#### Preset Strategies

**Value Screen**
```
Filters:
  P/E ratio < 20 (or sector median)
  P/B ratio < 3
  Dividend yield > 1.5%
  Debt/Equity < 1.5
  Free cash flow yield > 4%

Rank by: Composite of P/E percentile + FCF yield percentile + dividend yield percentile
```

**Growth Screen**
```
Filters:
  Revenue growth (YoY) > 15%
  EPS growth (YoY) > 15%
  Gross margin > 40%
  Market cap > $2B (avoid micro-caps)

Rank by: Revenue growth × EPS growth (weighted 60/40)
```

**Quality Screen**
```
Filters:
  ROE > 15%
  Gross margin > 35%
  Operating margin > 10%
  Debt/Equity < 1.0
  Positive FCF for 3+ consecutive years

Rank by: ROE × operating margin stability
```

**Dividend Screen**
```
Filters:
  Dividend yield > 2.0%
  Payout ratio < 75%
  Dividend growth (5Y CAGR) > 5%
  Consecutive dividend increases > 5 years
  Debt/Equity < 1.5

Rank by: Dividend yield × dividend growth rate
```

**Momentum Screen**
```
Filters:
  Price > 200-day MA
  Price > 50-day MA
  52-week relative strength > 70th percentile
  Volume > 500K daily average

Rank by: 6-month return minus 1-month return (classic momentum factor)
```

**GARP (Growth at a Reasonable Price)**
```
Filters:
  PEG ratio < 1.5
  Revenue growth > 10%
  P/E < 25
  ROE > 12%

Rank by: PEG ratio (ascending — lower is better)
```

#### Custom Screens

When the user provides custom criteria:

1. Map each criterion to the closest yfinance field
2. Validate that the field is available (some metrics are sparse)
3. If a metric isn't available via yfinance, check if SEC EDGAR XBRL can provide it
4. Clearly state which criteria could and could not be applied

### Step 3: Fetch and Filter

Execute the screen:

```bash
python scripts/yahoo_finance.py --screen AAPL,MSFT,GOOGL,... --json
```

**Processing logic:**
1. Parse JSON output for each ticker
2. Apply hard filters — exclude any stock that fails ANY filter criterion
3. Handle missing data: if a critical metric is unavailable for a stock, exclude it and note why
4. Calculate composite ranking score for survivors

**Missing data rules:**
- If >30% of universe is missing a metric, warn the user and suggest dropping that filter
- If a single stock is missing 1-2 non-critical metrics, include it with "N/A" noted
- Never impute or estimate missing values — screen on available data only

### Step 4: Rank and Score

For composite rankings:

1. Convert each metric to a percentile rank within the screened universe
2. Apply strategy-specific weights
3. Calculate weighted composite score (0-100 scale)
4. Sort descending by composite score

**Normalization:** For metrics where lower is better (P/E, debt), invert the percentile
(100 - percentile) before weighting.

### Step 5: Output Results

#### Watchlist Table (Primary Output)

```markdown
## Screen Results: [Strategy Name]
**Universe:** [description] | **Date:** [YYYY-MM-DD] | **Passing:** [N] of [Total]

| Rank | Ticker | Company | Sector | Score | [Key Metric 1] | [Key Metric 2] | [Key Metric 3] |
|------|--------|---------|--------|-------|-----------------|-----------------|-----------------|
| 1    | AAPL   | Apple   | Tech   | 87.3  | 28.5x P/E       | 15.2% growth    | 26.1% ROE       |
| 2    | ...    | ...     | ...    | ...   | ...             | ...             | ...             |

**Filters applied:** [list each filter and threshold]
**Data source:** yfinance, fetched [timestamp]
**Excluded (missing data):** [list any excluded tickers and why]
```

#### Per-Stock Mini Profile (for top 5)

For each of the top 5 results, include a 3-4 line summary:
- What the company does (one sentence)
- Why it scored well (which metrics stood out)
- One risk or caveat to watch

### Step 6: Follow-Up Suggestions

After presenting results, suggest logical next steps:

- "Want me to run a deeper analysis on any of these? (`/earnings TICK` or `/dcf TICK`)"
- "Should I compare the top 3 head-to-head? (`/comps TICK1 TICK2 TICK3`)"
- "Want me to save this as a watchlist for morning monitoring?"

## Sector-Specific Adjustments

Different sectors require different screening metrics:

| Sector | Additional Metrics | Adjusted Thresholds |
|---|---|---|
| Technology / SaaS | Rule of 40, NRR (if available) | Higher P/E tolerance (< 35) |
| Financials / Banks | P/TBV, NIM, efficiency ratio | Use P/TBV instead of P/B |
| REITs | FFO/share, dividend yield, NAV discount | Use FFO multiples, not P/E |
| Biotech | Pipeline stage, cash runway | Skip profitability filters |
| Utilities | Regulated ROE, payout ratio | Lower growth thresholds (> 3%) |
| Energy | EV/EBITDA, reserve life, breakeven price | Cycle-adjust earnings |

## Quality Checklist

- [ ] Universe clearly defined and documented
- [ ] All filter thresholds stated explicitly
- [ ] Data source and fetch timestamp included
- [ ] Missing data handled and documented
- [ ] Results sorted by composite score
- [ ] Top 5 have mini-profiles with risk caveats
- [ ] Sector-appropriate metrics used
- [ ] Follow-up actions suggested
- [ ] No stale data (all fetched in current session)

## Common Pitfalls

- **Survivorship bias:** Screening only currently listed stocks ignores delisted failures.
  Acknowledge this limitation in results.
- **Point-in-time data:** yfinance returns current financials, not as-reported. Note this.
- **Overfitting:** Stacking too many filters (>6) tends to produce a tiny, idiosyncratic set.
  Warn the user if the result set is <5 stocks from a broad universe.
- **Sector concentration:** If all results cluster in one sector, flag it and suggest
  diversifying filters or running sector-specific screens.

## Batch Size and Performance

| Universe Size | Approach | Expected Time |
|---|---|---|
| < 20 tickers | Single batch | ~10 seconds |
| 20-50 tickers | Single batch | ~20 seconds |
| 50-200 tickers | Batch of 50, sequential | ~1-2 minutes |
| 200+ tickers | Batch of 50, with progress updates | ~3-5 minutes |

Always inform the user of expected wait time for large screens. Provide progress updates
("Screened 100/500 tickers...") for universes >100.
