# AI Stock Research Skills

基于 [OpenClaw](https://github.com/openclaw/openclaw) 构建的 AI 投研技能套件，灵感来自 [Anthropic Financial Services Plugins](https://github.com/anthropics/anthropic-cookbook/tree/main/misc/financial_services_plugins) 架构。

用免费数据源 + AI Agent 实现从选股筛选到模拟盘交易的完整闭环。

## 📂 项目结构

```
├── cn-stock-research/     # A股投研（24文件，2381行）
│   ├── SKILL.md           # 路由器（7个子技能调度）
│   ├── commands/          # 7个命令入口
│   ├── skills/            # 7个子技能 SOP
│   └── scripts/           # 数据层 + 筛选 + 交易
│
└── us-stock-research/     # 美股投研（23文件，5206行）
    ├── SKILL.md           # 路由器（8个子技能调度）
    ├── commands/          # 7个命令入口
    ├── skills/            # 8个子技能 SOP
    └── scripts/           # Yahoo Finance + SEC EDGAR + Excel
```

## 🇨🇳 A股投研

**数据源**：Sina Finance API（主） + Tencent Quotes API（备） — 全免费，无需 API key，海外可用

**核心能力**：
- `/screen` — 全市场 5484 只 A 股量化筛选（5 因子模型）
- `/earnings` — 个股财报分析
- `/sector` — 板块轮动追踪
- `/morning-note` — 盘前战报
- `/thesis` — 投资逻辑追踪
- `/monitor` — 持仓监控（支持 XTP 模拟盘）
- `/rebalance` — 调仓执行

**筛选流程**：
```
5484只 → 硬过滤(市值/价格/ST/PE/成交量) → 2690只 → 5因子打分 → Top N
```

**5 因子模型**：成长 30% + 估值 25% + 质量 20% + 安全 15% + 动量 10%

## 🇺🇸 美股投研

**数据源**：Yahoo Finance（主） + SEC EDGAR（交叉验证） + MCP 搜索引擎（定性） — 全免费

**核心能力**：
- `/screen` — S&P 500 + 成长中盘全量筛选（5 因子模型）
- `/earnings` — 财报深度分析
- `/dcf` — DCF 估值模型（含 Excel 输出）
- `/comps` — 可比公司分析
- `/thesis` — 投资论文追踪
- `/morning-note` — 盘前简报
- `/sector` — 行业分析
- 持仓监控（支持 Alpaca 纸交易）

**筛选流程**：
```
536只(S&P500+成长股) → 硬过滤(7条) → 362只 → 5因子打分 → Top N
```

## ⚡ 快速开始

### 前置条件

```bash
pip install yfinance alpaca-py openpyxl requests
```

### 配合 OpenClaw 使用

```bash
# 将 skill 目录复制到 OpenClaw skills 目录
cp -r cn-stock-research ~/.openclaw/skills/
cp -r us-stock-research ~/.openclaw/skills/

# 重启 OpenClaw
openclaw gateway restart
```

然后直接对 AI 说："帮我全市场筛选 A 股 Top 20" 或 "Analyze NVDA earnings"。

### 独立使用脚本

```bash
# A股全市场筛选
cd cn-stock-research/scripts
python cn_full_screen.py 20

# 美股全市场筛选
cd us-stock-research/scripts
python us_full_screen.py 10
```

## 🏗️ 架构设计

借鉴 Anthropic Financial Services Plugins 的 4 条核心原则：

1. **子技能原子化** — 选股、财报、估值、监控各自独立，AI 只加载当前需要的模块
2. **数据源分级降级** — 主源挂了自动切备源，不会因单一数据源故障导致系统瘫痪
3. **输出模板化** — 每类报告有固定结构，杜绝 AI 编数据
4. **自动质检** — 出报告前强制检查：数据源标注、关键字段齐全、结论有据

## 💰 成本

| 项目 | 费用 |
|------|------|
| 数据源 | $0（全部免费 API） |
| 交易模拟 | $0（XTP 模拟盘 / Alpaca Paper） |
| AI 模型 | 取决于你用的模型 |

## ⚠️ 免责声明

本项目仅用于学习和研究目的，不构成投资建议。模拟盘结果不代表实盘表现。投资有风险，决策需谨慎。

## 📄 License

MIT
