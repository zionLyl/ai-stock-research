#!/usr/bin/env python3
"""XTP 查询工具 - 独立进程运行，避免回调阻塞"""
import os, sys, time, json

def main():
    from xtpwrapper import TraderApi
    
    password = os.environ.get("XTP_PASSWORD", "")
    key = os.environ.get("XTP_KEY", "")
    if not password or not key:
        print(json.dumps({"error": "XTP_PASSWORD 或 XTP_KEY 未设置"}))
        return
    
    results = {"asset": None, "positions": [], "asset_done": False, "pos_done": False}
    
    class MyTrader(TraderApi):
        def OnQueryAsset(self, asset, error_info, req, is_last, sid):
            if asset:
                results["asset"] = {
                    "total_asset": asset.total_asset,
                    "buying_power": asset.buying_power,
                    "security_asset": asset.security_asset,
                }
            if is_last:
                results["asset_done"] = True
        
        def OnQueryPosition(self, pos, error_info, req, is_last, sid):
            if pos and pos.ticker:
                tk = pos.ticker.decode() if isinstance(pos.ticker, bytes) else str(pos.ticker)
                nm = pos.ticker_name
                if isinstance(nm, bytes):
                    try: nm = nm.decode("gbk")
                    except: nm = nm.decode("utf-8", errors="replace")
                results["positions"].append({
                    "ticker": tk,
                    "name": nm,
                    "total_qty": int(pos.total_qty),
                    "sellable_qty": int(pos.sellable_qty),
                    "avg_price": float(pos.avg_price),
                    "unrealized_pnl": float(pos.unrealized_pnl),
                    "yesterday_position": int(pos.yesterday_position),
                })
            if is_last:
                results["pos_done"] = True
    
    cfg_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(cfg_path) as f:
        cfg = json.load(f)
    xtp = cfg.get("xtp", {})
    
    log_dir = "/tmp/xtp_query"
    os.makedirs(log_dir, exist_ok=True)
    
    trader = MyTrader()
    trader.CreateTrader(3, log_dir, 18)
    trader.SetSoftwareKey(key)
    
    sid = trader.Login(
        xtp.get("trade_server", "122.112.139.0"),
        xtp.get("trade_port", 6104),
        xtp.get("account", "YOUR_XTP_ACCOUNT"),
        password,
    )
    
    if sid == 0:
        err = trader.GetApiLastError()
        print(json.dumps({"error": f"登录失败: {err.error_msg}"}))
        trader.Release()
        return
    
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    
    if cmd in ("asset", "all"):
        trader.QueryAsset(sid, 0)
        for _ in range(50):
            if results["asset_done"]: break
            time.sleep(0.1)
    
    if cmd in ("positions", "all"):
        trader.QueryPosition("", sid, 0)
        for _ in range(50):
            if results["pos_done"]: break
            time.sleep(0.1)
    
    trader.Logout(sid)
    trader.Release()
    
    output = {}
    if cmd in ("asset", "all"):
        output["asset"] = results["asset"]
    if cmd in ("positions", "all"):
        output["positions"] = results["positions"]
    
    print(json.dumps(output, ensure_ascii=False))

if __name__ == "__main__":
    main()
