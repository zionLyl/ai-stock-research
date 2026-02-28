---
description: Create, update, or review an investment thesis for a stock
argument-hint: "[company name or ticker] [optional: 'update', 'review']"
---

# Thesis Tracker Command

Create a new investment thesis, update an existing one with new data, or review all
active theses for a periodic check-in.

## Workflow

### Step 1: Parse Input

Extract from the user's input:
- **Company ticker** (for create/update) or **"review"** (for portfolio-wide review)
- **Action** — create (default if no thesis exists), update (if thesis exists), or review (all theses)

If not provided, ask:
- "What company? Or would you like to review all active theses?"

### Step 2: Route by Action

**Create new thesis:**
1. Check `memory/thesis_{TICKER}.md` — if exists, offer to update instead
2. Use `skill: "thesis-tracker"` to walk through thesis creation:
   - Fetch foundation data via yfinance + SEC EDGAR + MCP search
   - Structure interactively: one-line thesis, bull pillars, bear risks, catalysts, valuation anchor
   - Set conviction level (1-5) and exit criteria
3. Save to `memory/thesis_{TICKER}.md`

**Update existing thesis:**
1. Load `memory/thesis_{TICKER}.md`
2. Fetch current price, recent news, and latest earnings data
3. Review each pillar (intact / weakening / broken), each risk, and catalyst status
4. Update valuation anchor, re-assess conviction
5. Add entry to update log
6. Save updated file

**Review all theses:**
1. Load all `memory/thesis_*.md` files
2. For each: fetch current price, calculate return since last update
3. Flag theses not updated in >90 days
4. Generate summary dashboard with action items

### Step 3: Deliver Output

Provide:
1. **Thesis document** — full structured thesis (create) or updated thesis (update)
2. **Review dashboard** — summary table with conviction, returns, and action needed (review)
3. **Alerts** — broken pillars, overdue reviews, triggered catalysts

## Quality Checklist

- [ ] One-line thesis is specific and testable
- [ ] 3-5 bull pillars with evidence and status
- [ ] 3-5 bear risks with probability/impact
- [ ] Catalysts with expected dates
- [ ] Conviction level set with clear rationale
- [ ] Exit criteria defined (when to sell)
- [ ] Saved to `memory/thesis_{TICKER}.md`
