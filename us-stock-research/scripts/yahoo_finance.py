#!/usr/bin/env python3
"""
Yahoo Finance Data Fetcher
Wrapper around yfinance for US stock research.

Usage:
    from yahoo_finance import StockData
    stock = StockData("AAPL")
    financials = stock.get_financials()
    price = stock.get_current_price()
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

try:
    import yfinance as yf
except ImportError:
    print("yfinance not installed. Run: pip install yfinance")
    sys.exit(1)


class StockData:
    """Fetch and structure stock data from Yahoo Finance."""

    def __init__(self, ticker: str):
        self.ticker = ticker.upper()
        self.stock = yf.Ticker(self.ticker)
        self._info = None

    @property
    def info(self) -> dict:
        """Cached company info."""
        if self._info is None:
            self._info = self.stock.info
        return self._info

    # ── Company Overview ──────────────────────────────────────────────

    def get_company_overview(self) -> dict:
        """Basic company information."""
        i = self.info
        return {
            "ticker": self.ticker,
            "name": i.get("longName", ""),
            "sector": i.get("sector", ""),
            "industry": i.get("industry", ""),
            "description": i.get("longBusinessSummary", ""),
            "website": i.get("website", ""),
            "employees": i.get("fullTimeEmployees", ""),
            "country": i.get("country", ""),
            "exchange": i.get("exchange", ""),
            "currency": i.get("currency", "USD"),
        }

    # ── Price & Market Data ───────────────────────────────────────────

    def get_current_price(self) -> dict:
        """Current price and trading data."""
        i = self.info
        return {
            "ticker": self.ticker,
            "price": i.get("currentPrice") or i.get("regularMarketPrice"),
            "previous_close": i.get("previousClose"),
            "open": i.get("open") or i.get("regularMarketOpen"),
            "day_high": i.get("dayHigh") or i.get("regularMarketDayHigh"),
            "day_low": i.get("dayLow") or i.get("regularMarketDayLow"),
            "volume": i.get("volume") or i.get("regularMarketVolume"),
            "avg_volume": i.get("averageVolume"),
            "market_cap": i.get("marketCap"),
            "52w_high": i.get("fiftyTwoWeekHigh"),
            "52w_low": i.get("fiftyTwoWeekLow"),
            "50d_avg": i.get("fiftyDayAverage"),
            "200d_avg": i.get("twoHundredDayAverage"),
            "timestamp": datetime.now().isoformat(),
        }

    def get_historical_prices(
        self, period: str = "1y", interval: str = "1d"
    ) -> list[dict]:
        """
        Historical price data.
        period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
        interval: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
        """
        df = self.stock.history(period=period, interval=interval)
        if df.empty:
            return []
        df = df.reset_index()
        records = []
        for _, row in df.iterrows():
            date_val = row.get("Date") or row.get("Datetime")
            records.append(
                {
                    "date": str(date_val),
                    "open": round(row["Open"], 2),
                    "high": round(row["High"], 2),
                    "low": round(row["Low"], 2),
                    "close": round(row["Close"], 2),
                    "volume": int(row["Volume"]),
                }
            )
        return records

    # ── Key Statistics ────────────────────────────────────────────────

    def get_key_stats(self) -> dict:
        """Key financial statistics and ratios."""
        i = self.info
        return {
            "ticker": self.ticker,
            "market_cap": i.get("marketCap"),
            "enterprise_value": i.get("enterpriseValue"),
            "trailing_pe": i.get("trailingPE"),
            "forward_pe": i.get("forwardPE"),
            "peg_ratio": i.get("pegRatio"),
            "price_to_book": i.get("priceToBook"),
            "price_to_sales": i.get("priceToSalesTrailing12Months"),
            "ev_to_revenue": i.get("enterpriseToRevenue"),
            "ev_to_ebitda": i.get("enterpriseToEbitda"),
            "profit_margin": i.get("profitMargins"),
            "operating_margin": i.get("operatingMargins"),
            "gross_margin": i.get("grossMargins"),
            "ebitda_margin": (
                i.get("ebitda") / i.get("totalRevenue")
                if i.get("ebitda") and i.get("totalRevenue")
                else None
            ),
            "return_on_equity": i.get("returnOnEquity"),
            "return_on_assets": i.get("returnOnAssets"),
            "revenue_growth": i.get("revenueGrowth"),
            "earnings_growth": i.get("earningsGrowth"),
            "beta": i.get("beta"),
            "dividend_yield": i.get("dividendYield"),
            "payout_ratio": i.get("payoutRatio"),
            "debt_to_equity": i.get("debtToEquity"),
            "current_ratio": i.get("currentRatio"),
            "quick_ratio": i.get("quickRatio"),
            "free_cash_flow": i.get("freeCashflow"),
            "operating_cash_flow": i.get("operatingCashflow"),
            "total_revenue": i.get("totalRevenue"),
            "ebitda": i.get("ebitda"),
            "net_income": i.get("netIncomeToCommon"),
            "total_debt": i.get("totalDebt"),
            "total_cash": i.get("totalCash"),
            "shares_outstanding": i.get("sharesOutstanding"),
            "float_shares": i.get("floatShares"),
        }

    # ── Financial Statements ──────────────────────────────────────────

    def get_financials(self, quarterly: bool = False) -> dict:
        """Income statement, balance sheet, and cash flow."""
        if quarterly:
            income = self.stock.quarterly_income_stmt
            balance = self.stock.quarterly_balance_sheet
            cashflow = self.stock.quarterly_cashflow
        else:
            income = self.stock.income_stmt
            balance = self.stock.balance_sheet
            cashflow = self.stock.cashflow

        def df_to_dict(df):
            if df is None or df.empty:
                return {}
            result = {}
            for col in df.columns:
                col_key = str(col)
                result[col_key] = {}
                for idx, val in df[col].items():
                    result[col_key][str(idx)] = (
                        None if val != val else val  # handle NaN
                    )
            return result

        return {
            "ticker": self.ticker,
            "period": "quarterly" if quarterly else "annual",
            "income_statement": df_to_dict(income),
            "balance_sheet": df_to_dict(balance),
            "cash_flow": df_to_dict(cashflow),
        }

    def get_income_statement(self, quarterly: bool = False) -> dict:
        """Income statement only, as a clean dict."""
        df = (
            self.stock.quarterly_income_stmt
            if quarterly
            else self.stock.income_stmt
        )
        if df is None or df.empty:
            return {}
        result = {}
        for col in df.columns:
            period_key = col.strftime("%Y-%m-%d") if hasattr(col, "strftime") else str(col)
            result[period_key] = {}
            for idx, val in df[col].items():
                result[period_key][str(idx)] = None if val != val else float(val)
        return result

    def get_balance_sheet(self, quarterly: bool = False) -> dict:
        """Balance sheet only."""
        df = (
            self.stock.quarterly_balance_sheet
            if quarterly
            else self.stock.balance_sheet
        )
        if df is None or df.empty:
            return {}
        result = {}
        for col in df.columns:
            period_key = col.strftime("%Y-%m-%d") if hasattr(col, "strftime") else str(col)
            result[period_key] = {}
            for idx, val in df[col].items():
                result[period_key][str(idx)] = None if val != val else float(val)
        return result

    def get_cash_flow(self, quarterly: bool = False) -> dict:
        """Cash flow statement only."""
        df = (
            self.stock.quarterly_cashflow
            if quarterly
            else self.stock.cashflow
        )
        if df is None or df.empty:
            return {}
        result = {}
        for col in df.columns:
            period_key = col.strftime("%Y-%m-%d") if hasattr(col, "strftime") else str(col)
            result[period_key] = {}
            for idx, val in df[col].items():
                result[period_key][str(idx)] = None if val != val else float(val)
        return result

    # ── Earnings ──────────────────────────────────────────────────────

    def get_earnings_dates(self) -> list[dict]:
        """Upcoming and recent earnings dates."""
        try:
            df = self.stock.earnings_dates
            if df is None or df.empty:
                return []
            records = []
            df = df.reset_index()
            for _, row in df.iterrows():
                records.append(
                    {
                        "date": str(row.get("Earnings Date", "")),
                        "eps_estimate": row.get("EPS Estimate"),
                        "reported_eps": row.get("Reported EPS"),
                        "surprise_pct": row.get("Surprise(%)"),
                    }
                )
            return records
        except Exception:
            return []

    def get_earnings_history(self) -> list[dict]:
        """Historical earnings with beat/miss data."""
        try:
            df = self.stock.earnings_history
            if df is None or df.empty:
                return []
            return df.to_dict("records")
        except Exception:
            return []

    # ── Analyst Data ──────────────────────────────────────────────────

    def get_analyst_recommendations(self) -> list[dict]:
        """Recent analyst recommendations."""
        try:
            df = self.stock.recommendations
            if df is None or df.empty:
                return []
            df = df.reset_index()
            records = []
            for _, row in df.tail(20).iterrows():
                records.append(
                    {
                        "date": str(row.get("Date", row.get("index", ""))),
                        "firm": row.get("Firm", ""),
                        "to_grade": row.get("To Grade", ""),
                        "from_grade": row.get("From Grade", ""),
                        "action": row.get("Action", ""),
                    }
                )
            return records
        except Exception:
            return []

    def get_analyst_price_targets(self) -> dict:
        """Analyst price target summary."""
        i = self.info
        return {
            "ticker": self.ticker,
            "target_high": i.get("targetHighPrice"),
            "target_low": i.get("targetLowPrice"),
            "target_mean": i.get("targetMeanPrice"),
            "target_median": i.get("targetMedianPrice"),
            "num_analysts": i.get("numberOfAnalystOpinions"),
            "recommendation": i.get("recommendationKey"),
            "recommendation_mean": i.get("recommendationMean"),
        }

    # ── Peer Comparison ───────────────────────────────────────────────

    def get_peers(self) -> list[str]:
        """Get list of peer/comparable tickers from Yahoo Finance."""
        try:
            # yfinance doesn't have a direct peers attribute in all versions
            # Fall back to sector-based approach
            sector = self.info.get("sector", "")
            industry = self.info.get("industry", "")
            return {
                "ticker": self.ticker,
                "sector": sector,
                "industry": industry,
                "note": "Use screener to find peers in same sector/industry",
            }
        except Exception:
            return {"ticker": self.ticker, "peers": []}

    # ── Dividends & Splits ────────────────────────────────────────────

    def get_dividends(self) -> list[dict]:
        """Dividend history."""
        divs = self.stock.dividends
        if divs is None or divs.empty:
            return []
        records = []
        for date, amount in divs.items():
            records.append({"date": str(date), "dividend": round(float(amount), 4)})
        return records

    def get_splits(self) -> list[dict]:
        """Stock split history."""
        splits = self.stock.splits
        if splits is None or splits.empty:
            return []
        records = []
        for date, ratio in splits.items():
            records.append({"date": str(date), "ratio": float(ratio)})
        return records

    # ── Screening Helper ──────────────────────────────────────────────

    @staticmethod
    def screen_stocks(tickers: list[str]) -> list[dict]:
        """
        Screen multiple stocks and return key metrics for comparison.
        Useful for building stock screening tables.
        """
        results = []
        for ticker in tickers:
            try:
                stock = StockData(ticker)
                i = stock.info
                results.append(
                    {
                        "ticker": ticker,
                        "name": i.get("longName", ""),
                        "sector": i.get("sector", ""),
                        "industry": i.get("industry", ""),
                        "market_cap": i.get("marketCap"),
                        "price": i.get("currentPrice") or i.get("regularMarketPrice"),
                        "pe_ratio": i.get("trailingPE"),
                        "forward_pe": i.get("forwardPE"),
                        "peg_ratio": i.get("pegRatio"),
                        "price_to_book": i.get("priceToBook"),
                        "ev_to_ebitda": i.get("enterpriseToEbitda"),
                        "profit_margin": i.get("profitMargins"),
                        "operating_margin": i.get("operatingMargins"),
                        "roe": i.get("returnOnEquity"),
                        "revenue_growth": i.get("revenueGrowth"),
                        "earnings_growth": i.get("earningsGrowth"),
                        "dividend_yield": i.get("dividendYield"),
                        "beta": i.get("beta"),
                        "debt_to_equity": i.get("debtToEquity"),
                        "current_ratio": i.get("currentRatio"),
                        "52w_high": i.get("fiftyTwoWeekHigh"),
                        "52w_low": i.get("fiftyTwoWeekLow"),
                        "52w_change": (
                            (
                                (i.get("currentPrice") or i.get("regularMarketPrice", 0))
                                - i.get("fiftyTwoWeekLow", 0)
                            )
                            / i.get("fiftyTwoWeekLow", 1)
                            if i.get("fiftyTwoWeekLow")
                            else None
                        ),
                    }
                )
            except Exception as e:
                results.append({"ticker": ticker, "error": str(e)})
        return results

    # ── Bulk Export ────────────────────────────────────────────────────

    def get_full_profile(self) -> dict:
        """Complete data dump for a single stock."""
        return {
            "overview": self.get_company_overview(),
            "price": self.get_current_price(),
            "key_stats": self.get_key_stats(),
            "analyst_targets": self.get_analyst_price_targets(),
            "financials_annual": self.get_financials(quarterly=False),
            "financials_quarterly": self.get_financials(quarterly=True),
            "earnings_dates": self.get_earnings_dates(),
        }


# ── CLI Interface ─────────────────────────────────────────────────────

def format_number(val, is_pct: bool = False, is_money: bool = False) -> str:
    """Format numbers for display."""
    if val is None:
        return "N/A"
    if is_pct:
        return f"{val * 100:.1f}%"
    if is_money:
        if abs(val) >= 1e12:
            return f"${val / 1e12:.1f}T"
        if abs(val) >= 1e9:
            return f"${val / 1e9:.1f}B"
        if abs(val) >= 1e6:
            return f"${val / 1e6:.1f}M"
        return f"${val:,.0f}"
    if isinstance(val, float):
        return f"{val:.2f}"
    return str(val)


def print_summary(ticker: str):
    """Print a quick summary for a ticker."""
    stock = StockData(ticker)
    overview = stock.get_company_overview()
    price = stock.get_current_price()
    stats = stock.get_key_stats()

    print(f"\n{'=' * 60}")
    print(f"  {overview['name']} ({ticker})")
    print(f"  {overview['sector']} | {overview['industry']}")
    print(f"{'=' * 60}")
    print(f"  Price:        {format_number(price['price'], is_money=True)}")
    print(f"  Market Cap:   {format_number(stats['market_cap'], is_money=True)}")
    print(f"  EV:           {format_number(stats['enterprise_value'], is_money=True)}")
    print(f"  P/E (TTM):    {format_number(stats['trailing_pe'])}")
    print(f"  P/E (Fwd):    {format_number(stats['forward_pe'])}")
    print(f"  EV/EBITDA:    {format_number(stats['ev_to_ebitda'])}")
    print(f"  P/B:          {format_number(stats['price_to_book'])}")
    print(f"  Beta:         {format_number(stats['beta'])}")
    print(f"  ---")
    print(f"  Rev Growth:   {format_number(stats['revenue_growth'], is_pct=True)}")
    print(f"  Gross Margin: {format_number(stats['gross_margin'], is_pct=True)}")
    print(f"  Op Margin:    {format_number(stats['operating_margin'], is_pct=True)}")
    print(f"  Net Margin:   {format_number(stats['profit_margin'], is_pct=True)}")
    print(f"  ROE:          {format_number(stats['return_on_equity'], is_pct=True)}")
    print(f"  D/E:          {format_number(stats['debt_to_equity'])}")
    print(f"  Div Yield:    {format_number(stats['dividend_yield'], is_pct=True)}")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python yahoo_finance.py <TICKER> [--json] [--financials] [--screen TICK1,TICK2,...]")
        sys.exit(1)

    ticker_arg = sys.argv[1].upper()

    if "--json" in sys.argv:
        stock = StockData(ticker_arg)
        print(json.dumps(stock.get_full_profile(), indent=2, default=str))
    elif "--financials" in sys.argv:
        stock = StockData(ticker_arg)
        print(json.dumps(stock.get_financials(), indent=2, default=str))
    elif "--screen" in sys.argv:
        idx = sys.argv.index("--screen")
        if idx + 1 < len(sys.argv):
            tickers = sys.argv[idx + 1].split(",")
        else:
            tickers = [ticker_arg]
        results = StockData.screen_stocks(tickers)
        print(json.dumps(results, indent=2, default=str))
    else:
        print_summary(ticker_arg)
