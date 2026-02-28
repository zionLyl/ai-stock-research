---
name: rebalance
description: 调仓执行。卖出+买入、目标权重调整、XTP 下单。
---

# 调仓执行

## 适用场景
- 全量建仓（筛选后首次买入）
- 换仓（卖旧买新）
- 目标权重调整

## 执行前检查
1. 当前是否为交易时间（9:30-11:30, 13:00-15:00）？
2. XTP 账户是否可连接？
3. 可用资金是否充足？

## 工作流

### Step 1: 确定目标持仓
从 config.json 或 screening 结果获取目标标的列表。

### Step 2: 计算差异
```
目标持仓 - 当前持仓 = 需要买入的
当前持仓 - 目标持仓 = 需要卖出的
```

### Step 3: 先卖后买
T+1 规则下，卖出释放的资金当天可用于买入。
1. 执行所有卖单
2. 等待确认
3. 执行所有买单

### Step 4: 拆单逻辑
```python
from xtp_trader import place_order
# 自动拆单: 主板 ≤999,900股, 科创板 ≤99,900股
result = place_order("600519", "buy", quantity, price)
```

### Step 5: 确认和记录
- 检查所有订单状态
- 更新 config.json（holdings/candidates）
- 记录到 memory/YYYY-MM-DD.md

## 仓位规则
- **单只**: 100万（用户设定）
- **总持仓**: 不超本金80%
- **现金保留**: ≥20%

## 下单注意
- 市价单用 BEST5_OR_CANCEL (price_type=5)
- 限价单建议挂在买一/卖一附近
- 非交易时间下单会被拒绝（XTP error）
- 科创板最小交易单位 200 股
