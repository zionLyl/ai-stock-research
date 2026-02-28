---
name: sector-overview
description: >
  Industry landscape analysis and sector research for US equities. Use when the user wants a
  sector or industry overview, market sizing, competitive landscape mapping, key trend analysis,
  top player comparison, or valuation context for a sector. Triggers on: "sector overview",
  "industry landscape", "industry analysis", "sector report", "market landscape",
  "competitive landscape", "who are the top players in", "sector deep dive".
---

# Sector Overview

Generate a structured industry landscape report covering market sizing, competitive dynamics,
key players, valuation context, and investment implications. Output a Markdown report designed
for an individual investor who wants to understand an industry before picking stocks in it.

## Purpose

Sector overviews answer: "What's the state of this industry, who are the key players, and
where are the opportunities?" Use this before stock-picking in an unfamiliar sector or to
refresh understanding of a sector you already invest in.

## Workflow

### Step 0: Define Scope

Confirm with the user:

1. **Sector / subsector** — How narrowly defined? ("semiconductors" vs "AI accelerator chips")
2. **Depth** — Overview (5-8 pages) or deep dive (12-18 pages)?
3. **Angle** — Neutral landscape or thematic thesis (e.g., "AI infrastructure buildout")?
4. **Universe** — US-listed only (default) or include international players?

If the user is vague ("tell me about tech"), ask for specificity. "Tech" is too broad — narrow
to a subsector (cloud infrastructure, cybersecurity, e-commerce, etc.).

### Step 1: Market Overview

#### Market Size & Growth

Search via MCP for recent industry reports and data:
```
"{INDUSTRY} market size 2025"
"{INDUSTRY} TAM total addressable market"
"{INDUSTRY} market forecast CAGR"
```

Assemble:
- Total addressable market (TAM) with source and year
- Current served addressable market (SAM) if distinguishable
- Historical growth rate (3-5 year CAGR)
- Forecast growth rate and key growth assumptions
- Market segmentation (by product type, geography, end market, customer type)

**Critical:** Always cite the source for market size data. Different research firms produce
wildly different TAM estimates — note the range and use the most credible source.

#### Industry Structure

| Dimension | What to Assess |
|---|---|
| Concentration | Fragmented vs consolidated — top 5 market share |
| Value chain | Where does value accrue? (components, platforms, services) |
| Business models | Subscription, transaction, licensing, hardware, services, hybrid |
| Barriers to entry | Capital, regulatory, technical, network effects, switching costs |
| Cyclicality | Cyclical vs secular — sensitivity to macro conditions |

#### Key Trends & Drivers

Identify 3-5 major themes:

**Tailwinds (growth drivers):**
- Secular technology shifts (AI, cloud, electrification)
- Regulatory changes creating demand
- Demographic or behavioral shifts
- Underinvestment cycles creating replacement demand

**Headwinds (risks):**
- Regulatory tightening
- Technology disruption from adjacent sectors
- Margin compression from competition
- Supply chain or input cost pressures

**Disruption vectors:**
- Which incumbents are vulnerable and why?
- Where are new entrants gaining traction?
- What adjacent industries could encroach?

### Step 2: Competitive Landscape

#### Top Players Comparison

Fetch data for the 8-12 largest public companies in the sector:

```bash
python scripts/yahoo_finance.py {TICK1},{TICK2},... --screen --json
```

Build the primary comparison table:

| Company | Ticker | Market Cap | Revenue | Rev Growth | EBITDA Margin | Market Share | Key Differentiator |
|---------|--------|-----------|---------|-----------|--------------|-------------|-------------------|
| | | | | | | | |

#### Company Profiles (Top 5-8)

For each major player, a concise profile:

1. **Business description** — What they do in 2-3 sentences
2. **Strategic positioning** — Moat and competitive advantage
3. **Recent developments** — Last 1-2 quarters of earnings, M&A, product launches
4. **Valuation snapshot** — Current P/E, EV/EBITDA, EV/Revenue
5. **Bull / bear in one line each** — Why own vs why avoid

#### Competitive Dynamics

Assess how companies compete:
- **Price vs product vs service vs distribution** — what's the primary axis?
- **Share shifts** — Who is gaining/losing share and why?
- **Moat durability** — Are competitive advantages strengthening or eroding?
- **M&A activity** — Consolidation trends, recent deals, likely targets
- **New entrant threat** — Private companies or adjacent players to watch

### Step 3: Valuation Context

#### Current Sector Multiples

| Multiple | Current | 5Y Avg | 5Y Low | 5Y High | vs S&P 500 |
|----------|---------|--------|--------|---------|-----------|
| P/E (Forward) | | | | | premium/discount |
| EV/EBITDA | | | | | |
| EV/Revenue | | | | | |
| PEG | | | | | |

**Data sourcing:**
- Calculate from individual company data fetched via yfinance (market-cap-weighted or median)
- Cross-check with MCP search: "{INDUSTRY} sector valuation multiples"

#### Premium / Discount Drivers

Why does this sector trade at a premium or discount to the broader market?
- Growth profile relative to S&P 500
- Margin structure and cash flow generation
- Cyclicality and earnings visibility
- Recent sentiment shifts (AI hype, regulatory fear, etc.)

#### M&A Transaction Multiples

Search for recent M&A deals in the sector:
```
"{INDUSTRY} M&A transactions 2024 2025"
"{INDUSTRY} acquisition multiples"
```

Note deal multiples (EV/Revenue, EV/EBITDA) as a private market valuation anchor.

### Step 4: Investment Implications

#### Opportunity Map

Categorize companies into a simple framework:

```
                    HIGH GROWTH
                        │
         Growth at      │      Premium
         Reasonable     │      Growth
         Price          │      (expensive but fast)
    ────────────────────┼────────────────────
         Value /        │      Fully
         Turnaround     │      Valued
         (cheap for a   │      (no edge)
          reason?)      │
                        │
                    LOW GROWTH

         CHEAP ─────────────────── EXPENSIVE
              (vs sector median multiples)
```

#### Key Debates

For each major debate in the sector, present both sides:

1. **{Debate topic}**
   - Bull: {argument}
   - Bear: {argument}
   - Data to watch: {what resolves it}

#### Thematic Bets

How can an investor express a view on this sector?
- **Pure play exposure** — companies with 80%+ revenue from this sector
- **Picks-and-shovels** — infrastructure/tools providers
- **Contrarian** — out-of-favor names with thesis for re-rating
- **Quality compounders** — high-ROIC, steady growers for long-term holding

### Step 5: Output

#### Markdown Report Structure

```markdown
# {SECTOR} Industry Overview

**Date:** {DATE} | **Analyst:** AI-assisted | **Depth:** {Overview/Deep Dive}

## Executive Summary
{3-5 bullet points: market size, growth, key theme, valuation context, top pick}

## Market Overview
### Size & Growth
### Industry Structure
### Key Trends

## Competitive Landscape
### Top Players Comparison (table)
### Company Profiles
### Competitive Dynamics

## Valuation Context
### Sector Multiples (current vs historical)
### Premium/Discount Analysis
### M&A Benchmarks

## Investment Implications
### Opportunity Map
### Key Debates
### Thematic Bets

## Appendix
### Data Sources
### Methodology Notes
```

**File naming:** `{SECTOR}_Overview_{DATE}.md`
**Location:** `~/.openclaw/workspace/reports/`

#### Report Length Guidelines

| Depth | Length | When to Use |
|---|---|---|
| Quick Overview | 3-5 pages | "Give me a quick rundown of {sector}" |
| Standard (default) | 5-8 pages | `/sector {industry}` command |
| Deep Dive | 12-18 pages | Explicit request for deep analysis |

Default to **Standard** unless otherwise specified.

## Sector-Specific Frameworks

Different sectors require different analytical lenses:

| Sector | Key Framework | Primary Multiples |
|---|---|---|
| SaaS / Cloud | Rule of 40, NRR, gross margin | EV/Revenue, EV/ARR |
| Semiconductors | Cycle positioning, inventory days | EV/EBITDA, P/E |
| Financials | Credit quality, NIM, capital ratios | P/TBV, ROE |
| Healthcare | Pipeline analysis, patent cliff | EV/Revenue, P/E |
| Retail | Same-store sales, e-commerce mix | EV/EBITDA, P/E |
| Energy | Commodity exposure, breakeven price | EV/EBITDA, FCF yield |
| Industrials | Backlog, book-to-bill, cycle position | EV/EBITDA, P/E |
| REITs | Occupancy, NOI growth, NAV | P/FFO, dividend yield |

See `../comps-analysis/references/schemas.md` for detailed metric definitions per sector.

## Quality Checklist

- [ ] Sector/subsector clearly defined (not too broad)
- [ ] Market size cited with source (not made up)
- [ ] TAM vs SAM distinguished (if material difference)
- [ ] Top 5-8 players profiled with current data
- [ ] Competitive dynamics assessed (not just a company list)
- [ ] Valuation multiples current (fetched in session, not from memory)
- [ ] Historical valuation range provided for context
- [ ] 3-5 key trends identified with supporting evidence
- [ ] Investment implications are actionable (not just "sector is interesting")
- [ ] Key debates presented with both bull and bear sides
- [ ] All data sourced and dated
- [ ] Stale data flagged

## Common Pitfalls

- **Too broad:** "Technology sector overview" is meaningless. Always narrow to a subsector.
- **TAM hype:** Distinguish between inflated TAM projections and realistic addressable market.
  Every industry report claims $X trillion by 20XX — apply skepticism.
- **Recency bias:** Don't let the last quarter's narrative dominate the landscape analysis.
  Look at 3-5 year trends.
- **Survivor focus:** Include discussion of failures and challenged players, not just winners.
- **Static snapshot:** Note that sector overviews age fast. Date everything and flag what may
  be stale within 3 months.

## Integration with Other Skills

- **stock-screening:** Sector overview identifies key metrics → feed into screening filters
- **comps-analysis:** Top players comparison is a natural precursor to detailed comps
- **thesis-tracker:** Sector themes inform thesis pillars for individual stocks
- **earnings-analysis:** Sector context improves earnings interpretation
- **morning-note:** Sector trends inform which news items matter
