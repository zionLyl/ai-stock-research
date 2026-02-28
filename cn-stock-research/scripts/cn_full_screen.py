#!/usr/bin/env python3
"""
A股全市场量化筛选
类似美股 us_full_screen.py 的A股版本

流程:
1. 拉取全量A股 (~5500只) via Sina API
2. 硬性过滤 (市值/价格/ST/PE/流动性)
3. 5因子打分 (成长30%/估值25%/质量20%/安全15%/动量10%)
4. 输出排名 JSON + Top N 摘要

用法:
    python cn_full_screen.py                   # 默认 Top 50
    python cn_full_screen.py --top 20          # Top 20
    python cn_full_screen.py --output /tmp/x.json  # 指定输出
    python cn_full_screen.py --sector 半导体    # 行业过滤
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# 同目录导入
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cn_data import CNBatchData, CNStockData, TencentAPI, _safe_float, _board_type

###############################################################################
# STEP 1: BUILD UNIVERSE
###############################################################################

def build_universe() -> list:
    """
    获取全量A股
    数据来自 Sina Finance API，含 PE/PB/市值/换手率
    """
    print("📊 Step 1: 拉取全量A股...", file=sys.stderr)
    stocks = CNBatchData.get_all_a_shares(sort="mktcap", max_pages=80)
    print(f"   获取 {len(stocks)} 只", file=sys.stderr)
    return stocks


###############################################################################
# STEP 2: HARD FILTERS
###############################################################################

def apply_hard_filters(stocks: list, sector_filter: str = None) -> list:
    """
    硬性过滤 — 不满足直接淘汰
    """
    print("📊 Step 2: 硬性过滤...", file=sys.stderr)
    passed = []
    stats = {"total": len(stocks), "st": 0, "price": 0, "mktcap": 0,
             "pe": 0, "liquidity": 0, "sector": 0}

    for s in stocks:
        name = s.get("name", "")
        code = s.get("code", "")
        price = _safe_float(s.get("trade"))
        pe = _safe_float(s.get("per"))
        pb = _safe_float(s.get("pb"))
        mktcap = _safe_float(s.get("mktcap"))   # 万元
        amount = _safe_float(s.get("amount"))    # 元
        turnover = _safe_float(s.get("turnoverratio"))

        # 1. 排除 ST / 退市
        if "ST" in name or "退" in name or "*ST" in name:
            stats["st"] += 1
            continue

        # 2. 股价 > 3元
        if price is None or price < 3:
            stats["price"] += 1
            continue

        # 3. 市值 > 50亿 (mktcap 单位是万元)
        if mktcap is None or mktcap < 500000:  # 50亿 = 500000万
            stats["mktcap"] += 1
            continue

        # 4. PE > 0（盈利）
        if pe is None or pe <= 0:
            stats["pe"] += 1
            continue

        # 5. 日成交额 > 5000万
        if amount is not None and amount < 50000000:
            stats["liquidity"] += 1
            continue

        # 6. 行业过滤（如果指定）
        # Sina 数据没有行业字段，跳过行业过滤
        # 后续可通过 MCP 搜索补充

        passed.append({
            "code": code,
            "name": name,
            "price": price,
            "pe": pe,
            "pb": pb,
            "mktcap_wan": mktcap,          # 万元
            "mktcap_yi": round(mktcap / 10000, 2) if mktcap else None,  # 亿元
            "amount": amount,
            "turnover_rate": turnover,
            "change_pct": _safe_float(s.get("changepercent")),
            "board": _board_type(code),
        })

    print(f"   过滤后: {len(passed)} 只 "
          f"(ST:{stats['st']} 低价:{stats['price']} 小市值:{stats['mktcap']} "
          f"亏损:{stats['pe']} 低流动:{stats['liquidity']})",
          file=sys.stderr)
    return passed


###############################################################################
# STEP 3: ENRICH DATA (batch technical indicators)
###############################################################################

def enrich_stock(stock: dict) -> dict:
    """为单只股票补充技术指标"""
    try:
        sd = CNStockData(stock["code"])
        tech = sd.get_technical_indicators(n=120)
        stock["tech"] = tech
    except Exception as e:
        stock["tech"] = {}
        stock["enrich_error"] = str(e)
    return stock


def enrich_batch(stocks: list, max_workers: int = 8) -> list:
    """
    并发补充技术指标
    注意：对 ~1000+ 只股票拉K线，Sina API 可能限流
    所以只对评分前 200 名补充
    """
    print(f"📊 Step 3: 补充技术指标 ({len(stocks)} 只)...", file=sys.stderr)
    enriched = []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(enrich_stock, s): s for s in stocks}
        for i, future in enumerate(as_completed(futures)):
            try:
                result = future.result()
                enriched.append(result)
            except Exception:
                enriched.append(futures[future])
            if (i + 1) % 50 == 0:
                print(f"   已处理 {i+1}/{len(stocks)}", file=sys.stderr)
    return enriched


###############################################################################
# STEP 4: 5-FACTOR SCORING
###############################################################################

WEIGHTS = {
    "growth": 0.30,
    "valuation": 0.25,
    "quality": 0.20,
    "safety": 0.15,
    "momentum": 0.10,
}


def score_stock(stock: dict) -> dict:
    """
    5因子打分 (0-100)
    """
    scores = {}

    pe = stock.get("pe")
    pb = stock.get("pb")
    mktcap_yi = stock.get("mktcap_yi")
    turnover = stock.get("turnover_rate")
    change_pct = stock.get("change_pct")
    tech = stock.get("tech", {})

    # --- Growth (30%) ---
    # 基于 PE 反推（低PE可能意味着成熟期，但这里简化处理）
    # 真正的成长性需要财报数据（营收增速），先用动量+换手率代理
    growth_score = 50  # 基础分
    if change_pct is not None:
        if change_pct > 5:
            growth_score += 20
        elif change_pct > 2:
            growth_score += 10
        elif change_pct < -5:
            growth_score -= 10
    if turnover is not None:
        if turnover > 5:
            growth_score += 15
        elif turnover > 2:
            growth_score += 5
    # RSI 作为趋势代理
    rsi = tech.get("rsi14")
    if rsi is not None:
        if 40 < rsi < 65:
            growth_score += 10  # 健康区间
        elif rsi > 75:
            growth_score -= 5   # 过热
    scores["growth"] = max(0, min(100, growth_score))

    # --- Valuation (25%) ---
    val_score = 50
    if pe is not None:
        if pe < 10:
            val_score += 30
        elif pe < 15:
            val_score += 20
        elif pe < 25:
            val_score += 10
        elif pe < 40:
            val_score += 0
        elif pe < 80:
            val_score -= 10
        else:
            val_score -= 25
    if pb is not None:
        if pb < 1:
            val_score += 15
        elif pb < 2:
            val_score += 10
        elif pb < 5:
            val_score += 0
        elif pb > 10:
            val_score -= 15
    scores["valuation"] = max(0, min(100, val_score))

    # --- Quality (20%) ---
    # 需要财报数据（ROE, 毛利率），先用PB+PE交叉估算
    qual_score = 50
    if pe is not None and pb is not None and pe > 0:
        # 隐含 ROE ≈ PB / PE * 100
        implied_roe = (pb / pe) * 100
        if implied_roe > 20:
            qual_score += 25
        elif implied_roe > 15:
            qual_score += 15
        elif implied_roe > 10:
            qual_score += 5
        elif implied_roe < 5:
            qual_score -= 15
    scores["quality"] = max(0, min(100, qual_score))

    # --- Safety (15%) ---
    safe_score = 50
    if mktcap_yi is not None:
        if mktcap_yi > 2000:
            safe_score += 20   # 超大盘
        elif mktcap_yi > 500:
            safe_score += 15
        elif mktcap_yi > 100:
            safe_score += 5
        else:
            safe_score -= 5
    if turnover is not None:
        if turnover > 1:
            safe_score += 10  # 流动性好
        elif turnover < 0.3:
            safe_score -= 10  # 流动性差
    # 距高点跌幅作为安全边际
    off_high = tech.get("off_high_pct")
    if off_high is not None:
        if off_high < -30:
            safe_score += 10  # 跌多了，安全边际高
        elif off_high > -5:
            safe_score -= 5   # 接近高点
    scores["safety"] = max(0, min(100, safe_score))

    # --- Momentum (10%) ---
    mom_score = 50
    vs_ma20 = tech.get("vs_ma20_pct")
    vs_ma60 = tech.get("vs_ma60_pct")
    if vs_ma20 is not None:
        if vs_ma20 > 5:
            mom_score += 15
        elif vs_ma20 > 0:
            mom_score += 10
        elif vs_ma20 < -10:
            mom_score -= 15
        elif vs_ma20 < 0:
            mom_score -= 5
    if vs_ma60 is not None:
        if vs_ma60 > 10:
            mom_score += 10
        elif vs_ma60 > 0:
            mom_score += 5
        elif vs_ma60 < -20:
            mom_score -= 10
    scores["momentum"] = max(0, min(100, mom_score))

    # --- Composite ---
    composite = sum(scores[k] * WEIGHTS[k] for k in WEIGHTS)
    stock["scores"] = scores
    stock["composite"] = round(composite, 2)
    return stock


###############################################################################
# STEP 5: RANK AND OUTPUT
###############################################################################

def run_screen(top_n: int = 50, output_path: str = None, sector_filter: str = None):
    t0 = time.time()

    # 1. Universe
    universe = build_universe()
    if not universe:
        print("❌ 无法获取A股列表", file=sys.stderr)
        return

    # 2. Hard filter
    filtered = apply_hard_filters(universe, sector_filter=sector_filter)
    if not filtered:
        print("❌ 所有股票被过滤", file=sys.stderr)
        return

    # 3. Pre-score (without tech data, just basics)
    print("📊 Step 3a: 基础打分...", file=sys.stderr)
    for s in filtered:
        score_stock(s)

    # Sort by pre-score, take top 200 for enrichment
    filtered.sort(key=lambda x: x.get("composite", 0), reverse=True)
    top_candidates = filtered[:200]

    # 4. Enrich top 200 with technical indicators
    enriched = enrich_batch(top_candidates, max_workers=6)

    # 5. Re-score with tech data
    print("📊 Step 4: 重新打分...", file=sys.stderr)
    for s in enriched:
        score_stock(s)

    enriched.sort(key=lambda x: x.get("composite", 0), reverse=True)
    top = enriched[:top_n]

    elapsed = time.time() - t0

    # Build result
    result = {
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        "market": "CN",
        "universe_size": len(universe),
        "after_filter": len(filtered),
        "enriched": len(enriched),
        "top_n": top_n,
        "elapsed_seconds": round(elapsed, 1),
        "weights": WEIGHTS,
        "results": [{
            "rank": i + 1,
            "code": s["code"],
            "name": s["name"],
            "price": s["price"],
            "pe": s["pe"],
            "pb": s["pb"],
            "mktcap_yi": s.get("mktcap_yi"),
            "change_pct": s.get("change_pct"),
            "board": s.get("board"),
            "composite": s["composite"],
            "scores": s.get("scores", {}),
            "tech": {k: v for k, v in s.get("tech", {}).items()
                     if k in ("rsi14", "vs_ma20_pct", "vs_ma60_pct", "off_high_pct")},
        } for i, s in enumerate(top)],
    }

    # Output
    out_path = output_path or "/tmp/cn_screen_full.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    # Print summary
    print(f"\n✅ 完成! {result['universe_size']}只 → {result['after_filter']}只(过滤后)"
          f" → Top {top_n} | 耗时 {elapsed:.1f}s", file=sys.stderr)
    print(f"📁 结果: {out_path}\n", file=sys.stderr)

    print(f"{'排名':>4} {'代码':>8} {'名称':<10} {'价格':>8} {'PE':>6} {'PB':>6} "
          f"{'市值(亿)':>8} {'涨跌%':>6} {'综合分':>6} {'板块':<6}")
    print("-" * 80)
    for r in result["results"][:top_n]:
        print(f"{r['rank']:>4} {r['code']:>8} {r['name']:<10} {r['price']:>8.2f} "
              f"{r['pe'] or 0:>6.1f} {r['pb'] or 0:>6.2f} "
              f"{r.get('mktcap_yi') or 0:>8.1f} {r.get('change_pct') or 0:>6.2f} "
              f"{r['composite']:>6.1f} {r.get('board',''):<6}")


###############################################################################
# CLI
###############################################################################

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A股全市场量化筛选")
    parser.add_argument("--top", type=int, default=50, help="输出 Top N (默认50)")
    parser.add_argument("--output", "-o", default=None, help="输出JSON路径")
    parser.add_argument("--sector", default=None, help="行业过滤 (如: 半导体)")
    args = parser.parse_args()
    run_screen(top_n=args.top, output_path=args.output, sector_filter=args.sector)
