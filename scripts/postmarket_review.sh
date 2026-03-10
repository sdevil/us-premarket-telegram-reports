#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
: "${TELEGRAM_TARGET:?Set TELEGRAM_TARGET to the Telegram chat target}"
TRADE_DATE="${TRADE_DATE:-$(TZ=America/New_York date +%F)}"
REPORT_DIR="${REPORT_DIR:-$(pwd)/reports}"
REVIEW_DIR="${REVIEW_DIR:-$(pwd)/reviews}"
mkdir -p "$REPORT_DIR" "$REVIEW_DIR"
PRIMARY_FILE="$REPORT_DIR/${TRADE_DATE}-primary.md"
OVERNIGHT_FILE="$REPORT_DIR/${TRADE_DATE}-overnight.md"
OUTFILE="$REVIEW_DIR/${TRADE_DATE}-postmarket-review.md"
[[ -f "$PRIMARY_FILE" ]] || { echo "Missing primary report: $PRIMARY_FILE" >&2; exit 1; }
PRIMARY_CONTENT="$(cat "$PRIMARY_FILE")"
if [[ -f "$OVERNIGHT_FILE" ]]; then
  OVERNIGHT_CONTENT="$(cat "$OVERNIGHT_FILE")"
else
  OVERNIGHT_CONTENT="No overnight update file was found for this trade date. Review the primary report and actual market action anyway."
fi
PROMPT=$(cat <<EOF
Review today's US equities trading session after the market close and evaluate the premarket recommendations.

Trade date: ${TRADE_DATE}

You must review the actual market action of the recommended names and keep improving the strategy over time.
Use only reliable English financial/market sources when checking what happened.
Final output must be entirely in Simplified Chinese except ticker symbols and terms like VIX, SPY, QQQ, VWAP, R/R, MFE, MAE.
Focus only on LONG setups from the S&P 500 and Nasdaq 100 universe.
Do not fabricate price action. If any data is unavailable, say unavailable explicitly.

Today's primary report:
${PRIMARY_CONTENT}

Today's overnight update:
${OVERNIGHT_CONTENT}

Review tasks:
- Check what actually happened after the open and by the close for the suggested names.
- Evaluate whether each trigger was hit, whether the breakout/follow-through was real or false, and whether the stop/target logic was reasonable.
- Separate research quality from execution quality.
- State clearly if a high-conviction idea did not deserve that ranking.
- State clearly if a Watchlist name should have stayed a watchlist or should have been upgraded.
- Identify recurring lessons that can improve future reports.
- Give concrete strategy adjustments for the next session.
- Evaluate whether ticker-specific drivers were used correctly. Example: TSLA should weight Musk/Tesla signals more; biotech should weight trial/FDA outcomes more.
- Evaluate whether macro-special-source interpretation was correct. Example: Trump/policy posts should usually affect market/sector weighting before single-stock ranking.

Required output format:
美股收盘后复盘
日期：YYYY-MM-DD

当日市场回顾
SPY：
QQQ：
VIX：
市场环境总结：

盘前建议复盘
#1 股票代码 – 结果评级（优秀 / 合格 / 失败）
是否触发：
开盘后表现：
收盘结果：
MFE：
MAE：
判断问题：
执行问题：
复盘结论：

#2 ... same structure
#3 ... same structure

今日最佳与最差
最佳 setup：
最差 setup：
原因：

策略学习
今天学到的 3 条：
1.
2.
3.

明日策略调整
应该提高权重的模式：
应该降低权重的模式：
Trigger 调整建议：
风控调整建议：

给明天盘前模型的提示
- 提示1
- 提示2
- 提示3

Ticker-specific 学习
哪些股票的自有特性今天最重要：
哪些股票今天不该套用通用逻辑：
哪些宏观/政策信号今天改变了排序：

Keep it concise but specific.
EOF
)
OUTPUT="$(openclaw agent --agent trading-agent --timeout 900 --message "$PROMPT")"
printf '%s\n' "$OUTPUT" | tee "$OUTFILE" >/dev/null
openclaw message send --channel telegram --target "$TELEGRAM_TARGET" --message "$OUTPUT"
printf 'Saved post-market review to %s\n' "$OUTFILE"
