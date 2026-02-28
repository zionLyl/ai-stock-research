# Earnings Analysis — Detailed Workflow

Step-by-step execution guide for producing a post-earnings analysis report.

## Step 1: Identify the Target

Confirm with the user:
- **Ticker symbol** (validate it's a US-listed equity)
- **Quarter** — which fiscal quarter? Map calendar to fiscal year if needed
  - Many companies have non-calendar fiscal years (e.g., AAPL FY ends September)
  - Ask: "AAPL Q4 2025 — do you mean the quarter ending September 2025 (Apple's fiscal Q4) or December 2025 (calendar Q4)?"
- **Depth** — quick take, standard (default), or deep dive?

## Step 2: Fetch Quantitative Data

Execute in this order:

### 2a. yfinance — Primary Financial Data

```bash
python scripts/yahoo_finance.py {TICKER} --json
```

Extract:
- Latest quarterly earnings (actual EPS, estimated EPS, surprise)
- Quarterly income statement (current + prior 3 quarters)
- Quarterly balance sheet
- Quarterly cash flow statement
- Price history around earnings date (5 days before, 5 days after)
- Analyst price targets and recommendations

### 2b. SEC EDGAR — Official Filing Data

```bash
python scripts/sec_edgar.py {TICKER} --form 10-Q --json
```

Use EDGAR for:
- Verifying yfinance numbers against official filings
- Segment data (often only in filings, not yfinance)
- Management Discussion & Analysis (MD&A) section
- Risk factor updates
- Related party transactions or unusual items

### 2c. Cross-Verification

Compare yfinance and EDGAR numbers:
- Revenue should match within rounding
- EPS may differ (diluted vs basic, GAAP vs non-GAAP)
- If discrepancy >2%, investigate and note which number to use

## Step 3: Fetch Qualitative Data

### 3a. Earnings Call Transcript

Search via MCP:
```
"{TICKER} Q{N} {YEAR} earnings call transcript"
"{COMPANY_NAME} earnings call transcript {MONTH} {YEAR}"
```

If full transcript found:
- Extract management prepared remarks summary
- Extract key Q&A exchanges
- Note management tone (word analysis: "strong", "challenging", "uncertain")

If only summary available:
- Use summary but note it's not a full transcript
- Search for additional analyst coverage to fill gaps

### 3b. Analyst Reactions

Search via MCP:
```
"{TICKER} earnings analyst reaction"
"{TICKER} earnings price target change {DATE}"
```

Collect:
- Major analyst rating changes
- Price target revisions (upgrades/downgrades)
- Consensus estimate revisions post-earnings

### 3c. News Context

Search for market-moving context:
```
"{TICKER} earnings {DATE} news"
```

- Were there concurrent announcements (acquisitions, restructuring)?
- Industry-wide events affecting interpretation?
- Macro backdrop (Fed meetings, economic data releases)

## Step 4: Analyze

Work through each section of the analysis framework (see SKILL.md):

1. **Beat/Miss** — Calculate EPS and revenue surprise
2. **Margin Trends** — Build 4-8 quarter margin table
3. **Segments** — Break down by business unit if applicable
4. **Guidance** — Categorize and compare to consensus
5. **Balance Sheet** — Quick health check
6. **Cash Flow** — Quality of earnings assessment
7. **Forward Signals** — Management commentary analysis

## Step 5: Synthesize

Combine quantitative and qualitative findings into:

1. **Headline** — One sentence capturing the quarter (e.g., "Revenue beat with margin expansion, but soft guidance weighs on shares")
2. **Three key takeaways** — Bullet points, most important first
3. **Investment implication** — What should a holder do? What should a potential buyer think?
4. **Risk update** — Any new risks surfaced this quarter?

## Step 6: Generate Report

Follow the structure in `references/report-structure.md`.

Save to: `~/.openclaw/workspace/reports/{TICKER}_Earnings_Q{N}_{YEAR}.md`

## Step 7: Post-Report Actions

Suggest to the user:
- Update thesis if one exists: "Want me to update your {TICKER} thesis with these results?"
- Refresh valuation: "Should I update the DCF with new guidance numbers?"
- Check portfolio impact: "This stock is in your portfolio — the {X}% move means {$Y} P&L impact."
