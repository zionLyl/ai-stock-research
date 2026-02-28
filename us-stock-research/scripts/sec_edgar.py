#!/usr/bin/env python3
"""
SEC EDGAR Filing Fetcher
Free API wrapper for accessing SEC filings (10-K, 10-Q, 8-K, etc.).

Usage:
    from sec_edgar import EdgarClient
    client = EdgarClient()
    cik = client.get_cik("AAPL")
    filings = client.get_recent_filings("AAPL")
    text = client.get_filing_text(accession_number)

SEC EDGAR API docs: https://www.sec.gov/edgar/sec-api-documentation
Rate limit: 10 requests per second (we enforce this).
"""

import json
import re
import sys
import time
from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import quote

# SEC requires a User-Agent header identifying the requester
USER_AGENT = "OpenClaw-StockResearch/1.0 (personal research tool)"
BASE_URL = "https://efts.sec.gov/LATEST"
EDGAR_DATA_URL = "https://data.sec.gov"
EDGAR_FULL_TEXT_URL = "https://efts.sec.gov/LATEST/search-index"

# Rate limiting: SEC allows 10 req/sec, we stay conservative at 5
_last_request_time = 0.0
_MIN_INTERVAL = 0.2  # 200ms between requests


def _rate_limited_request(url: str, max_retries: int = 3) -> bytes:
    """Make a rate-limited request to SEC EDGAR."""
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < _MIN_INTERVAL:
        time.sleep(_MIN_INTERVAL - elapsed)

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    }
    req = Request(url, headers=headers)

    for attempt in range(max_retries):
        try:
            _last_request_time = time.time()
            with urlopen(req, timeout=30) as response:
                return response.read()
        except HTTPError as e:
            if e.code == 429:  # Too Many Requests
                wait = 2 ** attempt
                print(f"Rate limited, waiting {wait}s...")
                time.sleep(wait)
                continue
            raise
        except URLError:
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            raise

    raise RuntimeError(f"Failed to fetch {url} after {max_retries} retries")


class EdgarClient:
    """SEC EDGAR API client."""

    def __init__(self):
        self._cik_cache = {}

    # ── CIK Lookup ────────────────────────────────────────────────────

    def get_cik(self, ticker: str) -> Optional[str]:
        """
        Look up CIK (Central Index Key) for a ticker symbol.
        Returns CIK as a zero-padded 10-digit string.
        """
        ticker = ticker.upper()
        if ticker in self._cik_cache:
            return self._cik_cache[ticker]

        url = f"{EDGAR_DATA_URL}/submissions/CIK{ticker}.json"
        try:
            # Try direct ticker lookup first (works for some)
            data = _rate_limited_request(url)
            result = json.loads(data)
            cik = str(result.get("cik", "")).zfill(10)
            self._cik_cache[ticker] = cik
            return cik
        except (HTTPError, KeyError):
            pass

        # Fall back to company search
        try:
            url = f"https://efts.sec.gov/LATEST/search-index?q=%22{quote(ticker)}%22&dateRange=custom&startdt=2020-01-01&forms=10-K"
            data = _rate_limited_request(url)
            result = json.loads(data)
            hits = result.get("hits", {}).get("hits", [])
            if hits:
                cik = str(hits[0].get("_source", {}).get("entity_id", "")).zfill(10)
                self._cik_cache[ticker] = cik
                return cik
        except Exception:
            pass

        # Try the company tickers JSON
        try:
            url = f"{EDGAR_DATA_URL}/files/company_tickers.json"
            data = _rate_limited_request(url)
            tickers_data = json.loads(data)
            for entry in tickers_data.values():
                if entry.get("ticker", "").upper() == ticker:
                    cik = str(entry.get("cik_str", "")).zfill(10)
                    self._cik_cache[ticker] = cik
                    return cik
        except Exception:
            pass

        return None

    # ── Company Info ──────────────────────────────────────────────────

    def get_company_info(self, ticker: str) -> Optional[dict]:
        """Get company information from EDGAR submissions."""
        cik = self.get_cik(ticker)
        if not cik:
            return None

        url = f"{EDGAR_DATA_URL}/submissions/CIK{cik}.json"
        try:
            data = _rate_limited_request(url)
            result = json.loads(data)
            return {
                "cik": cik,
                "name": result.get("name", ""),
                "ticker": ticker.upper(),
                "sic": result.get("sic", ""),
                "sic_description": result.get("sicDescription", ""),
                "fiscal_year_end": result.get("fiscalYearEnd", ""),
                "state": result.get("stateOfIncorporation", ""),
                "ein": result.get("ein", ""),
                "exchanges": result.get("exchanges", []),
                "category": result.get("category", ""),
            }
        except Exception:
            return None

    # ── Filings ───────────────────────────────────────────────────────

    def get_recent_filings(
        self,
        ticker: str,
        form_type: Optional[str] = None,
        count: int = 20,
    ) -> list[dict]:
        """
        Get recent filings for a company.
        form_type: "10-K", "10-Q", "8-K", "DEF 14A", etc. None for all types.
        """
        cik = self.get_cik(ticker)
        if not cik:
            return []

        url = f"{EDGAR_DATA_URL}/submissions/CIK{cik}.json"
        try:
            data = _rate_limited_request(url)
            result = json.loads(data)
        except Exception:
            return []

        recent = result.get("filings", {}).get("recent", {})
        if not recent:
            return []

        forms = recent.get("form", [])
        dates = recent.get("filingDate", [])
        accessions = recent.get("accessionNumber", [])
        primary_docs = recent.get("primaryDocument", [])
        descriptions = recent.get("primaryDocDescription", [])

        filings = []
        for i in range(min(len(forms), len(dates))):
            if form_type and forms[i] != form_type:
                continue
            accession_clean = accessions[i].replace("-", "")
            filing = {
                "form_type": forms[i],
                "filing_date": dates[i],
                "accession_number": accessions[i],
                "primary_document": primary_docs[i] if i < len(primary_docs) else "",
                "description": descriptions[i] if i < len(descriptions) else "",
                "url": (
                    f"https://www.sec.gov/Archives/edgar/data/{cik.lstrip('0')}"
                    f"/{accession_clean}/{primary_docs[i]}"
                    if i < len(primary_docs)
                    else ""
                ),
                "filing_index_url": (
                    f"https://www.sec.gov/Archives/edgar/data/{cik.lstrip('0')}"
                    f"/{accession_clean}/"
                ),
            }
            filings.append(filing)
            if len(filings) >= count:
                break

        return filings

    def get_10k_filings(self, ticker: str, count: int = 5) -> list[dict]:
        """Get recent 10-K (annual report) filings."""
        return self.get_recent_filings(ticker, form_type="10-K", count=count)

    def get_10q_filings(self, ticker: str, count: int = 8) -> list[dict]:
        """Get recent 10-Q (quarterly report) filings."""
        return self.get_recent_filings(ticker, form_type="10-Q", count=count)

    def get_8k_filings(self, ticker: str, count: int = 10) -> list[dict]:
        """Get recent 8-K (current report) filings."""
        return self.get_recent_filings(ticker, form_type="8-K", count=count)

    # ── Filing Text Extraction ────────────────────────────────────────

    def get_filing_text(
        self, filing_url: str, max_chars: int = 100000
    ) -> Optional[str]:
        """
        Fetch the text content of a filing document.
        Works with HTML filing documents.
        Returns plain text extracted from the filing.
        """
        try:
            headers = {"User-Agent": USER_AGENT}
            req = Request(filing_url, headers=headers)
            with urlopen(req, timeout=60) as response:
                content = response.read().decode("utf-8", errors="replace")

            # Strip HTML tags for a rough text extraction
            text = re.sub(r"<style[^>]*>.*?</style>", "", content, flags=re.DOTALL)
            text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.DOTALL)
            text = re.sub(r"<[^>]+>", " ", text)
            text = re.sub(r"&nbsp;", " ", text)
            text = re.sub(r"&amp;", "&", text)
            text = re.sub(r"&lt;", "<", text)
            text = re.sub(r"&gt;", ">", text)
            text = re.sub(r"&#\d+;", " ", text)
            text = re.sub(r"\s+", " ", text).strip()

            if len(text) > max_chars:
                text = text[:max_chars] + f"\n\n[Truncated at {max_chars} characters]"

            return text
        except Exception as e:
            return f"Error fetching filing: {e}"

    # ── Full-Text Search ──────────────────────────────────────────────

    def search_filings(
        self,
        query: str,
        form_type: Optional[str] = None,
        date_start: Optional[str] = None,
        date_end: Optional[str] = None,
        count: int = 10,
    ) -> list[dict]:
        """
        Full-text search across EDGAR filings.
        query: Search terms (company name, topic, etc.)
        date_start/date_end: Format "YYYY-MM-DD"
        """
        params = [f"q={quote(query)}", f"from=0", f"size={count}"]
        if form_type:
            params.append(f"forms={quote(form_type)}")
        if date_start:
            params.append(f"dateRange=custom&startdt={date_start}")
        if date_end:
            params.append(f"enddt={date_end}")

        url = f"https://efts.sec.gov/LATEST/search-index?{'&'.join(params)}"
        try:
            data = _rate_limited_request(url)
            result = json.loads(data)
            hits = result.get("hits", {}).get("hits", [])
            filings = []
            for hit in hits:
                source = hit.get("_source", {})
                filings.append(
                    {
                        "entity_name": source.get("entity_name", ""),
                        "file_date": source.get("file_date", ""),
                        "form_type": source.get("form_type", ""),
                        "file_num": source.get("file_num", ""),
                        "period_of_report": source.get("period_of_report", ""),
                    }
                )
            return filings
        except Exception:
            # Fallback to EFTS search endpoint
            url = f"https://efts.sec.gov/LATEST/search-index?q={quote(query)}"
            try:
                data = _rate_limited_request(url)
                result = json.loads(data)
                return result.get("hits", {}).get("hits", [])[:count]
            except Exception:
                return []

    # ── XBRL Financial Data ───────────────────────────────────────────

    def get_company_facts(self, ticker: str) -> Optional[dict]:
        """
        Get XBRL company facts (structured financial data).
        Returns all reported financial facts from SEC filings.
        This is a rich source of historical financial data.
        """
        cik = self.get_cik(ticker)
        if not cik:
            return None

        url = f"{EDGAR_DATA_URL}/api/xbrl/companyfacts/CIK{cik}.json"
        try:
            data = _rate_limited_request(url)
            return json.loads(data)
        except Exception:
            return None

    def get_financial_fact(
        self,
        ticker: str,
        taxonomy: str = "us-gaap",
        fact: str = "Revenues",
    ) -> list[dict]:
        """
        Get a specific financial fact from XBRL data.
        taxonomy: "us-gaap", "dei", "ifrs-full"
        fact: e.g., "Revenues", "NetIncomeLoss", "Assets", "EarningsPerShareBasic"
        """
        facts = self.get_company_facts(ticker)
        if not facts:
            return []

        facts_data = facts.get("facts", {}).get(taxonomy, {}).get(fact, {})
        units = facts_data.get("units", {})

        results = []
        for unit_type, entries in units.items():
            for entry in entries:
                results.append(
                    {
                        "value": entry.get("val"),
                        "unit": unit_type,
                        "end_date": entry.get("end"),
                        "start_date": entry.get("start"),
                        "fiscal_year": entry.get("fy"),
                        "fiscal_period": entry.get("fp"),
                        "form": entry.get("form"),
                        "filed": entry.get("filed"),
                        "accession": entry.get("accn"),
                    }
                )

        return results

    # ── Convenience Methods ───────────────────────────────────────────

    def get_latest_10k_url(self, ticker: str) -> Optional[str]:
        """Get URL of the most recent 10-K filing."""
        filings = self.get_10k_filings(ticker, count=1)
        if filings:
            return filings[0].get("url")
        return None

    def get_latest_10q_url(self, ticker: str) -> Optional[str]:
        """Get URL of the most recent 10-Q filing."""
        filings = self.get_10q_filings(ticker, count=1)
        if filings:
            return filings[0].get("url")
        return None

    def get_filing_summary(self, ticker: str) -> dict:
        """Summary of available filings for a company."""
        info = self.get_company_info(ticker)
        recent_10k = self.get_10k_filings(ticker, count=3)
        recent_10q = self.get_10q_filings(ticker, count=4)
        recent_8k = self.get_8k_filings(ticker, count=5)

        return {
            "company": info,
            "latest_10k": recent_10k,
            "latest_10q": recent_10q,
            "latest_8k": recent_8k,
            "total_10k": len(recent_10k),
            "total_10q": len(recent_10q),
            "total_8k": len(recent_8k),
        }


# ── CLI Interface ─────────────────────────────────────────────────────

def print_filings(ticker: str, form_type: Optional[str] = None):
    """Print recent filings for a ticker."""
    client = EdgarClient()
    info = client.get_company_info(ticker)

    if info:
        print(f"\n{'=' * 60}")
        print(f"  {info['name']} ({ticker}) | CIK: {info['cik']}")
        print(f"  SIC: {info['sic_description']}")
        print(f"  Fiscal Year End: {info['fiscal_year_end']}")
        print(f"{'=' * 60}")
    else:
        print(f"\nCould not find company info for {ticker}")
        return

    filings = client.get_recent_filings(ticker, form_type=form_type, count=15)
    if not filings:
        print("  No filings found.")
        return

    print(f"\n  Recent Filings{' (' + form_type + ')' if form_type else ''}:")
    print(f"  {'Form':<10} {'Date':<12} {'Description'}")
    print(f"  {'-' * 50}")
    for f in filings:
        desc = f["description"][:40] if f["description"] else ""
        print(f"  {f['form_type']:<10} {f['filing_date']:<12} {desc}")
    print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python sec_edgar.py <TICKER> [--form 10-K|10-Q|8-K] [--json] [--facts FACT_NAME]")
        sys.exit(1)

    ticker_arg = sys.argv[1].upper()
    client = EdgarClient()

    if "--json" in sys.argv:
        summary = client.get_filing_summary(ticker_arg)
        print(json.dumps(summary, indent=2, default=str))
    elif "--facts" in sys.argv:
        idx = sys.argv.index("--facts")
        fact_name = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else "Revenues"
        facts = client.get_financial_fact(ticker_arg, fact=fact_name)
        print(json.dumps(facts[-10:], indent=2, default=str))  # Last 10 entries
    else:
        form = None
        if "--form" in sys.argv:
            idx = sys.argv.index("--form")
            form = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else None
        print_filings(ticker_arg, form)
