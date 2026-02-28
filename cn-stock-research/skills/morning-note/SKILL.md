---
name: morning-note
description: A股盘前战报。市场概览、持仓预警、今日策略。2分钟读完。
---

# 盘前战报

设计目标：2分钟读完，只保留影响今日操作的信息。

## 工作流

### Step 1: 市场概览
```python
from cn_data import CNMarketData
snap = CNMarketData.get_market_snapshot()  # 指数行情
sectors = CNMarketData.get_sector_rotation()  # 板块排名
```

### Step 2: 持仓检查
```python
from cn_data import CNBatchData
from config_manager import get_symbols
holdings = get_symbols("holdings")
quotes = CNBatchData.get_batch_quotes(holdings)
```
- 标注涨跌 ≥3% 的持仓
- 检查是否有持仓触及止损位

### Step 3: 重大事件
MCP 搜索: "A股 今日 重大消息" + 持仓相关新闻

### Step 4: 输出格式
```
📊 A股盘前战报 YYYY-MM-DD

指数: 上证XXXX(+X.X%) | 沪深300 XXXX(+X.X%) | 创业板 XXXX(+X.X%)
环境: 🟢绿灯 / 🟡黄灯 / 🔴红灯

持仓预警:
⚠️ XXX 涨/跌 X.X%（原因）
⚠️ XXX 接近止损位

今日关注:
- 事件1
- 事件2

策略: 一句话总结今日操作方向
```
