---
name: sector-rotation
description: A股板块轮动分析。行业/概念板块涨跌排名、资金流向、龙头异动。
---

# 板块轮动分析

## 适用场景
- "今天哪些板块涨了"
- "最近热点板块是什么"
- "半导体板块怎么样"

## 工作流

### Step 1: 获取板块数据
```bash
python3 scripts/cn_data.py --sector
```
返回行业板块涨跌排名 Top 30。

### Step 2: 概念板块
通过 `CNMarketData.get_concept_sectors()` 获取概念板块排名。

### Step 3: 分析
- 涨幅前5板块：是主题炒作还是基本面驱动？
- 跌幅前5板块：是获利回吐还是趋势反转？
- 持仓相关板块的排名变化
- MCP 搜索政策催化（如果板块异动明显）

### Step 4: 输出
- 行业板块 Top 10 涨跌排名
- 概念板块 Top 10 涨跌排名
- 一句话判断：当前市场风格（大盘/小盘、价值/成长、进攻/防守）
- 对持仓的影响建议

## 数据源
- Sina Finance API: 行业板块(`hangye_block`)、概念板块(`gainian_block`)
- MCP 搜索: 政策解读、板块催化事件
