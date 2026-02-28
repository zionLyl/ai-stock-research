---
name: portfolio-monitor
description: 持仓监控、盈亏追踪、异常预警。
---

# 持仓监控

## 适用场景
- Cron 定时监控（盘中 4 次）
- 用户主动查看持仓
- 大盘异动时检查

## 工作流

### Step 1: 获取持仓
```python
from xtp_trader import get_positions, get_account
from cn_data import CNBatchData
from config_manager import get_symbols, get_stop_losses

positions = get_positions()  # XTP 真实持仓
account = get_account()      # 资金情况
```

### Step 2: 获取实时行情
```python
codes = [p["ticker"] for p in positions]
quotes = CNBatchData.get_batch_quotes(codes)
```

### Step 3: 计算盈亏
每只: 市值 = 数量 × 现价, 盈亏 = 市值 - 成本

### Step 4: 异常检测
- 涨跌 ≥ 5% → 🚀/💥 标注
- 触及止损位 → ⚠️ 立即预警
- 组合总亏损 > 3% → 🔴 风控提醒

### Step 5: 输出格式
```
📊 XTP 持仓监控 (N只)
总资产: XX亿 | 持仓市值: XX万 | 可用: XX亿

板块1 (N只) 🟢/🔴 +XX万(+X.X%)
  🟢 股票A XX.XX(+X.X%) +XX万(+X.X%)
  🔴 股票B XX.XX(-X.X%) -XX万(-X.X%)

⚠️ 异常提醒:
🚀 XX 涨幅超5%
💥 XX 跌幅超5%
```

## 与其他子技能联动
- 异常 → 触发 thesis-tracker 复查
- 止损 → 触发 rebalance 执行卖出
