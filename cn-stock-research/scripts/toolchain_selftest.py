#!/usr/bin/env python3
"""
A股投研工具链健康检查 (v2)
检查: Sina API, Tencent API, MCP, XTP, 新模块导入
"""

import json
import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

PASS = "✅"
FAIL = "❌"
WARN = "⚠️"

results = []

def check(name, ok, detail=""):
    status = PASS if ok else FAIL
    results.append((status, name, detail))
    print(f"  {status} {name}" + (f" — {detail}" if detail else ""))


print("🔍 A股投研工具链健康检查\n")

# 1. Module imports
print("📦 模块导入:")
try:
    from cn_data import CNStockData, CNMarketData, CNBatchData, SinaAPI, TencentAPI
    check("cn_data.py", True)
except Exception as e:
    check("cn_data.py", False, str(e))

try:
    from config_manager import load_config, get_symbols, update_config
    check("config_manager.py", True)
except Exception as e:
    check("config_manager.py", False, str(e))

try:
    from scoring import score_growth, compute_weighted_score, assess_environment
    check("scoring.py", True)
except Exception as e:
    check("scoring.py", False, str(e))

try:
    from xtp_trader import get_account, get_positions
    check("xtp_trader.py", True)
except Exception as e:
    check("xtp_trader.py", False, str(e))

# 2. Data sources
print("\n📡 数据源:")
try:
    count = SinaAPI.get_total_count()
    check("Sina Finance API", count > 0, f"A股总数: {count}")
except Exception as e:
    check("Sina Finance API", False, str(e))

try:
    idx = TencentAPI.get_index_quotes()
    sh = idx.get("上证指数", {})
    check("Tencent Quotes API", bool(sh.get("price")),
          f"上证: {sh.get('price')} ({sh.get('change_pct')}%)" if sh else "")
except Exception as e:
    check("Tencent Quotes API", False, str(e))

try:
    q = TencentAPI.get_quotes(["600519"])
    mt = q.get("600519", {})
    check("Tencent 个股行情", bool(mt.get("price")),
          f"茅台: {mt.get('price')} PE={mt.get('pe')}" if mt else "")
except Exception as e:
    check("Tencent 个股行情", False, str(e))

try:
    kline = SinaAPI.get_kline("600519", scale=240, datalen=5)
    check("Sina K线数据", len(kline) >= 3, f"{len(kline)} 条")
except Exception as e:
    check("Sina K线数据", False, str(e))

# 3. MCP
print("\n🔌 MCP 搜索:")
try:
    r = subprocess.run("command -v mcporter", shell=True, capture_output=True)
    check("mcporter CLI", r.returncode == 0)
except Exception as e:
    check("mcporter CLI", False, str(e))

# 4. Config
print("\n⚙️ 配置:")
try:
    cfg = load_config()
    h = len(cfg.get("holdings", []))
    c = len(cfg.get("candidates", []))
    w = len(cfg.get("watchlist", []))
    check("config.json", True, f"holdings={h} candidates={c} watchlist={w}")
except Exception as e:
    check("config.json", False, str(e))

# 5. XTP
print("\n💹 XTP (可选):")
xtp_pw = os.environ.get("XTP_PASSWORD", "")
xtp_key = os.environ.get("XTP_KEY", "")
if xtp_pw and xtp_key:
    check("XTP 环境变量", True)
else:
    check("XTP 环境变量", False, "XTP_PASSWORD 或 XTP_KEY 未设置 (可选)")

# Summary
print("\n" + "─" * 40)
passed = sum(1 for s, _, _ in results if s == PASS)
failed = sum(1 for s, _, _ in results if s == FAIL)
print(f"总计: {passed} 通过 / {failed} 失败 / {len(results)} 项")
if failed > 0:
    print(f"\n{FAIL} 有 {failed} 项检查未通过")
    sys.exit(1)
else:
    print(f"\n{PASS} 全部通过!")
