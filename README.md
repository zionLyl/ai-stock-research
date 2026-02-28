# AI Stock Research Skills

A股 + 美股 AI 量化投研技能套件，架构灵感来自 [Anthropic Financial Services Plugins](https://github.com/anthropics/anthropic-cookbook/tree/main/misc/financial_services_plugins)。基于 [OpenClaw](https://github.com/openclaw/openclaw) 构建。

AI-powered stock research skills for China A-shares & US equities, inspired by [Anthropic Financial Services Plugins](https://github.com/anthropics/anthropic-cookbook/tree/main/misc/financial_services_plugins). Built on [OpenClaw](https://github.com/openclaw/openclaw).

---

## 🏗️ 架构设计 / Architecture

借鉴 Anthropic Financial Services Plugins 的 4 条核心原则 / 4 core principles from Anthropic FSP:

| 原则 / Principle | 说明 / Description |
|------|------|
| **子技能原子化 / Atomic Sub-skills** | 选股、财报、估值、监控各自独立，AI 只加载当前需要的模块 |
| **数据源分级降级 / Data Source Fallback** | 主源挂了自动切备源（Sina→Tencent / yfinance→SEC EDGAR） |
| **输出模板化 / Templated Output** | 每类报告有固定结构，杜绝 AI 编数据 |
| **自动质检 / Auto Quality Checks** | 出报告前强制检查：数据源标注、关键字段齐全、结论有据 |

---

## 🇨🇳 cn-stock-research — A股投研

**数据源**：Sina Finance API（主力）+ Tencent Quotes API（备用）— **$0，无需 API key，海外可用**

### 目录结构

```
cn-stock-research/
├── SKILL.md              # 路由器 — 根据用户意图分发到子技能
├── commands/             # 7 个命令入口
│   ├── screen.md         # /screen 全市场量化筛选
│   ├── earnings.md       # /earnings 财报分析
│   ├── sector.md         # /sector 板块轮动
│   ├── morning-note.md   # /morning-note 盘前战报
│   ├── thesis.md         # /thesis 投资逻辑追踪
│   ├── monitor.md        # /monitor 持仓监控
│   └── rebalance.md      # /rebalance 调仓执行
├── skills/               # 7 个子技能（每个有独立 SOP）
│   ├── stock-screening/
│   ├── earnings-analysis/
│   ├── sector-rotation/
│   ├── morning-note/
│   ├── thesis-tracker/
│   ├── portfolio-monitor/
│   └── rebalance/
└── scripts/
    ├── cn_data.py        # 数据层（Sina + Tencent API，544行）
    ├── cn_full_screen.py # 全市场筛选引擎（401行）
    ├── scoring.py        # 6维评分引擎
    ├── xtp_trader.py     # XTP 交易层（中泰证券模拟盘）
    ├── config_manager.py # 配置管理
    └── generate_report.py
```

### 筛选流程

```
5484只全A股
  ↓ 硬过滤：市值>50亿 / 股价>3元 / 非ST / PE>0 / 日成交>5000万
2690只
  ↓ 5因子打分：成长30% + 估值25% + 质量20% + 安全15% + 动量10%
  ↓ Top 200 补充K线/技术指标 → 重新打分
Top N（默认50只）
```

运行时间：~130 秒完成全市场筛选

### 快速开始

```bash
# 安装依赖
pip install requests

# 独立运行：全市场筛选 Top 20
python cn-stock-research/scripts/cn_full_screen.py 20
```

### 配置 XTP 模拟盘（可选）

```bash
export XTP_PASSWORD='your_password'
export XTP_KEY='your_key'
# 编辑 cn-stock-research/scripts/config.json，填入你的 XTP 账号信息
```

---

## 🇺🇸 us-stock-research — US Equities

**Data Sources**: Yahoo Finance (primary) + SEC EDGAR (cross-validation) + MCP search engines (qualitative) — **$0**

### Directory Structure

```
us-stock-research/
├── SKILL.md              # Router — dispatches to sub-skills by user intent
├── commands/             # 7 command entry points
│   ├── screen.md         # /screen quantitative screening
│   ├── earnings.md       # /earnings post-earnings analysis
│   ├── dcf.md            # /dcf discounted cash flow model
│   ├── comps.md          # /comps comparable company analysis
│   ├── thesis.md         # /thesis investment thesis tracking
│   ├── morning-note.md   # /morning-note pre-market briefing
│   └── sector.md         # /sector industry overview
├── skills/               # 8 sub-skills (each with detailed SOP)
│   ├── stock-screening/
│   ├── earnings-analysis/
│   ├── dcf-valuation/
│   ├── comps-analysis/
│   ├── thesis-tracker/
│   ├── morning-note/
│   ├── sector-overview/
│   └── portfolio-monitor/
└── scripts/
    ├── yahoo_finance.py  # Yahoo Finance data wrapper (489 lines)
    ├── sec_edgar.py      # SEC EDGAR filing fetcher (454 lines)
    └── excel_builder.py  # Excel model builder (861 lines)
```

### Screening Pipeline

```
536 stocks (S&P 500 + growth mid-caps)
  ↓ Hard filters: market cap >$5B / forward PE 0-100 / revenue growth >0% / gross margin >20% / analyst coverage
362 stocks
  ↓ 5-factor scoring: Growth 30% + Value 25% + Quality 20% + Safety 15% + Momentum 10%
Top N (default 10)
```

### Quick Start

```bash
# Install dependencies
pip install yfinance openpyxl

# Standalone: full market screen, top 10
python us-stock-research/scripts/us_full_screen.py 10
```

### Configure Alpaca Paper Trading (Optional)

```bash
export ALPACA_API_KEY='your_api_key'
export ALPACA_SECRET='your_secret'
```

Free paper trading, no US residency required. Sign up at [alpaca.markets](https://alpaca.markets).

---

## ⚡ Use with OpenClaw

```bash
# Copy skills to OpenClaw directory
cp -r cn-stock-research ~/.openclaw/skills/
cp -r us-stock-research ~/.openclaw/skills/

# Restart
openclaw gateway restart
```

Then talk to your AI:
- "帮我全市场筛选 A 股 Top 20"
- "分析贵州茅台最新财报"
- "Screen US stocks for high growth"
- "Analyze NVDA latest earnings"
- "Build a DCF model for AAPL"

---

## 💰 Cost

| Item | Cost |
|------|------|
| A股数据 (Sina / Tencent) | $0 |
| US data (Yahoo Finance / SEC) | $0 |
| 模拟交易 (XTP / Alpaca) | $0 |
| AI model | Depends on your choice |

---

## ⚠️ 免责声明 / Disclaimer

本项目仅用于学习和研究目的，不构成投资建议。模拟盘结果不代表实盘表现。

This project is for educational and research purposes only. It does not constitute investment advice. Simulated trading results do not represent real trading performance.

## 📄 License

MIT
