---
name: us-stock-research
description: Comprehensive US stock investment research suite for individual investors. Routes to specialized sub-skills for screening, earnings analysis, valuation, thesis tracking, and portfolio monitoring. Triggers on any US stock research request.
---

# US Stock Research Suite

A complete toolkit for researching, analyzing, and monitoring US-listed equities. Built for an individual programmer-investor managing a personal portfolio — data-driven, direct, no corporate jargon.

## When to Use This Skill

**Trigger on any of these requests:**
- Stock screening or filtering ("find cheap tech stocks", "screen for high-growth SaaS")
- Earnings analysis ("analyze AAPL earnings", "how did NVDA do last quarter")
- DCF valuation ("value MSFT", "build a DCF for GOOGL")
- Comparable company analysis ("comp AMZN against peers", "what's TSLA trading at vs peers")
- Investment thesis creation or update ("track my AAPL thesis", "update bull case for NVDA")
- Morning briefing ("what's happening pre-market", "morning note")
- Sector overview ("overview of semiconductor industry", "cloud computing landscape")
- Portfolio monitoring ("check my portfolio", "how are my holdings doing")

**Do NOT use when:**
- Requesting A-share / China stock research → use `cn-stock-research` skill instead
- Requesting crypto, forex, or commodity analysis → out of scope
- Asking general finance questions without a stock research angle

## Routing Logic

Route to the appropriate sub-skill based on user intent:

| User Intent | Sub-Skill | Command |
|---|---|---|
| Screen stocks by criteria | `stock-screening` | `/screen` |
| Analyze quarterly earnings | `earnings-analysis` | `/earnings` |
| Build DCF valuation model | `dcf-valuation` | `/dcf` |
| Compare against peer companies | `comps-analysis` | `/comps` |
| Create/update investment thesis | `thesis-tracker` | `/thesis` |
| Pre-market daily briefing | `morning-note` | `/morning-note` |
| Industry landscape analysis | `sector-overview` | `/sector` |
| Monitor portfolio P&L | `portfolio-monitor` | — |

If the user's intent spans multiple skills (e.g., "analyze AAPL earnings and update my thesis"), execute them sequentially: complete the primary analysis first, then feed results into the secondary skill.

## Data Sources

We rely on **free, publicly available** data sources. No Bloomberg, FactSet, or institutional terminals.

### Priority Order

1. **yfinance (Yahoo Finance API)** — Primary source for structured financial data
   - Current price, historical prices, key statistics
   - Income statement, balance sheet, cash flow (annual & quarterly)
   - Earnings dates, analyst estimates, recommendations
   - Script: `scripts/yahoo_finance.py`

2. **MCP Search Engines** — For news, analysis, transcripts, and unstructured data
   - Tavily, Serper, Firecrawl, Jina (via mcporter)
   - Use for: earnings transcripts, analyst commentary, news, management quotes
   - Always verify dates — search results may be stale

3. **SEC EDGAR** — Official filings (10-K, 10-Q, 8-K, proxy statements)
   - Free API, no authentication required
   - Script: `scripts/sec_edgar.py`
   - Use for: detailed financial data, risk factors, management discussion

4. **Web Fetch** — Direct page retrieval for specific URLs
   - Earnings call transcripts, press releases, investor presentations
   - Always verify the source and date

### Data Verification Rules

- **Cross-check critical numbers** from at least 2 sources (yfinance + SEC filing)
- **Always verify dates** — never assume data is current without checking
- **Cite every data point** — format: `Source: [Source Name], [Date], [URL if applicable]`
- **Flag stale data** — if data is >3 months old, explicitly note this
- **Never use training data** as a primary source — always fetch live data

## Output Standards

### Report Format
- **Primary:** Markdown reports delivered in chat
- **Secondary:** Excel models (DCF, comps) saved to `~/.openclaw/workspace/reports/`
- **File naming:** `{TICKER}_{Type}_{Date}.{ext}` (e.g., `AAPL_Earnings_Q4_2025.md`)

### Quality Checklist (applies to ALL outputs)
- [ ] Every number has a cited source
- [ ] All data verified as current (not from training knowledge)
- [ ] Key metrics cross-checked from 2+ sources
- [ ] Date of analysis clearly stated
- [ ] Clear "what it means" interpretation, not just raw numbers
- [ ] Actionable conclusion or recommendation
- [ ] Risks and caveats explicitly stated

### Writing Style
- Direct and data-driven — lead with numbers, not adjectives
- "Revenue grew 15% to $94.9B" not "Strong revenue growth"
- Use tables for comparisons, not paragraphs
- Bullet points for key takeaways
- English for reports (US stocks), bilingual commentary acceptable
- No corporate jargon — write for a programmer who invests, not a banker

## Scripts

| Script | Purpose | Usage |
|---|---|---|
| `scripts/yahoo_finance.py` | Yahoo Finance data fetcher | `python yahoo_finance.py AAPL [--json\|--financials\|--screen TICK1,TICK2]` |
| `scripts/sec_edgar.py` | SEC EDGAR filing fetcher | `python sec_edgar.py AAPL [--form 10-K\|--json\|--facts Revenues]` |
| `scripts/excel_builder.py` | Excel model builder | `python excel_builder.py AAPL dcf\|comps\|portfolio` |

## Sub-Skills

### stock-screening/
Quantitative stock screening across value, growth, quality, momentum, and special situation strategies. Uses yfinance for bulk data retrieval and ranking.

### earnings-analysis/
Post-earnings analysis report generation. Covers beat/miss analysis, segment breakdown, margin trends, guidance changes, and thesis impact. Produces a 5-8 page Markdown report.

### dcf-valuation/
Discounted cash flow model builder. Full DCF with WACC calculation, 5-year projections, terminal value (Gordon Growth + exit multiple), and sensitivity analysis. Outputs Excel model + Markdown summary.

### comps-analysis/
Comparable company analysis. Peer group selection, operating metrics, valuation multiples, and statistical benchmarking. Outputs Excel + Markdown summary.

### thesis-tracker/
Investment thesis creation and maintenance. Tracks thesis pillars, risks, catalysts, conviction level, and update log. Stores structured data in `memory/` for cross-session persistence.

### morning-note/
Pre-market daily briefing. Overnight developments, futures, key earnings, economic data, and coverage universe alerts. Designed for quick consumption (2-minute read).

### sector-overview/
Industry landscape analysis. Market size, competitive dynamics, key players, valuation context, and investment implications. 5-10 page overview or 15-20 page deep dive.

### portfolio-monitor/
Portfolio P&L monitoring and alerts. Tracks holdings, calculates returns, monitors alert thresholds, and generates performance summaries.

## Integration Notes

- This skill works alongside `cn-stock-research` (A-shares) under the same OpenClaw setup
- Reports save to `~/.openclaw/workspace/reports/` (shared directory)
- Thesis data persists in `memory/` for cross-session reference
- MCP tools are shared via mcporter configuration
