# Comps Analysis — Industry Metric Schemas

Detailed metric definitions for industry-specific comparable company analysis.

---

## Universal Metrics (All Industries)

### Operating Metrics

| Metric | Formula | Source |
|---|---|---|
| Revenue (TTM) | Sum of last 4 quarters | yfinance quarterly income stmt |
| Revenue Growth (YoY) | (Rev_TTM - Rev_prior_TTM) / Rev_prior_TTM | yfinance |
| Gross Margin | Gross Profit / Revenue | yfinance |
| EBITDA Margin | EBITDA / Revenue | yfinance |
| Operating Margin | Operating Income / Revenue | yfinance |
| Net Margin | Net Income / Revenue | yfinance |
| ROE | Net Income / Avg Shareholders' Equity | yfinance |
| ROIC | NOPAT / Invested Capital | Calculated |

### Valuation Multiples

| Multiple | Formula | Notes |
|---|---|---|
| P/E (Trailing) | Price / TTM EPS | Exclude negative earnings |
| P/E (Forward) | Price / Forward EPS Estimate | yfinance `.info['forwardPE']` |
| EV/Revenue | Enterprise Value / TTM Revenue | Works for unprofitable companies |
| EV/EBITDA | Enterprise Value / TTM EBITDA | Most common comp multiple |
| P/FCF | Price / FCF per Share | FCF = Operating CF - CapEx |
| PEG | P/E / EPS Growth Rate | Only meaningful if growth > 0 |
| EV/Gross Profit | EV / Gross Profit | Useful for SaaS, marketplaces |

### Balance Sheet

| Metric | Formula | Notes |
|---|---|---|
| Net Debt / EBITDA | (Total Debt - Cash) / EBITDA | Leverage indicator |
| Debt / Equity | Total Debt / Total Equity | Capital structure |
| Current Ratio | Current Assets / Current Liabilities | Liquidity |

---

## Technology / SaaS

```
Key Metrics:
  Rule of 40 = Revenue Growth (%) + EBITDA Margin (%)
    Score > 40 = strong
    Score > 60 = exceptional

  EV / ARR = Enterprise Value / Annual Recurring Revenue
    (Use Revenue as proxy if ARR not disclosed)

  Gross Margin:
    > 75% = best-in-class SaaS
    60-75% = acceptable
    < 60% = hardware/services mixed in

  Net Revenue Retention (NRR):
    > 130% = exceptional (strong expansion)
    110-130% = healthy
    < 100% = net churn (red flag)
    Note: Rarely available via yfinance — search earnings transcripts

  R&D as % of Revenue:
    Context: higher is not always better — depends on stage

  SBC as % of Revenue:
    Stock-based compensation intensity
    > 20% is dilutive concern
```

### SaaS Comp Table Columns

```
| Company | Ticker | MCap | EV | Rev | Growth | GM | EBITDA M | R40 | EV/Rev | EV/GP | P/E |
```

---

## E-Commerce / Marketplace

```
Key Metrics:
  GMV Growth = (GMV_t - GMV_t-1) / GMV_t-1
    (Gross Merchandise Value — total transaction volume)

  Take Rate = Revenue / GMV
    Higher take rate = more monetization per transaction

  Customer Metrics (if available from filings):
    Active buyers/sellers
    Revenue per active user
    Orders per customer

  Unit Economics:
    CAC = Sales & Marketing / New Customers Added
    LTV/CAC ratio > 3x is healthy
```

---

## Semiconductors

```
Key Metrics:
  Gross Margin:
    Cyclical indicator — peak margins often signal cycle top
    Fabless: 50-70%
    IDM: 40-60%

  R&D Intensity = R&D / Revenue
    > 20% typical for leading-edge companies

  Inventory Days = (Inventory / COGS) × 365
    Rising inventory days can signal demand weakness

  Revenue per Wafer (or per chip):
    Mix indicator — higher ASPs signal premium products

  Book-to-Bill Ratio:
    > 1.0 = orders exceeding shipments (positive)
    < 1.0 = shipments exceeding orders (demand weakening)
    (Usually from industry data, not company filings)
```

---

## Banks / Financials

```
Key Metrics:
  P/TBV = Price / Tangible Book Value per Share
    Primary valuation metric for banks
    > 1.5x = premium franchise
    < 1.0x = market doubts asset quality

  Net Interest Margin (NIM) = Net Interest Income / Avg Earning Assets
    2.5-3.5% typical for US banks
    Highly sensitive to rate environment

  Efficiency Ratio = Non-Interest Expense / (Net Interest Income + Non-Interest Income)
    < 55% = well-managed
    > 65% = needs improvement

  Return on Assets (ROA):
    > 1.0% = strong
    > 1.3% = exceptional

  CET1 Ratio = Common Equity Tier 1 / Risk-Weighted Assets
    Regulatory minimum ~4.5% + buffer
    > 10% = well-capitalized

  Net Charge-Off Rate = Net Charge-Offs / Avg Loans
    Rising NCOs = deteriorating credit quality

  Loan-to-Deposit Ratio:
    < 100% = funded by deposits (stable)
    > 100% = reliant on wholesale funding (riskier)

Note: Do NOT use P/E as primary valuation for banks. Use P/TBV and ROE.
```

---

## REITs

```
Key Metrics:
  FFO = Net Income + D&A - Gains on Property Sales
    Funds From Operations — primary REIT earnings metric

  AFFO = FFO - Maintenance CapEx - Straight-line Rent Adjustments
    More conservative than FFO

  P/FFO = Price / FFO per Share
    REIT equivalent of P/E

  P/AFFO = Price / AFFO per Share
    More conservative valuation

  Dividend Yield:
    REITs must distribute 90%+ of taxable income
    Yield context matters by REIT type

  NAV Premium/Discount:
    NAV = Estimated property value - liabilities
    Trading above NAV = premium (market likes the platform)
    Trading below NAV = discount (potential value or red flag)

  Occupancy Rate:
    > 95% = strong demand
    < 90% = potential concern

  Same-Property NOI Growth:
    Organic growth indicator

Note: Do NOT use P/E for REITs. Use P/FFO, P/AFFO, and dividend yield.
```

---

## Biotech / Pharma

```
Key Metrics:
  EV / Revenue:
    Primary multiple for profitable pharma
    Less meaningful for pre-revenue biotech

  R&D as % of Revenue:
    Pharma: 15-25%
    Biotech: Can exceed 100% (pre-revenue)

  Pipeline Value:
    Qualitative assessment based on:
    - Number of drugs in Phase 1/2/3
    - Addressable market for each candidate
    - Probability of approval by phase

  Patent Cliff Exposure:
    Revenue at risk from upcoming patent expirations
    Timeline of key patent expiries (next 5 years)

  Cash Runway (pre-revenue biotech):
    Cash / Quarterly Cash Burn = Quarters of runway
    < 4 quarters = potential dilution risk
```

---

## Retail

```
Key Metrics:
  Same-Store Sales (SSS) Growth:
    Organic growth excluding new store openings
    > 3% = strong
    Negative = concerning

  Inventory Turnover = COGS / Average Inventory
    Higher is generally better (fresh inventory)
    Compare within sub-sector (grocery vs apparel)

  Revenue per Square Foot:
    Store productivity metric
    Useful for brick-and-mortar retailers

  E-commerce Penetration:
    Online sales as % of total revenue
    Trend matters more than absolute level

  Gross Margin by Channel:
    Online vs in-store margin differential
```

---

## Energy (Oil & Gas)

```
Key Metrics:
  EV/EBITDA:
    Primary valuation metric — normalize for commodity prices

  Production Growth:
    Oil: barrels per day (bpd)
    Gas: million cubic feet per day (mcf/d)
    Combined: barrels of oil equivalent per day (boe/d)

  Finding & Development Cost (F&D):
    Cost to find and develop one barrel of reserves

  Reserve Replacement Ratio:
    Proved reserves added / production depleted
    > 100% = replacing more than producing

  Breakeven Price:
    Oil price needed to cover all-in costs
    Lower = more resilient to price downturns

  Free Cash Flow Yield:
    Important for capital discipline assessment
```

---

## Industrials / Manufacturing

```
Key Metrics:
  Book-to-Bill Ratio:
    New orders / revenue
    > 1.0 = growing backlog

  Backlog:
    Total unfulfilled orders
    Months of backlog = Backlog / Monthly Revenue

  ROIC:
    Particularly important for capital-intensive businesses

  Asset Turnover = Revenue / Total Assets:
    Efficiency of asset utilization

  CapEx / Revenue:
    Capital intensity indicator
    Higher = more maintenance required

  Working Capital Efficiency:
    Cash conversion cycle trends
```
