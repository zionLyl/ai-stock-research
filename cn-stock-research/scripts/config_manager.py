#!/usr/bin/env python3
"""
A股投研配置管理
从 lib_cn.py 提取，负责 config.json 的读写和持仓/候选/止损管理
"""

import copy
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

DEFAULT_CONFIG = {
    "market": "CN",
    "holdings": [],
    "candidates": [],
    "watchlist": [],
    "report_extras": [],
    "stop_loss": {},
    "targets": {"doubling_target_cny": 200000},
    "account": {"currency": "CNY", "type": "simulation", "broker": "zts_xtp"},
    "xtp": {},
    "macro_indicators": ["上证指数", "沪深300", "中证500", "北向资金", "融资融券", "LPR", "社融"],
    "position_size_wan": 100,  # 每只100万
    "archive": {"enabled": True, "dir": "/tmp/openclaw-archive-cn"},
}


def _deep_merge(base: dict, override: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in (override or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


# ---------------------------------------------------------------------------
# Config CRUD
# ---------------------------------------------------------------------------

def load_config() -> dict:
    try:
        with open(CONFIG_PATH) as f:
            raw = json.load(f)
        return _deep_merge(DEFAULT_CONFIG, raw)
    except FileNotFoundError:
        return copy.deepcopy(DEFAULT_CONFIG)


def save_config(cfg: dict):
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


def update_config(**kwargs) -> dict:
    """
    快捷更新配置:
      update_config(holdings=["600519"], add_holding="300750", remove_holding="000858",
                    candidates=[...], add_candidate=..., remove_candidate=...,
                    watchlist=[...], stop_loss={...}, set_stop_loss=("600519", 1680.0),
                    target=300000, position_size_wan=100)
    """
    cfg = load_config()

    for key in ("holdings", "candidates", "watchlist", "stop_loss", "report_extras"):
        if key in kwargs:
            cfg[key] = kwargs[key]

    if "target" in kwargs:
        cfg["targets"]["doubling_target_cny"] = kwargs["target"]
    if "position_size_wan" in kwargs:
        cfg["position_size_wan"] = kwargs["position_size_wan"]

    # 快捷操作
    for action, list_key in [
        ("add_holding", "holdings"), ("add_candidate", "candidates"),
        ("add_watchlist", "watchlist"), ("add_report_extra", "report_extras"),
    ]:
        if action in kwargs:
            sym = kwargs[action]
            if sym not in cfg[list_key]:
                cfg[list_key].append(sym)

    for action, list_key in [
        ("remove_holding", "holdings"), ("remove_candidate", "candidates"),
        ("remove_watchlist", "watchlist"), ("remove_report_extra", "report_extras"),
    ]:
        if action in kwargs:
            sym = kwargs[action]
            cfg[list_key] = [s for s in cfg[list_key] if s != sym]

    if "set_stop_loss" in kwargs:
        sym, price = kwargs["set_stop_loss"]
        cfg["stop_loss"][sym] = price
    if "remove_stop_loss" in kwargs:
        sym = kwargs["remove_stop_loss"]
        cfg["stop_loss"].pop(sym, None)

    save_config(cfg)
    return cfg


# ---------------------------------------------------------------------------
# Accessors
# ---------------------------------------------------------------------------

def get_symbols(mode="all") -> list:
    """mode: holdings/candidates/watchlist/report/all"""
    cfg = load_config()
    if mode == "holdings":
        return cfg["holdings"]
    elif mode == "candidates":
        return cfg["candidates"]
    elif mode == "watchlist":
        return cfg["watchlist"]
    elif mode == "report":
        return cfg["holdings"] + cfg["candidates"]
    elif mode == "report_full":
        seen = set()
        result = []
        for sym in cfg["holdings"] + cfg["candidates"] + cfg.get("report_extras", []):
            if sym not in seen:
                seen.add(sym)
                result.append(sym)
        return result
    else:
        seen = set()
        result = []
        for sym in cfg["holdings"] + cfg["candidates"] + cfg["watchlist"]:
            if sym not in seen:
                seen.add(sym)
                result.append(sym)
        return result


def get_stop_losses() -> dict:
    return load_config().get("stop_loss", {})


def get_target() -> int:
    return load_config()["targets"]["doubling_target_cny"]


def get_position_size() -> int:
    """每只持仓金额（万元）"""
    return load_config().get("position_size_wan", 100)
