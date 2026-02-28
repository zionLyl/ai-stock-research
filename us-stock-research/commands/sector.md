---
description: Generate an industry landscape overview with market sizing, key players, and valuation context
argument-hint: "[industry or sector, e.g. 'semiconductors', 'cloud infrastructure', 'cybersecurity']"
---

# Sector Overview Command

Create a structured industry landscape report covering market sizing, competitive dynamics,
top players, valuation context, and investment implications.

## Workflow

### Step 1: Parse Input

Extract from the user's input:
- **Sector / subsector** (e.g., "semiconductors", "AI infrastructure", "cybersecurity")
- **Depth** — overview (default, 5-8 pages) or deep dive (12-18 pages)

If not provided or too broad, ask:
- "What specific industry or subsector? (e.g., 'cloud infrastructure' rather than just 'tech')"

### Step 2: Load Sector Overview Skill

Use `skill: "sector-overview"` to generate the report:

1. **Market overview** — TAM, growth rate (CAGR), market segmentation via MCP search
2. **Industry structure** — concentration, value chain, barriers to entry, business models
3. **Key trends** — 3-5 tailwinds and headwinds with supporting evidence
4. **Competitive landscape** — top 8-12 players via yfinance bulk data fetch
   - Comparison table: market cap, revenue, growth, margins, market share
   - Company profiles for top 5-8 players
   - Competitive dynamics: share shifts, moat durability, M&A activity
5. **Valuation context** — sector multiples (current vs 5Y avg), premium/discount drivers
6. **Investment implications** — opportunity map, key debates (bull vs bear), thematic bets

### Step 3: Deliver Output

Provide:
1. **Markdown report** — saved to `~/.openclaw/workspace/reports/{SECTOR}_Overview_{DATE}.md`
2. **Executive summary** — 3-5 bullet points for quick consumption
3. **Follow-up suggestions** — screen the sector (`/screen`), deep-dive a specific name (`/earnings`, `/dcf`)

## Quality Checklist

- [ ] Subsector is specific enough to be actionable (not just "tech")
- [ ] Market size cited with source (not estimated from training data)
- [ ] Top 5-8 players profiled with current data from yfinance
- [ ] Valuation multiples fetched live with historical context
- [ ] Key trends supported by evidence
- [ ] Investment implications are actionable
- [ ] All data sourced and dated
