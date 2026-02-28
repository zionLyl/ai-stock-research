# AI Stock Research Skills

[中文](#中文) | [English](#english)

---

<a id="中文"></a>

## 🇨🇳 中文

基于 [OpenClaw](https://github.com/openclaw/openclaw) 构建的 AI 投研技能套件，架构灵感来自 [Anthropic Financial Services Plugins](https://github.com/anthropics/anthropic-cookbook/tree/main/misc/financial_services_plugins)。

**用免费数据源 + AI Agent，实现从全市场量化筛选到模拟盘自动交易的完整闭环。**

### 📂 项目结构

```
├── cn-stock-research/        # A股投研（7个子技能）
│   ├── SKILL.md              # 路由器 — 根据用户意图分发到子技能
│   ├── commands/             # 7个命令入口
│   │   ├── screen.md         # /screen 全市场量化筛选
│   │   ├── earnings.md       # /earnings 财报分析
│   │   ├── sector.md         # /sector 板块轮动
│   │   ├── morning-note.md   # /morning-note 盘前战报
│   │   ├── thesis.md         # /thesis 投资逻辑追踪
│   │   ├── monitor.md        # /monitor 持仓监控
│   │   └── rebalance.md      # /rebalance 调仓执行
│   ├── skills/               # 7个子技能（每个有独立 SOP）
│   └── scripts/              # Python 脚本
│       ├── cn_data.py        # 数据层（Sina + Tencent API）
│       ├── cn_full_screen.py # 全市场筛选引擎
│       ├── scoring.py        # 评分引擎
│       ├── xtp_trader.py     # XTP 交易层（中泰证券模拟盘）
│       ├── config_manager.py # 配置管理
│       └── generate_report.py
│
└── us-stock-research/        # 美股投研（8个子技能）
    ├── SKILL.md              # 路由器
    ├── commands/             # 7个命令入口
    │   ├── screen.md         # /screen 量化筛选
    │   ├── earnings.md       # /earnings 财报分析
    │   ├── dcf.md            # /dcf 估值模型
    │   ├── comps.md          # /comps 可比公司
    │   ├── thesis.md         # /thesis 投资论文
    │   ├── morning-note.md   # /morning-note 盘前简报
    │   └── sector.md         # /sector 行业分析
    ├── skills/               # 8个子技能
    └── scripts/
        ├── yahoo_finance.py  # Yahoo Finance 数据封装
        ├── sec_edgar.py      # SEC EDGAR 文件抓取
        └── excel_builder.py  # Excel 报告生成
```

### 🏗️ 架构设计

借鉴 Anthropic Financial Services Plugins 的 4 条核心原则：

| 原则 | 说明 |
|------|------|
| **子技能原子化** | 选股、财报、估值、监控各自独立，AI 只加载当前需要的模块 |
| **数据源分级降级** | 主源挂了自动切备源（Sina → Tencent / yfinance → SEC） |
| **输出模板化** | 每类报告有固定结构，杜绝 AI 编数据、写散文 |
| **自动质检** | 出报告前强制检查：数据源标注、关键字段齐全、结论有据 |

### 📊 A股：全市场量化筛选

**数据源**：Sina Finance API（主力）+ Tencent Quotes API（备用）— **$0，无需 API key，海外可用**

**筛选流程**：
```
5484只全A股
  ↓ 硬过滤：市值>50亿 / 股价>3元 / 非ST / PE>0 / 日成交>5000万
2690只
  ↓ 5因子打分：成长30% + 估值25% + 质量20% + 安全15% + 动量10%
  ↓ Top 200 补充K线/技术指标 → 重新打分
Top N（默认50）
```

**运行时间**：~130 秒完成全市场筛选

**交易**：支持中泰证券 XTP 模拟盘（需自行申请账号）

### 📊 美股：S&P 500+ 量化筛选

**数据源**：Yahoo Finance（主力）+ SEC EDGAR（交叉验证）+ MCP 搜索引擎（定性信息）— **$0**

**筛选流程**：
```
536只（S&P 500 + 成长中盘股）
  ↓ 硬过滤：市值>$5B / 正向PE(<100) / 营收增长 / 毛利率>20% / 有分析师覆盖
362只
  ↓ 5因子打分：成长30% + 估值25% + 质量20% + 安全15% + 动量10%
Top N（默认10）
```

**交易**：支持 Alpaca Paper Trading（免费纸交易，不需要美国身份）

### ⚡ 快速开始

#### 前置条件

```bash
pip install yfinance alpaca-py openpyxl requests
```

#### 配合 OpenClaw 使用

```bash
# 复制 skill 到 OpenClaw skills 目录
cp -r cn-stock-research ~/.openclaw/skills/
cp -r us-stock-research ~/.openclaw/skills/

# 重启
openclaw gateway restart
```

然后对 AI 说：
- "帮我全市场筛选 A 股 Top 20"
- "分析贵州茅台最新财报"
- "Analyze NVDA earnings"
- "Screen US stocks for high growth"

#### 独立运行脚本

```bash
# A股全市场筛选 Top 20
python cn-stock-research/scripts/cn_full_screen.py 20

# 美股全市场筛选 Top 10
python us-stock-research/scripts/us_full_screen.py 10
```

#### 配置 XTP 模拟盘（可选）

```bash
# 设置环境变量
export XTP_PASSWORD='your_password'
export XTP_KEY='your_key'

# 编辑 cn-stock-research/scripts/config.json，填入你的账号信息
```

#### 配置 Alpaca 纸交易（可选）

```bash
export ALPACA_API_KEY='your_api_key'
export ALPACA_SECRET='your_secret'
```

### 💰 成本

| 项目 | 费用 |
|------|------|
| A股数据（Sina / Tencent） | $0 |
| 美股数据（Yahoo Finance / SEC） | $0 |
| 交易模拟（XTP / Alpaca） | $0 |
| AI 模型 | 取决于你用的模型 |

### ⚠️ 免责声明

本项目仅用于学习和研究目的，不构成投资建议。模拟盘结果不代表实盘表现。投资有风险，决策需谨慎。

---

<a id="english"></a>

## 🇺🇸 English

AI-powered stock research skill suite built on [OpenClaw](https://github.com/openclaw/openclaw), inspired by the architecture of [Anthropic Financial Services Plugins](https://github.com/anthropics/anthropic-cookbook/tree/main/misc/financial_services_plugins).

**Free data sources + AI Agent = Full pipeline from market-wide quantitative screening to simulated trading.**

### 🏗️ Architecture

Adapted from 4 core principles of Anthropic's Financial Services Plugins:

| Principle | Implementation |
|-----------|---------------|
| **Atomic sub-skills** | Screening, earnings, valuation, monitoring are independent modules. AI loads only what it needs. |
| **Data source fallback** | Primary fails → auto-switch to backup (Sina→Tencent / yfinance→SEC EDGAR) |
| **Templated output** | Every report type has a fixed structure. No AI hallucination in numbers. |
| **Auto quality checks** | Pre-publish validation: source citations, key fields present, evidence-based conclusions |

### 📊 China A-Shares

**Data Sources**: Sina Finance API (primary) + Tencent Quotes API (fallback) — **Free, no API key, works globally**

**Screening Pipeline**:
```
5,484 A-shares (full market)
  ↓ Hard filters: market cap >5B CNY / price >3 CNY / non-ST / PE >0 / daily volume >50M CNY
2,690 stocks
  ↓ 5-factor scoring: Growth 30% + Value 25% + Quality 20% + Safety 15% + Momentum 10%
  ↓ Top 200 enriched with K-line/technicals → re-scored
Top N (default 50)
```

**Runtime**: ~130 seconds for full market scan

**Trading**: XTP simulated trading (ZTS Securities, China)

**7 Sub-skills**: stock-screening, earnings-analysis, sector-rotation, morning-note, thesis-tracker, portfolio-monitor, rebalance

### 📊 US Equities

**Data Sources**: Yahoo Finance (primary) + SEC EDGAR (cross-validation) + MCP search engines (qualitative) — **Free**

**Screening Pipeline**:
```
536 stocks (S&P 500 + growth mid-caps)
  ↓ Hard filters: market cap >$5B / forward PE 0-100 / revenue growth >0 / gross margin >20% / analyst coverage
362 stocks
  ↓ 5-factor scoring: Growth 30% + Value 25% + Quality 20% + Safety 15% + Momentum 10%
Top N (default 10)
```

**Trading**: Alpaca Paper Trading (free, no US residency required)

**8 Sub-skills**: stock-screening, earnings-analysis, dcf-valuation, comps-analysis, thesis-tracker, morning-note, sector-overview, portfolio-monitor

### ⚡ Quick Start

#### Prerequisites

```bash
pip install yfinance alpaca-py openpyxl requests
```

#### With OpenClaw

```bash
cp -r cn-stock-research ~/.openclaw/skills/
cp -r us-stock-research ~/.openclaw/skills/
openclaw gateway restart
```

Then ask your AI:
- "Screen A-shares, give me top 20"
- "Analyze NVDA latest earnings"
- "Build a DCF model for AAPL"

#### Standalone Scripts

```bash
# A-share full market screen, top 20
python cn-stock-research/scripts/cn_full_screen.py 20

# US stock screen, top 10
python us-stock-research/scripts/us_full_screen.py 10
```

#### Configure Trading (Optional)

**XTP (China A-shares)**:
```bash
export XTP_PASSWORD='your_password'
export XTP_KEY='your_key'
# Edit cn-stock-research/scripts/config.json with your account info
```

**Alpaca (US equities)**:
```bash
export ALPACA_API_KEY='your_api_key'
export ALPACA_SECRET='your_secret'
```

### 💰 Cost

| Item | Cost |
|------|------|
| A-share data (Sina / Tencent) | $0 |
| US data (Yahoo Finance / SEC) | $0 |
| Simulated trading (XTP / Alpaca) | $0 |
| AI model | Depends on your choice |

### ⚠️ Disclaimer

This project is for educational and research purposes only. It does not constitute investment advice. Simulated trading results do not represent real trading performance. Invest at your own risk.

### 📄 License

MIT
