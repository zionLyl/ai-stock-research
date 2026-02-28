# DCF Valuation — Formula Reference

Complete formula reference for building a discounted cash flow model.

---

## WACC (Weighted Average Cost of Capital)

### Cost of Equity — CAPM

```
Ke = Rf + β × ERP

Where:
  Ke   = Cost of equity
  Rf   = Risk-free rate (10-year US Treasury yield)
  β    = Levered beta (from yfinance or regression)
  ERP  = Equity risk premium (default: 5.5%)
```

### Small-Cap Adjustment (Optional)

```
Ke_adjusted = Ke + Size Premium

Size Premium by Market Cap:
  > $10B:   0.0%
  $2B-$10B: 1.0-1.5%
  $500M-$2B: 2.0-3.0%
  < $500M:  3.0-5.0%
```

### Beta Estimation (When yfinance Beta Unavailable)

```
Unlevered Beta = Levered Beta / (1 + (1 - Tax Rate) × D/E)
Relevered Beta = Unlevered Beta × (1 + (1 - Tax Rate) × Target D/E)

Alternative: Use industry median unlevered beta and relever
```

### Cost of Debt

```
Kd = Interest Expense / Average Total Debt
After-tax Kd = Kd × (1 - Tax Rate)

Sanity check against:
  - Company's bond yields (if publicly traded debt)
  - Credit rating implied spread + risk-free rate
```

### WACC Assembly

```
WACC = (E/V) × Ke + (D/V) × Kd × (1 - t)

Where:
  E = Market value of equity (Market Cap)
  D = Market value of debt (book value as proxy)
  V = E + D (total enterprise value of capital)
  t = Marginal tax rate
```

---

## Free Cash Flow Build

### Unlevered Free Cash Flow (UFCF)

```
Revenue
- Cost of Goods Sold
= Gross Profit

- Selling, General & Administrative
- Research & Development
- Other Operating Expenses
= EBIT (Operating Income)

- Taxes on EBIT (= EBIT × Tax Rate)
= NOPAT (Net Operating Profit After Tax)

+ Depreciation & Amortization
- Capital Expenditures
- Increase in Net Working Capital
= Unlevered Free Cash Flow
```

### Net Working Capital

```
NWC = Current Operating Assets - Current Operating Liabilities

Current Operating Assets:
  + Accounts Receivable
  + Inventory
  + Prepaid Expenses

Current Operating Liabilities:
  + Accounts Payable
  + Accrued Expenses
  + Deferred Revenue (current portion)

Change in NWC = NWC_current - NWC_prior
  Positive change → cash outflow (uses cash)
  Negative change → cash inflow (source of cash)
```

### Working Capital Ratios (For Projection)

```
Days Sales Outstanding (DSO) = (Accounts Receivable / Revenue) × 365
Days Inventory Outstanding (DIO) = (Inventory / COGS) × 365
Days Payable Outstanding (DPO) = (Accounts Payable / COGS) × 365

Cash Conversion Cycle = DSO + DIO - DPO
```

---

## Terminal Value

### Gordon Growth Model (Perpetuity Growth)

```
TV = UFCF_n × (1 + g) / (WACC - g)

Where:
  UFCF_n = Unlevered free cash flow in final projection year
  g      = Terminal growth rate (typically 2.0-3.0%)
  WACC   = Weighted average cost of capital

Constraints:
  g must be < WACC (otherwise TV is infinite/negative)
  g should approximate long-term nominal GDP growth
  g > 3.5% requires strong justification
```

### Exit Multiple Method

```
TV = EBITDA_n × Exit Multiple

Choosing the exit multiple:
  1. Current EV/EBITDA of mature industry peers
  2. Historical median EV/EBITDA for the sector (5-10 year)
  3. Current trading multiple of the target (if at steady state)

Sanity check: Implied perpetuity growth from exit multiple
  Implied g = WACC - (UFCF_n+1 / TV)
  If implied g > 4%, the exit multiple may be too high
```

---

## Discounting

### Present Value of Projected Cash Flows

```
PV(UFCF) = Σ [UFCF_t / (1 + WACC)^t]  for t = 1 to n

Mid-year convention (recommended):
  PV(UFCF) = Σ [UFCF_t / (1 + WACC)^(t - 0.5)]  for t = 1 to n
```

### Present Value of Terminal Value

```
PV(TV) = TV / (1 + WACC)^n

With mid-year convention:
  PV(TV) = TV / (1 + WACC)^(n - 0.5)
```

---

## Enterprise Value to Equity Value Bridge

```
Enterprise Value = PV(UFCF) + PV(TV)

Equity Value =
  Enterprise Value
  + Cash & Cash Equivalents
  + Short-term Investments
  - Total Debt (short-term + long-term)
  - Preferred Stock (liquidation value)
  - Minority Interest (at market or book)
  - Pension Deficit (if material)
  - Operating Lease Obligations (if not already in debt)
  + Equity Method Investments (at fair value, if material)

Implied Share Price = Equity Value / Fully Diluted Shares Outstanding
```

### Fully Diluted Share Count (Treasury Stock Method)

```
Diluted Shares = Basic Shares + Incremental Shares from Options/Warrants + RSU Shares

For Options/Warrants:
  If Exercise Price < Current Stock Price (in the money):
    Incremental Shares = Options × (Stock Price - Exercise Price) / Stock Price

For RSUs:
  Incremental Shares = Unvested RSUs × (1 - Tax Withholding Rate)
  (Simplified: just add full RSU count)
```

---

## Margin Formulas

```
Gross Margin = Gross Profit / Revenue
Operating Margin = EBIT / Revenue
EBITDA Margin = EBITDA / Revenue
Net Margin = Net Income / Revenue
FCF Margin = Free Cash Flow / Revenue

Revenue Growth = (Revenue_t - Revenue_t-1) / Revenue_t-1
CAGR = (Revenue_end / Revenue_start)^(1/n) - 1
```

---

## Key Ratios for Sanity Checks

```
TV as % of EV:
  Healthy: 50-75%
  Concerning: > 80% (too dependent on terminal assumptions)

Implied EV/EBITDA (from DCF):
  Compare to current trading multiple and comps
  Large divergence → re-examine assumptions

FCF Yield at Fair Value:
  FCF Yield = Year 1 UFCF / Enterprise Value
  Should be comparable to peers
  < 2% for growth companies
  > 5% for mature/value companies

Revenue CAGR Check:
  Projected 5-year CAGR should be justifiable
  Compare to: historical CAGR, industry growth, TAM analysis
```
