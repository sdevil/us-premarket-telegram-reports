#!/usr/bin/env bash
set -euo pipefail

# Set TELEGRAM_TARGET before use, for example:
# export TELEGRAM_TARGET=<TELEGRAM_TARGET>
: "${TELEGRAM_TARGET:?Set TELEGRAM_TARGET to the Telegram chat target}"

PROMPT=$(cat <<'EOF'
Generate the next US trading day long watchlist.

Requirements:
- Research only from English financial sources.
- Final report must be entirely in Simplified Chinese except ticker symbols and terms like VIX, SPY, QQQ, VWAP, R/R.
- Focus only on institutional-quality LONG setups.
- Stock universe limited to S&P 500 and Nasdaq 100.
- Use reliable sources: Yahoo Finance, Nasdaq Market Activity, Reuters Markets, CNBC Markets.
- If premarket data is unavailable, explicitly say unavailable and rely on previous day levels.
- Return EXACTLY 3 ranked trade candidates.
- Focus on: strong catalysts, strong relative volume, high liquidity, institutional participation, strong sector alignment, favorable risk/reward.

Output format:
美股盘前做多观察名单
日期：YYYY-MM-DD

今日交易环境评估
市场适合度：
交易风险等级：

市场环境
VIX：
SPY趋势：
QQQ趋势：

市场广度

板块强弱
强势板块：
弱势板块：

市场主题
主题1
主题2
主题3

盘前做多候选
#1 股票代码 – 公司名称
催化剂：
做多逻辑：
关键价位
昨日高点：
昨日低点：
阻力位：
支撑位：
交易策略
触发价格：
买入区间：
止损价格：
目标价格：
风险回报比：
相对成交量：
仓位建议：
信心评分：
结构评分：
胜率估计：

#2 ... same structure
#3 ... same structure

Telegram 交易卡片
#1 TICKER
Trigger：
Entry：
Stop：
Target：
Size：
Setup Score：
Win Probability：

#2 ...
#3 ...

9:30–10:00 交易执行脚本

开盘备注
关键观察点

Keep it concise and readable in under two minutes.
EOF
)

openclaw agent --channel telegram --to "$TELEGRAM_TARGET" --deliver --timeout 600 --message "$PROMPT"
