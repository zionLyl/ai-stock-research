#!/usr/bin/env python3
"""
A股数据层 — Sina Finance + Tencent Quotes
替代 AKShare（被东方财富封海外IP）

数据源优先级:
1. Sina Finance API — 全量A股列表、行情、K线、基本面
2. Tencent Quotes API — 实时行情兜底、PE/PB/市值
3. MCP 搜索 — 新闻、政策、事件

用法:
    from cn_data import CNStockData, CNMarketData, CNBatchData
    stock = CNStockData("600519")
    quote = stock.get_quote()
    kline = stock.get_kline(n=60)

CLI:
    python cn_data.py 600519                # 单股概览
    python cn_data.py 600519 --json         # JSON输出
    python cn_data.py --market-snapshot      # 市场快照
"""

import json
import re
import sys
import time
import urllib.request
from datetime import datetime, timedelta
from typing import Optional


# ---------------------------------------------------------------------------
# Utils
# ---------------------------------------------------------------------------

def _http_get(url: str, timeout: int = 10, encoding: str = "utf-8",
              headers: Optional[dict] = None, retries: int = 2) -> str:
    """HTTP GET with retry."""
    hdrs = {"User-Agent": "Mozilla/5.0 (compatible; CNStock/1.0)"}
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(url, headers=hdrs)
    for attempt in range(retries + 1):
        try:
            resp = urllib.request.urlopen(req, timeout=timeout)
            raw = resp.read()
            # 尝试 GBK 解码（Sina/Tencent 默认 GBK）
            for enc in [encoding, "gbk", "gb2312", "utf-8"]:
                try:
                    return raw.decode(enc)
                except (UnicodeDecodeError, LookupError):
                    continue
            return raw.decode("utf-8", errors="replace")
        except Exception as e:
            if attempt < retries:
                time.sleep(0.5 * (attempt + 1))
                continue
            raise
    return ""


def _safe_float(val) -> Optional[float]:
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip().replace(",", "").replace("%", "")
    if s in ("", "-", "None", "null", "N/A", "--", "nan", "0.000"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _market_prefix(code: str) -> str:
    """返回 'sh' 或 'sz'（新浪/腾讯格式）"""
    c = str(code).strip()
    if c.startswith(("6", "5", "9", "11")):
        return "sh"
    return "sz"


def _board_type(code: str) -> str:
    """判断板块类型"""
    c = str(code).strip()
    if c.startswith("688"):
        return "科创板"
    elif c.startswith(("300", "301")):
        return "创业板"
    elif c.startswith(("8", "4")):
        return "北交所"
    else:
        return "主板"


def _price_limit(code: str) -> float:
    """涨跌停幅度"""
    board = _board_type(code)
    limits = {"科创板": 0.20, "创业板": 0.10, "北交所": 0.30, "主板": 0.10}
    return limits.get(board, 0.10)


# ---------------------------------------------------------------------------
# Sina Finance API
# ---------------------------------------------------------------------------

class SinaAPI:
    """新浪财经 API 封装"""

    BASE = "http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php"
    HQ_BASE = "http://hq.sinajs.cn"
    KLINE_BASE = "https://quotes.sina.cn/cn/api/jsonp_v2.php"

    @staticmethod
    def get_stock_list(page: int = 1, num: int = 80, sort: str = "mktcap",
                       asc: int = 0) -> list:
        """
        获取全量A股列表（分页）
        返回: [{code, name, trade, per, pb, mktcap, changepercent, volume, amount, turnoverratio}, ...]
        """
        url = (f"{SinaAPI.BASE}/Market_Center.getHQNodeData?"
               f"page={page}&num={num}&sort={sort}&asc={asc}&node=hs_a")
        text = _http_get(url)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return []

    @staticmethod
    def get_total_count() -> int:
        """A股总数"""
        url = f"{SinaAPI.BASE}/Market_Center.getHQNodeStockCount?node=hs_a"
        text = _http_get(url).strip().strip('"')
        return int(text) if text.isdigit() else 0

    @staticmethod
    def get_realtime_quotes(symbols: list) -> dict:
        """
        批量实时行情（Sina hq API）
        symbols: ["600519", "000858"]
        返回: {code: {name, price, open, high, low, volume, amount, prev_close, ...}}
        """
        if not symbols:
            return {}
        codes = [f"{_market_prefix(s)}{s}" for s in symbols]
        # Sina 限制每次50个
        result = {}
        for i in range(0, len(codes), 50):
            batch = codes[i:i+50]
            url = f"{SinaAPI.HQ_BASE}/list={','.join(batch)}"
            text = _http_get(url, headers={"Referer": "https://finance.sina.com.cn"})
            for line in text.strip().split("\n"):
                line = line.strip()
                if not line or "=" not in line:
                    continue
                match = re.match(r'var hq_str_(\w+)="(.+)"', line)
                if not match:
                    continue
                sina_code = match.group(1)
                fields = match.group(2).split(",")
                if len(fields) < 32:
                    continue
                code = sina_code[2:]  # strip sh/sz
                result[code] = {
                    "name": fields[0],
                    "open": _safe_float(fields[1]),
                    "prev_close": _safe_float(fields[2]),
                    "price": _safe_float(fields[3]),
                    "high": _safe_float(fields[4]),
                    "low": _safe_float(fields[5]),
                    "volume": _safe_float(fields[8]),   # 手
                    "amount": _safe_float(fields[9]),    # 元
                    "date": fields[30] if len(fields) > 30 else "",
                    "time": fields[31] if len(fields) > 31 else "",
                    "source": "sina",
                }
        return result

    @staticmethod
    def get_kline(symbol: str, scale: int = 240, datalen: int = 120) -> list:
        """
        K线数据
        scale: 5/15/30/60/240(日)/1680(周)
        datalen: 返回条数
        返回: [{day, open, high, low, close, volume}, ...]
        """
        sina_code = f"{_market_prefix(symbol)}{symbol}"
        cb = f"var%20_{sina_code}="
        url = (f"{SinaAPI.KLINE_BASE}/{cb}/CN_MarketDataService.getKLineData?"
               f"symbol={sina_code}&scale={scale}&ma=no&datalen={datalen}")
        text = _http_get(url)
        # 解析 JSONP: var _shXXXXXX=([...]);
        match = re.search(r'\((\[.+\])\)', text, re.DOTALL)
        if not match:
            return []
        try:
            data = json.loads(match.group(1))
            return [{
                "date": d.get("day", ""),
                "open": _safe_float(d.get("open")),
                "high": _safe_float(d.get("high")),
                "low": _safe_float(d.get("low")),
                "close": _safe_float(d.get("close")),
                "volume": _safe_float(d.get("volume")),
            } for d in data]
        except json.JSONDecodeError:
            return []


# ---------------------------------------------------------------------------
# Tencent Quotes API
# ---------------------------------------------------------------------------

class TencentAPI:
    """腾讯行情 API 封装（兜底数据源）"""

    BASE = "http://qt.gtimg.cn/q="

    @staticmethod
    def get_quotes(symbols: list) -> dict:
        """
        批量行情
        返回: {code: {name, price, change_pct, pe, pb, market_cap, volume, amount, ...}}
        """
        if not symbols:
            return {}
        result = {}
        # 腾讯每次也限制一定数量
        for i in range(0, len(symbols), 50):
            batch = symbols[i:i+50]
            codes = [f"{_market_prefix(s)}{s}" for s in batch]
            url = f"{TencentAPI.BASE}{','.join(codes)}"
            text = _http_get(url, encoding="gbk")
            for line in text.strip().split("\n"):
                line = line.strip().rstrip(";")
                if not line or "~" not in line:
                    continue
                # v_sh600519="1~贵州茅台~600519~1455.02~1466.21~..."
                match = re.match(r'v_\w+="(.+)"', line)
                if not match:
                    continue
                fields = match.group(1).split("~")
                if len(fields) < 50:
                    continue
                code = fields[2]
                result[code] = {
                    "name": fields[1],
                    "price": _safe_float(fields[3]),
                    "prev_close": _safe_float(fields[4]),
                    "open": _safe_float(fields[5]),
                    "volume": _safe_float(fields[6]),   # 手
                    "amount": _safe_float(fields[37]),   # 万元
                    "high": _safe_float(fields[33]) if len(fields) > 47 else _safe_float(fields[41]),
                    "low": _safe_float(fields[34]) if len(fields) > 47 else _safe_float(fields[42]),
                    "change_pct": _safe_float(fields[32]),
                    "pe": _safe_float(fields[39]),
                    "pb": _safe_float(fields[46]) if len(fields) > 46 else None,
                    "market_cap": _safe_float(fields[45]),  # 亿
                    "float_market_cap": _safe_float(fields[44]) if len(fields) > 44 else None,
                    "turnover_rate": _safe_float(fields[38]),
                    "amplitude": _safe_float(fields[43]) if len(fields) > 43 else None,
                    "source": "tencent",
                }
        return result

    @staticmethod
    def get_index_quotes(codes: list = None) -> dict:
        """
        指数行情
        默认: 上证指数/沪深300/中证500/创业板指
        """
        if codes is None:
            codes = ["sh000001", "sh000300", "sh000905", "sz399006"]
        url = f"{TencentAPI.BASE}{','.join(codes)}"
        text = _http_get(url, encoding="gbk")
        result = {}
        name_map = {
            "000001": "上证指数", "000300": "沪深300",
            "000905": "中证500", "399006": "创业板指",
        }
        for line in text.strip().split("\n"):
            line = line.strip().rstrip(";")
            match = re.match(r'v_\w+="(.+)"', line)
            if not match:
                continue
            fields = match.group(1).split("~")
            if len(fields) < 35:
                continue
            code = fields[2]
            result[name_map.get(code, fields[1])] = {
                "code": code,
                "name": fields[1],
                "price": _safe_float(fields[3]),
                "change_pct": _safe_float(fields[32]),
                "volume": _safe_float(fields[6]),
                "amount": _safe_float(fields[37]),
                "source": "tencent",
            }
        return result


# ---------------------------------------------------------------------------
# High-level Data Classes
# ---------------------------------------------------------------------------

class CNStockData:
    """单只A股数据"""

    def __init__(self, symbol: str):
        self.symbol = str(symbol).strip()
        self.prefix = _market_prefix(self.symbol)
        self.board = _board_type(self.symbol)
        self._sina_quote = None
        self._tencent_quote = None

    def get_quote(self) -> dict:
        """获取实时行情（Tencent 优先，含 PE/PB/市值）"""
        tq = TencentAPI.get_quotes([self.symbol]).get(self.symbol, {})
        if tq and tq.get("price"):
            self._tencent_quote = tq
            return tq
        # fallback to Sina
        sq = SinaAPI.get_realtime_quotes([self.symbol]).get(self.symbol, {})
        self._sina_quote = sq
        return sq

    def get_kline(self, period: str = "daily", n: int = 120) -> list:
        """
        K线数据
        period: daily/weekly
        n: 条数
        """
        scale = {"daily": 240, "weekly": 1680, "60min": 60, "30min": 30}.get(period, 240)
        return SinaAPI.get_kline(self.symbol, scale=scale, datalen=n)

    def get_technical_indicators(self, n: int = 120) -> dict:
        """从K线计算技术指标: MA5/20/60, RSI14, MACD"""
        kline = self.get_kline(n=n)
        if not kline or len(kline) < 20:
            return {}

        closes = [k["close"] for k in kline if k.get("close") is not None]
        if len(closes) < 20:
            return {}

        result = {
            "latest": closes[-1],
            "ma5": round(sum(closes[-5:]) / len(closes[-5:]), 3),
            "ma20": round(sum(closes[-20:]) / len(closes[-20:]), 3),
        }

        if len(closes) >= 60:
            result["ma60"] = round(sum(closes[-60:]) / len(closes[-60:]), 3)

        # RSI(14)
        if len(closes) >= 15:
            gains, losses = [], []
            for i in range(-14, 0):
                diff = closes[i] - closes[i - 1]
                gains.append(max(diff, 0))
                losses.append(max(-diff, 0))
            avg_gain = sum(gains) / 14
            avg_loss = sum(losses) / 14
            if avg_loss > 0:
                rs = avg_gain / avg_loss
                result["rsi14"] = round(100 - (100 / (1 + rs)), 2)
            else:
                result["rsi14"] = 100.0

        # 相对MA20百分比
        if result.get("ma20"):
            result["vs_ma20_pct"] = round((closes[-1] - result["ma20"]) / result["ma20"] * 100, 2)
        if result.get("ma60"):
            result["vs_ma60_pct"] = round((closes[-1] - result["ma60"]) / result["ma60"] * 100, 2)

        # 120日高低点
        result["high_period"] = max(closes)
        result["low_period"] = min(closes)
        result["off_high_pct"] = round((closes[-1] - max(closes)) / max(closes) * 100, 2)

        return result

    def get_overview(self) -> dict:
        """综合概览"""
        quote = self.get_quote()
        tech = self.get_technical_indicators()
        return {
            "symbol": self.symbol,
            "board": self.board,
            "quote": quote,
            "technical": tech,
        }


class CNMarketData:
    """市场级别数据"""

    @staticmethod
    def get_indices() -> dict:
        """主要指数行情"""
        return TencentAPI.get_index_quotes()

    @staticmethod
    def get_market_snapshot() -> dict:
        """市场快照: 指数 + 简单统计"""
        indices = TencentAPI.get_index_quotes()
        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "indices": indices,
        }

    @staticmethod
    def get_sector_rotation(page: int = 1, num: int = 30) -> list:
        """
        行业板块涨跌排名（Sina API）
        返回: [{name, change_pct, volume, amount, leading_stock, ...}]
        """
        url = (f"{SinaAPI.BASE}/Market_Center.getHQNodeData?"
               f"page={page}&num={num}&sort=changepercent&asc=0&node=hangye_block")
        text = _http_get(url)
        try:
            data = json.loads(text)
            return [{
                "name": d.get("name", ""),
                "symbol": d.get("symbol", ""),
                "change_pct": _safe_float(d.get("changepercent")),
                "trade": _safe_float(d.get("trade")),
                "volume": _safe_float(d.get("volume")),
                "amount": _safe_float(d.get("amount")),
                "source": "sina",
            } for d in data]
        except (json.JSONDecodeError, TypeError):
            return []

    @staticmethod
    def get_concept_sectors(page: int = 1, num: int = 30) -> list:
        """
        概念板块涨跌排名
        """
        url = (f"{SinaAPI.BASE}/Market_Center.getHQNodeData?"
               f"page={page}&num={num}&sort=changepercent&asc=0&node=gainian_block")
        text = _http_get(url)
        try:
            data = json.loads(text)
            return [{
                "name": d.get("name", ""),
                "change_pct": _safe_float(d.get("changepercent")),
                "trade": _safe_float(d.get("trade")),
                "source": "sina",
            } for d in data]
        except (json.JSONDecodeError, TypeError):
            return []


class CNBatchData:
    """批量操作 — 用于全市场筛选"""

    @staticmethod
    def get_all_a_shares(sort: str = "mktcap", max_pages: int = 80) -> list:
        """
        获取全量A股（分页遍历 Sina API）
        每页80只，约70页 ≈ 5500只
        返回: [{code, name, trade, per, pb, mktcap, changepercent, volume, amount, turnoverratio}]
        """
        total = SinaAPI.get_total_count()
        if total <= 0:
            total = 5500  # fallback
        per_page = 80
        pages = min((total + per_page - 1) // per_page, max_pages)
        all_stocks = []

        for page in range(1, pages + 1):
            data = SinaAPI.get_stock_list(page=page, num=per_page, sort=sort)
            if not data:
                break
            all_stocks.extend(data)
            if len(data) < per_page:
                break
            # 避免请求太快
            if page % 10 == 0:
                time.sleep(0.3)

        return all_stocks

    @staticmethod
    def get_batch_quotes(symbols: list) -> dict:
        """批量行情（Tencent，含 PE/PB/市值）"""
        return TencentAPI.get_quotes(symbols)

    @staticmethod
    def get_batch_quotes_sina(symbols: list) -> dict:
        """批量行情（Sina，含 OHLCV）"""
        return SinaAPI.get_realtime_quotes(symbols)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _print_stock_overview(symbol: str, as_json: bool = False):
    stock = CNStockData(symbol)
    overview = stock.get_overview()
    if as_json:
        print(json.dumps(overview, indent=2, ensure_ascii=False))
        return

    q = overview.get("quote", {})
    t = overview.get("technical", {})
    name = q.get("name", "?")
    price = q.get("price", "?")
    change = q.get("change_pct", "?")
    pe = q.get("pe", "?")
    pb = q.get("pb", "?")
    mktcap = q.get("market_cap", "?")

    print(f"📊 {name} ({symbol}) [{overview['board']}]")
    print(f"   价格: {price}  涨跌: {change}%  PE: {pe}  PB: {pb}  市值: {mktcap}亿")
    if t:
        print(f"   MA5: {t.get('ma5','-')}  MA20: {t.get('ma20','-')}  MA60: {t.get('ma60','-')}")
        print(f"   RSI14: {t.get('rsi14','-')}  vs MA20: {t.get('vs_ma20_pct','-')}%  距高点: {t.get('off_high_pct','-')}%")


def _print_market_snapshot():
    snap = CNMarketData.get_market_snapshot()
    print(f"📈 A股市场快照 ({snap['timestamp']})")
    for name, idx in snap.get("indices", {}).items():
        print(f"   {name}: {idx.get('price', '?')} ({idx.get('change_pct', '?')}%)")


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--market-snapshot" in args:
        _print_market_snapshot()
    elif "--sector" in args:
        sectors = CNMarketData.get_sector_rotation()
        for s in sectors[:20]:
            print(f"  {s['name']:<10} {s.get('change_pct', '?'):>6}%")
    elif args:
        symbol = args[0]
        as_json = "--json" in args
        _print_stock_overview(symbol, as_json=as_json)
    else:
        print("用法: python cn_data.py 600519 [--json] | --market-snapshot | --sector")
