---
name: thesis-tracker
description: >
  Investment thesis creation, tracking, and maintenance for US equities. Use when the user
  wants to document a bull/bear case, create an investment thesis, update an existing thesis
  with new data, track thesis pillars and catalysts, or review conviction levels. Triggers on:
  "thesis", "bull case", "bear case", "investment case", "why I own", "track my thesis",
  "conviction", "catalyst", "update my thesis on".
---

# Thesis Tracker

Create, maintain, and update structured investment theses with persistent storage in `memory/`.
Each thesis is a living document — updated with every earnings report, material news event,
or user-initiated review. The goal: force intellectual honesty about why you own something.

## Core Principle

Every position needs a written thesis. A thesis that can't be articulated clearly is a position
that shouldn't exist. This skill enforces structure on the messy process of investment reasoning.

## Thesis Data Model

Each thesis is stored as a structured Markdown file in `memory/thesis_{TICKER}.md`:

```markdown
# {TICKER} Investment Thesis

## Meta
- **Created:** {DATE}
- **Last Updated:** {DATE}
- **Conviction:** {1-5 scale, with label}
- **Position Type:** Long / Short / Watchlist
- **Time Horizon:** {months/years}
- **Target Price:** ${X.XX} ({+/-X%} from current)
- **Stop-Loss:** ${X.XX} ({-X%} from entry)

## One-Line Thesis
{Single sentence that captures why you own this — forces clarity}

## Bull Case Pillars (3-5 reasons to own)
1. **{Pillar Name}** — {Description}
   - Evidence: {Data points supporting this pillar}
   - Status: Intact / Weakening / Broken
   - Last verified: {DATE}

2. **{Pillar Name}** — {Description}
   - Evidence: {Data points}
   - Status: Intact / Weakening / Broken
   - Last verified: {DATE}

## Bear Case / Risks (3-5 reasons this could fail)
1. **{Risk Name}** — {Description}
   - Probability: Low / Medium / High
   - Impact: Low / Medium / High
   - Mitigation: {What would reduce this risk}

## Catalysts (Upcoming events that could move the stock)
- [ ] {Catalyst 1} — Expected: {DATE}
- [ ] {Catalyst 2} — Expected: {DATE}
- [x] {Past catalyst} — Occurred: {DATE}, Result: {outcome}

## Valuation Anchor
- **Method:** {DCF / Comps / Sum-of-Parts}
- **Fair Value Estimate:** ${X.XX}
- **Current Price:** ${X.XX}
- **Margin of Safety:** {X%}
- **Key Assumptions:** {1-2 sentences}

## Update Log
| Date | Event | Action | Conviction Change |
|------|-------|--------|-------------------|
| {DATE} | {What happened} | {What you did/concluded} | {4→5, 3→3, etc.} |
```

## Workflow

### Creating a New Thesis

#### Step 1: Gather Foundation Data

Fetch comprehensive data for the target:

```bash
python scripts/yahoo_finance.py {TICKER} --json
python scripts/sec_edgar.py {TICKER} --form 10-K --json
```

Search for qualitative context:
- Business model and competitive position
- Recent earnings and guidance
- Analyst consensus and controversy
- Industry tailwinds/headwinds

#### Step 2: Structure the Thesis with the User

Walk through each section interactively:

1. **One-line thesis** — Ask: "In one sentence, why should you own {TICKER}?"
   - If the user struggles, that's a signal — dig deeper before proceeding
   - Help refine vague theses into specific, testable claims

2. **Bull case pillars** — Ask: "What are the 3-5 specific reasons this stock will work?"
   - Each pillar should be independently verifiable
   - Each pillar should have specific evidence (not "good company")
   - Examples of good pillars:
     - "Cloud revenue growing 30%+ with expanding margins as the business scales"
     - "Trading at 15x P/E vs 20x historical average, with no fundamental deterioration"
     - "New product cycle launching Q3 addresses $50B TAM"

3. **Bear case / risks** — Ask: "What could go wrong? What would make you sell?"
   - This is the most important section — forces pre-commitment to exit criteria
   - Pre-mortem: "Imagine it's 12 months from now and the stock is down 40%. Why?"

4. **Catalysts** — Ask: "What specific events could unlock value in the next 6-12 months?"
   - Earnings dates, product launches, regulatory decisions
   - Macro events (rate cuts, trade policy)
   - Corporate actions (buybacks, dividend increases, spin-offs)

5. **Valuation anchor** — Establish a fair value estimate
   - Link to DCF or comps analysis if available
   - Or simple multiple-based estimate (forward P/E × consensus EPS)

6. **Conviction level** — Set initial conviction on 1-5 scale

#### Step 3: Save and Confirm

Save the thesis to `memory/thesis_{TICKER}.md`.
Confirm the full thesis with the user before finalizing.

### Conviction Scale

| Level | Label | Meaning | Position Size Guidance |
|---|---|---|---|
| 5 | **Maximum Conviction** | Thesis is airtight, catalysts imminent, valuation compelling | Top 3 position (5-10% of portfolio) |
| 4 | **High Conviction** | Strong thesis with clear edge, minor uncertainties | Meaningful position (3-5%) |
| 3 | **Moderate Conviction** | Good thesis but execution risk or valuation less compelling | Standard position (2-3%) |
| 2 | **Low Conviction** | Thesis has notable weaknesses or uncertainty | Small position (1-2%) |
| 1 | **Speculative** | High-risk/high-reward, thesis could easily break | Minimal position (<1%) |

### Updating an Existing Thesis

#### Triggers for Thesis Update

- **Earnings report** — After running `/earnings`, offer to update the thesis
- **Material news** — Acquisition, management change, regulatory action
- **Price movement** — Stock moves >15% without clear cause
- **Catalyst resolution** — A catalyst event has occurred
- **Periodic review** — Monthly or quarterly check-in
- **User request** — Explicit "update my thesis on {TICKER}"

#### Update Process

1. Load existing thesis from `memory/thesis_{TICKER}.md`
2. Fetch current data (price, key metrics, recent news)
3. Review each pillar: Is it still intact, weakening, or broken?
4. Review each risk: Has probability or impact changed?
5. Check catalysts: Any resolved or new ones to add?
6. Update valuation anchor with current data
7. Re-assess conviction level
8. Add entry to update log

#### Pillar Status Framework

```
Intact      → Evidence still supports the pillar. No action needed.
Weakening   → Mixed signals or partial deterioration. Watch closely.
Broken      → Evidence contradicts the pillar. Serious concern.

If 2+ pillars are Broken → Recommend reviewing the entire position
If majority are Weakening → Recommend reducing conviction by 1 level
```

### Thesis Review (Monthly/Quarterly)

When the user asks for a thesis review or periodic check:

1. Load all thesis files from `memory/thesis_*.md`
2. For each thesis:
   - Fetch current price and calculate return since last update
   - Check if any catalysts have passed their expected dates
   - Flag any thesis not updated in >90 days
3. Generate a summary dashboard:

```markdown
# Thesis Review — {DATE}

| Ticker | Conviction | Last Updated | Return Since | Pillars Status | Action Needed |
|--------|-----------|-------------|-------------|---------------|---------------|
| AAPL   | 4/5       | 2025-01-15  | +8.3%       | 3 intact, 1 weakening | Review weakening pillar |
| NVDA   | 5/5       | 2025-02-01  | +15.2%      | 4 intact      | None |
| MSFT   | 3/5       | 2024-11-20  | -2.1%       | Not reviewed in 90+ days | Overdue for update |
```

### Kill Switch — When to Exit

A thesis should define **in advance** when to sell:

1. **Broken thesis:** 2+ bull case pillars broken → sell
2. **Valuation ceiling:** Stock exceeds fair value by >20% without thesis improvement → trim
3. **Stop-loss:** Predetermined loss threshold hit → reassess (not automatic sell)
4. **Time decay:** Catalysts haven't materialized within expected timeframe → reassess
5. **Better opportunity:** Higher-conviction idea with limited capital → swap

**Pre-commitment is key.** The time to decide when to sell is when you buy, not when the
stock is crashing and emotions are running high.

## Quality Checklist

- [ ] One-line thesis is specific and testable (not "good company")
- [ ] 3-5 bull case pillars with specific evidence
- [ ] 3-5 bear case risks with probability/impact assessment
- [ ] Upcoming catalysts with expected dates
- [ ] Valuation anchor with stated methodology
- [ ] Conviction level set with position size context
- [ ] Exit criteria clearly defined (when to sell)
- [ ] Update log started with creation entry
- [ ] Saved to `memory/thesis_{TICKER}.md`

## Integration with Other Skills

- **earnings-analysis:** Post-earnings → update thesis pillars and conviction
- **dcf-valuation:** DCF result → update valuation anchor
- **comps-analysis:** Relative valuation → context for fair value estimate
- **morning-note:** News alerts → trigger thesis review if material
- **portfolio-monitor:** Position P&L → context for thesis review
