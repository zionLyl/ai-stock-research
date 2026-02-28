#!/usr/bin/env python3
"""
XTP 交易层 (中泰证券模拟盘)
通过 subprocess 隔离调用，避免 XTP 回调死锁

关键规则:
- XTP_MARKET_TYPE: SZ_A=1, SH_A=2 (注意! 和交易所代码相反)
- XTP_EXCHANGE_TYPE: SH=1, SZ=2
- 主板单笔 ≤999,900 股, 科创板(688) ≤99,900 股
- T+1: 当天买入不能当天卖出

用法:
    python xtp_trader.py account        # 查询资金
    python xtp_trader.py positions      # 查询持仓
    python xtp_trader.py buy 600519 100 1500.00  # 限价买入
    python xtp_trader.py sell 600519 100          # 市价卖出
"""

import json
import os
import subprocess
import sys
import tempfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# XTP 凭证从环境变量读取
XTP_PASSWORD = os.environ.get("XTP_PASSWORD", "")
XTP_KEY = os.environ.get("XTP_KEY", "")

# 从 config.json 读取 XTP 配置
def _load_xtp_config() -> dict:
    config_path = os.path.join(SCRIPT_DIR, "config.json")
    try:
        with open(config_path) as f:
            cfg = json.load(f)
        return cfg.get("xtp", {})
    except FileNotFoundError:
        return {}


def _xtp_market(symbol: str) -> int:
    """XTP_MARKET_TYPE: SZ_A=1, SH_A=2 (和直觉相反!)"""
    if str(symbol).startswith(("6", "5", "9", "11")):
        return 2  # SH_A
    return 1  # SZ_A


def _max_order_qty(symbol: str) -> int:
    """单笔最大数量"""
    if str(symbol).startswith("688"):
        return 99900   # 科创板
    return 999900      # 主板/创业板


def _run_xtp_subprocess(script_content: str, timeout: int = 15) -> dict:
    """
    在独立子进程中执行 XTP 操作
    XTP 回调在嵌入式调用中会死锁，必须 subprocess 隔离
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(script_content)
        f.flush()
        script_path = f.name

    try:
        env = os.environ.copy()
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True, text=True, timeout=timeout, env=env
        )
        output = result.stdout.strip()
        if output:
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                return {"raw_output": output, "error": result.stderr.strip()}
        return {"error": result.stderr.strip() or "no output"}
    except subprocess.TimeoutExpired:
        return {"error": "XTP subprocess timeout"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        try:
            os.unlink(script_path)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_account() -> dict:
    """查询账户资金"""
    cfg = _load_xtp_config()
    account = cfg.get("account", "YOUR_XTP_ACCOUNT")
    server = cfg.get("trade_server", "122.112.139.0")
    port = cfg.get("trade_port", 6104)

    script = f'''
import json, os, threading
from xtpwrapper import TraderApi

class T(TraderApi):
    def __init__(self):
        super().__init__()
        self._result = {{}}
        self._done = threading.Event()
    def OnQueryAsset(self, asset, err, rid, is_last, sid):
        if asset:
            self._result = {{
                "total_asset": asset.total_asset,
                "buying_power": asset.buying_power,
                "security_asset": asset.security_asset,
            }}
        if is_last:
            self._done.set()

os.makedirs("/tmp/xtp_t", exist_ok=True)
t = T()
t.CreateTrader(1, "/tmp/xtp_t/", 18)
t.SetSoftwareKey("{XTP_KEY}")
sid = t.Login("{server}", {port}, "{account}", "{XTP_PASSWORD}")
if sid == 0:
    e = t.GetApiLastError()
    print(json.dumps({{"error": f"login failed: {{e.error_id}} {{e.error_msg}}"}}))
else:
    t._done.clear()
    t.QueryAsset(sid, 0)
    t._done.wait(timeout=5)
    print(json.dumps(t._result))
    t.Logout(sid)
t.Release()
'''
    return _run_xtp_subprocess(script)


def get_positions() -> list:
    """查询持仓"""
    cfg = _load_xtp_config()
    account = cfg.get("account", "YOUR_XTP_ACCOUNT")
    server = cfg.get("trade_server", "122.112.139.0")
    port = cfg.get("trade_port", 6104)

    script = f'''
import json, os, threading
from xtpwrapper import TraderApi

class T(TraderApi):
    def __init__(self):
        super().__init__()
        self._positions = []
        self._done = threading.Event()
    def OnQueryPosition(self, pos, err, rid, is_last, sid):
        if pos and pos.ticker:
            tk = pos.ticker
            if isinstance(tk, bytes): tk = tk.decode()
            nm = pos.ticker_name
            if isinstance(nm, bytes): nm = nm.decode()
            self._positions.append({{
                "ticker": tk, "name": nm,
                "total_qty": pos.total_qty,
                "sellable_qty": pos.sellable_qty,
                "avg_price": pos.avg_price,
                "unrealized_pnl": pos.unrealized_pnl,
                "market": pos.market,
            }})
        if is_last:
            self._done.set()

os.makedirs("/tmp/xtp_t", exist_ok=True)
t = T()
t.CreateTrader(1, "/tmp/xtp_t/", 18)
t.SetSoftwareKey("{XTP_KEY}")
sid = t.Login("{server}", {port}, "{account}", "{XTP_PASSWORD}")
if sid == 0:
    e = t.GetApiLastError()
    print(json.dumps([{{"error": f"login failed: {{e.error_id}} {{e.error_msg}}"}}]))
else:
    t._done.clear()
    t._positions = []
    t.QueryPosition("", sid, 0)
    t._done.wait(timeout=5)
    print(json.dumps(t._positions, ensure_ascii=False))
    t.Logout(sid)
t.Release()
'''
    return _run_xtp_subprocess(script)


def place_order(symbol: str, side: str, quantity: int, price: float = None) -> dict:
    """
    下单
    side: "buy" / "sell"
    price: None = 最优五档, 有值 = 限价
    会自动拆单（超过单笔限制时）
    """
    market = _xtp_market(symbol)
    max_qty = _max_order_qty(symbol)

    if quantity > max_qty:
        # 拆单
        results = []
        remaining = quantity
        while remaining > 0:
            batch = min(remaining, max_qty)
            r = _place_single_order(symbol, side, batch, price, market)
            results.append(r)
            remaining -= batch
        return {"split_orders": results, "total_qty": quantity}

    return _place_single_order(symbol, side, quantity, price, market)


def _place_single_order(symbol: str, side: str, quantity: int,
                        price: float, market: int) -> dict:
    cfg = _load_xtp_config()
    account = cfg.get("account", "YOUR_XTP_ACCOUNT")
    server = cfg.get("trade_server", "122.112.139.0")
    port = cfg.get("trade_port", 6104)

    side_code = 1 if side == "buy" else 2
    price_type = 1 if price else 5  # LIMIT=1, BEST5_OR_CANCEL=5
    price_val = price or 0

    script = f'''
import json, os
from xtpwrapper import TraderApi

os.makedirs("/tmp/xtp_t", exist_ok=True)
t = TraderApi()
t.CreateTrader(1, "/tmp/xtp_t/", 18)
t.SetSoftwareKey("{XTP_KEY}")
sid = t.Login("{server}", {port}, "{account}", "{XTP_PASSWORD}")
if sid == 0:
    e = t.GetApiLastError()
    print(json.dumps({{"error": f"login: {{e.error_id}} {{e.error_msg}}"}}))
else:
    order = {{
        "ticker": "{symbol}", "market": {market},
        "quantity": {quantity}, "side": {side_code},
        "price_type": {price_type}, "price": {price_val},
        "business_type": 0,
    }}
    oid = t.InsertOrder(order, sid)
    if oid == 0:
        e = t.GetApiLastError()
        print(json.dumps({{"error": f"order: {{e.error_id}} {{e.error_msg}}", "symbol": "{symbol}"}}))
    else:
        print(json.dumps({{"order_id": oid, "symbol": "{symbol}", "side": "{side}", "qty": {quantity}, "price": {price_val}}}))
    t.Logout(sid)
t.Release()
'''
    return _run_xtp_subprocess(script)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python xtp_trader.py account|positions|buy|sell <symbol> <qty> [price]")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "account":
        print(json.dumps(get_account(), indent=2, ensure_ascii=False))
    elif cmd == "positions":
        print(json.dumps(get_positions(), indent=2, ensure_ascii=False))
    elif cmd in ("buy", "sell"):
        sym = sys.argv[2]
        qty = int(sys.argv[3])
        price = float(sys.argv[4]) if len(sys.argv) > 4 else None
        print(json.dumps(place_order(sym, cmd, qty, price), indent=2, ensure_ascii=False))
    else:
        print(f"未知命令: {cmd}")
