#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
: "${TELEGRAM_TARGET:?Set TELEGRAM_TARGET to the Telegram chat target}"
TRADE_DATE="$(TZ=America/New_York date +%F)"
REPORT_DIR="${REPORT_DIR:-$(pwd)/reports}"
mkdir -p "$REPORT_DIR"
OUTFILE="$REPORT_DIR/${TRADE_DATE}-overnight.md"
PROMPT=$(cat <<'EOF'
Update the US premarket long watchlist before the US market opens.

Requirements:
- Research only from English financial sources.
- Final report must be entirely in Simplified Chinese except ticker symbols and terms like VIX, SPY, QQQ, VWAP, R/R.
- Focus only on institutional-quality LONG setups.
- Stock universe limited to S&P 500 and Nasdaq 100.
- Use reliable sources: Yahoo Finance, Nasdaq Market Activity, Reuters Markets, CNBC Markets.
- Incorporate overnight futures tone, premarket movers, and breaking news when reliable.
- If premarket data is unavailable, explicitly say unavailable and rely on previous day levels.
- Return EXACTLY 3 ranked trade candidates.
- Focus on: strong catalysts, strong relative volume, high liquidity, institutional participation, strong sector alignment, favorable risk/reward.

Selection rules:
- Do NOT include a candidate just because it is a famous large-cap AI/tech leader.
- Each candidate must have a specific current catalyst from recent earnings, guidance, analyst action, major news, clinical data, material contract/order, or clear sector leadership confirmed by fresh reporting.
- Overnight update should prioritize what is actually tradable near the US open, not what merely looked good the night before.
- Strong preference for names with actionable premarket context, fresh news flow, or clear opening-drive potential.
- Relative volume matters: if you cannot justify unusually strong participation versus normal activity, rank it lower or exclude it.
- Event quality matters more than brand recognition.
- Strong preference for single-name catalysts over generic sector sympathy.
- Do not use a stock as #3 if the thesis is mostly "the sector is strong" without a strong company-specific reason.
- If the third-best idea is materially weaker than #1 and #2, explicitly say the setup quality drops after the first two names.
- If only 2 names clearly qualify, still return 3, but the #3 must be labeled as a conditional watchlist name rather than a high-conviction setup.
- Avoid generic filler picks.
- Be skeptical and selective.

Ranking rules:
- Rank by opening tradability, not by company prestige.
- Penalize candidates with weak or ordinary relative volume.
- Penalize candidates lacking a fresh company-specific catalyst.
- Reward clean trigger levels, strong liquidity, obvious institutional participation, and reliable open-drive potential.

For each candidate, briefly cite the source basis in plain text, for example: 来源依据：Reuters / CNBC / Yahoo Finance / Nasdaq Market Activity.

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

高确信度做多候选
#1 股票代码 – 公司名称
催化剂：
做多逻辑：
来源依据：
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

条件观察名单（仅当高确信度机会不足时填写）
#3 股票代码 – 公司名称
候补原因：
做多逻辑：
来源依据：
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
仓位建议：轻仓 / 条件触发
信心评分：
结构评分：
胜率估计：

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
#3 ...（若为条件观察名单，请明确标注 Watchlist）

9:30–10:00 交易执行脚本

开盘备注
关键观察点

Keep it concise and readable in under two minutes.
EOF
)
OUTPUT="$(openclaw agent --agent trading-agent --timeout 600 --message "$PROMPT")"
printf '%s\n' "$OUTPUT" | tee "$OUTFILE" >/dev/null
openclaw message send --channel telegram --target "$TELEGRAM_TARGET" --message "$OUTPUT"
printf 'Saved overnight update to %s\n' "$OUTFILE"
