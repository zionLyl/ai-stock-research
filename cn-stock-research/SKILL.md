---
name: cn-stock-research
description: >
  A股投研全流程。触发条件: 用户要求"投研/选股/筛选/screen/盘前/复盘/持仓/调仓/板块/财报"
  或 cron 定时任务。单一问价/闲聊不触发。
---

# A股投研套件

模块化投研系统，覆盖选股→分析→交易→监控全流程。

## 路由表

| 用户意图 | 子技能 | 命令 |
|---------|--------|------|
| 全市场量化筛选 | `stock-screening` | `/screen` |
| 财报/业绩分析 | `earnings-analysis` | `/earnings` |
| 板块轮动分析 | `sector-rotation` | `/sector` |
| 盘前战报 | `morning-note` | `/morning-note` |
| 投资逻辑追踪 | `thesis-tracker` | `/thesis` |
| 持仓监控 | `portfolio-monitor` | `/monitor` |
| 调仓执行 | `rebalance` | `/rebalance` |

多意图请求按顺序执行（如"选股+建仓" → screening → rebalance）。

## 数据源

**主数据源（免费、海外可用、不封IP）：**

| 数据源 | 用途 | 备注 |
|--------|------|------|
| **Sina Finance API** | 全量A股列表、行情、K线、PE/PB/市值 | 5484只分页查询，无需API key |
| **Tencent Quotes API** | 实时行情兜底、PE/PB/市值/换手率 | `qt.gtimg.cn`，GBK编码 |
| **MCP 搜索** (Tavily/Serper/Jina) | 新闻、政策、事件驱动 | 通过 mcporter 调用 |
| **XTP** (中泰证券) | 模拟盘交易/持仓/资金 | xtpwrapper，subprocess 隔离 |

**已弃用：** AKShare（底层调东方财富API，海外IP被封）

## 数据质量铁律

### 1. 多源交叉验证
每个关键数据点（股价、PE、市值）从 **Sina + Tencent** 交叉验证，差异 >5% 标注。

### 2. 搜索失败必须重试
空结果或报错 → 换源重试（tavily→serper→jina），最多3次。

### 3. 空数据禁入决策
关键数据缺失 → 该股票不能被推荐。**绝不编造数据。**

### 4. 出报告前自检
每只推荐必须有: ✅最新价 ✅PE/PB ✅市值 ✅涨跌幅 ✅推荐依据(新闻/数据)。

### 5. 决策基于事实
禁止"常识"/"众所周知"。每个选股决策关联具体数据或新闻。

## 脚本

| 脚本 | 用途 | 用法 |
|------|------|------|
| `scripts/cn_data.py` | 数据层 (Sina+Tencent) | `python cn_data.py 600519 [--json\|--market-snapshot\|--sector]` |
| `scripts/cn_full_screen.py` | 全市场量化筛选 | `python cn_full_screen.py [--top 50] [--output path]` |
| `scripts/config_manager.py` | 配置管理 | Python import |
| `scripts/scoring.py` | 6维评分引擎 | Python import |
| `scripts/xtp_trader.py` | XTP 交易 | `python xtp_trader.py account\|positions\|buy\|sell` |
| `scripts/generate_report.py` | 报告数据采集 | `python generate_report.py [SYM1 SYM2]` |
| `scripts/toolchain_selftest.py` | 工具链健康检查 | `python toolchain_selftest.py` |

## A股特殊规则

- **T+1**: 当天买入不能当天卖出
- **涨跌停**: 主板/创业板 ±10%, 科创板 ±20%, 北交所 ±30%, ST ±5%
- **XTP 枚举反转**: `MARKET_TYPE` SZ_A=1/SH_A=2 vs `EXCHANGE_TYPE` SH=1/SZ=2
- **单笔限量**: 主板 ≤999,900股, 科创板 ≤99,900股
- **持仓规模**: 100万/只 (用户设定)

## 质量检查

- [ ] 持仓数据准确？
- [ ] 指数/宏观完整？
- [ ] 事件来自真实搜索？
- [ ] 零 AI 幻觉？
- [ ] T+1 已考虑？
