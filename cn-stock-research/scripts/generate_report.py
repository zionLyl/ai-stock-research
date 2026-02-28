#!/usr/bin/env python3
"""
A股投研报告数据采集 + JSON 输出
重构版：使用 cn_data.py + config_manager.py

用法: python3 generate_report.py [SYMBOL1 SYMBOL2 ...]
无参数时从 config.json 读取 holdings + candidates + report_extras
输出: /tmp/report_data_cn.json
"""

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cn_data import (
    CNStockData, CNMarketData, CNBatchData, TencentAPI,
    _safe_float, _board_type,
)
from config_manager import load_config, get_symbols, get_stop_losses, get_target


def _news_for_symbol(sym, name=""):
    """通过 mcporter 搜索个股新闻"""
    try:
        import subprocess
        query = f"{name} {sym} A股 最新消息" if name else f"{sym} A股 最新消息"
        cmd = f'mcporter call tavily tavily_search query="{query}" max_results=3'
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=25)
        data = json.loads(r.stdout)
        rows = []
        for item in data.get("results", [])[:3]:
            rows.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "snippet": item.get("content", "")[:200],
            })
        return rows
    except Exception:
        return []


def _fetch_symbol_data(sym, quotes_map):
    """采集单标的完整数据"""
    quote = quotes_map.get(sym, {})
    stock = CNStockData(sym)
    tech = stock.get_technical_indicators(n=120)
    name = quote.get("name", "")
    news = _news_for_symbol(sym, name)

    return {
        "symbol": sym,
        "board": _board_type(sym),
        "quote": quote,
        "technical": tech,
        "news": news,
    }


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--output", "-o", default="/tmp/report_data_cn.json")
    parser.add_argument("symbols", nargs="*")
    args = parser.parse_args()

    symbols = args.symbols or get_symbols("report_full")
    if not symbols:
        print("❌ 没有标的。请传入代码或在 config.json 中配置。", file=sys.stderr)
        sys.exit(1)

    print(f"📊 采集 {len(symbols)} 只标的...", file=sys.stderr)
    t0 = time.time()

    report = {
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        "market": "CN",
        "symbols": symbols,
        "indices": {},
        "sectors_top10": [],
        "stocks": {},
        "errors": [],
    }

    # 1. 指数行情
    print("📊 指数行情...", file=sys.stderr)
    try:
        report["indices"] = CNMarketData.get_indices()
    except Exception as e:
        report["errors"].append(f"indices: {e}")

    # 2. 板块 Top 10
    print("📊 板块轮动...", file=sys.stderr)
    try:
        sectors = CNMarketData.get_sector_rotation()
        report["sectors_top10"] = sectors[:10]
    except Exception as e:
        report["errors"].append(f"sectors: {e}")

    # 3. 批量行情
    print("📊 批量行情...", file=sys.stderr)
    quotes_map = CNBatchData.get_batch_quotes(symbols)

    # 4. 并发采集详细数据
    print("📊 并发采集详细数据...", file=sys.stderr)
    max_workers = min(8, max(2, len(symbols)))
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(_fetch_symbol_data, sym, quotes_map): sym
                   for sym in symbols}
        for future in as_completed(futures):
            sym = futures[future]
            try:
                data = future.result()
                report["stocks"][sym] = data
            except Exception as e:
                report["errors"].append(f"{sym}: {e}")

    # Output
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    elapsed = time.time() - t0
    print(f"\n✅ 完成: {len(report['stocks'])} 只标的 | "
          f"{len(report['errors'])} 错误 | {elapsed:.1f}s", file=sys.stderr)
    print(f"📁 {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
