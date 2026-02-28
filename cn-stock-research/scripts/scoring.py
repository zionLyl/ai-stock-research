#!/usr/bin/env python3
"""
A股评分引擎
6维度加权评分（用于持仓评估和候选排名）

与 cn_full_screen.py 的5因子筛选不同:
- 筛选5因子: 用于全市场批量打分（数据有限）
- 评估6维度: 用于深入研究单只股票（数据完整）
"""


# ---------------------------------------------------------------------------
# Scoring weights
# ---------------------------------------------------------------------------

DEFAULT_WEIGHTS = {
    "growth": 0.25,        # 增长确定性
    "valuation": 0.20,     # 估值合理性
    "capital_flow": 0.15,  # 资金面
    "catalyst": 0.15,      # 催化剂
    "technical": 0.10,     # 技术面
    "conviction": 0.15,    # 认知/确信度
}


def _clamp(score: float, lo: float = 1.0, hi: float = 5.0) -> float:
    return max(lo, min(hi, score))


# ---------------------------------------------------------------------------
# Individual scorers (1-5 scale)
# ---------------------------------------------------------------------------

def score_growth(revenue_growth_pct: float = None) -> float:
    """增长评分 — 基于营收增速"""
    if revenue_growth_pct is None:
        return 3.0
    if revenue_growth_pct >= 50:
        return 5.0
    if revenue_growth_pct >= 30:
        return 4.0
    if revenue_growth_pct >= 15:
        return 3.0
    if revenue_growth_pct >= 5:
        return 2.0
    return 1.0


def score_valuation(peg: float = None) -> float:
    """估值评分 — 基于 PEG"""
    if peg is None:
        return 3.0
    if peg <= 0.5:
        return 5.0
    if peg <= 0.8:
        return 4.5
    if peg <= 1.2:
        return 4.0
    if peg <= 2.0:
        return 3.0
    if peg <= 4.0:
        return 2.0
    return 1.0


def score_capital_flow(north_net_flow_m: float = None) -> float:
    """资金面评分 — 基于北向资金净流入（百万元）"""
    if north_net_flow_m is None:
        return 3.0
    if north_net_flow_m >= 100:
        return 5.0
    if north_net_flow_m >= 20:
        return 4.0
    if north_net_flow_m >= -20:
        return 3.0
    if north_net_flow_m >= -100:
        return 2.0
    return 1.0


def score_catalyst(days_to_event: int = None, news_count: int = 0) -> float:
    """催化剂评分"""
    if days_to_event is None:
        base = 3.0
    elif days_to_event <= 7:
        base = 5.0
    elif days_to_event <= 14:
        base = 4.0
    elif days_to_event <= 28:
        base = 3.0
    else:
        base = 2.0
    if news_count >= 3:
        base += 0.5
    elif news_count == 0 and days_to_event is None:
        base -= 0.5
    return _clamp(base)


def score_technical(rsi: float = None, vs_ma20_pct: float = None) -> float:
    """技术面评分"""
    if rsi is None and vs_ma20_pct is None:
        return 3.0
    base = 3.0
    if rsi is not None:
        if rsi <= 30:
            base = 4.5  # 超卖
        elif rsi <= 45:
            base = 4.0
        elif rsi <= 70:
            base = 3.0
        else:
            base = 2.0  # 过热
    if vs_ma20_pct is not None:
        if vs_ma20_pct >= 5:
            base += 0.5
        elif vs_ma20_pct >= 0:
            base += 0.25
        elif vs_ma20_pct <= -5:
            base -= 0.5
    return _clamp(base)


def score_conviction(bull_pct: float = None) -> float:
    """确信度评分"""
    if bull_pct is None:
        return 3.0
    if bull_pct >= 90:
        return 5.0
    if bull_pct >= 75:
        return 4.0
    if bull_pct >= 60:
        return 3.0
    if bull_pct >= 45:
        return 2.0
    return 1.0


# ---------------------------------------------------------------------------
# Composite
# ---------------------------------------------------------------------------

def compute_weighted_score(breakdown: dict, weights: dict = None) -> float:
    """计算加权总分 (1-5)"""
    w = weights or DEFAULT_WEIGHTS
    return round(sum(breakdown.get(k, 3.0) * w.get(k, 0) for k in w), 2)


# ---------------------------------------------------------------------------
# Environment signal
# ---------------------------------------------------------------------------

def assess_environment(north_flow_trend: str = "中性",
                       sh_change_pct: float = None) -> dict:
    """
    A股环境判定
    返回: {signal: "绿灯"/"黄灯"/"红灯", reasons: [...]}
    """
    signal = "黄灯"
    reasons = []

    if north_flow_trend == "连续大额流出":
        signal = "红灯"
        reasons.append("北向资金连续大额流出")
    elif north_flow_trend == "连续流出":
        signal = "黄灯"
        reasons.append("北向资金连续流出")
    elif north_flow_trend == "连续流入":
        signal = "绿灯"
        reasons.append("北向资金连续流入")

    if sh_change_pct is not None:
        if sh_change_pct < -2:
            if signal == "绿灯":
                signal = "黄灯"
            reasons.append(f"上证大跌 {sh_change_pct:.1f}%")
        elif sh_change_pct > 1:
            reasons.append(f"上证上涨 {sh_change_pct:+.1f}%")

    if not reasons:
        reasons.append("数据不足，默认黄灯")

    return {"signal": signal, "reasons": reasons}
