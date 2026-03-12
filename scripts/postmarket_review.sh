#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
: "${TELEGRAM_TARGET:?Set TELEGRAM_TARGET to the Telegram chat target}"
TRADE_DATE="${TRADE_DATE:-$(TZ=America/New_York date +%F)}"
REPORT_DIR="${REPORT_DIR:-$(pwd)/reports}"
REVIEW_DIR="${REVIEW_DIR:-$(pwd)/reviews}"
LESSONS_FILE="${LESSONS_FILE:-$(pwd)/skills/us-premarket-telegram-reports/references/strategy-lessons.md}"
LESSONS_JSONL="${LESSONS_JSONL:-$(pwd)/skills/us-premarket-telegram-reports/references/strategy-lessons.jsonl}"
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
source "$(pwd)/scripts/common_env.sh"
MARKET_CONTEXT_FILE="$(mktemp)"
python3 "$(pwd)/scripts/build_market_context.py" review > "$MARKET_CONTEXT_FILE"
MARKET_CONTEXT="$(cat "$MARKET_CONTEXT_FILE")"
STRATEGY_GUIDANCE="$(python3 "$(pwd)/scripts/build_strategy_guidance.py")"
PROMPT=$(cat <<EOF
Review today's US equities trading session after the market close and evaluate the premarket recommendations.

Recent strategy lessons to respect and critique when relevant:
${STRATEGY_GUIDANCE}

Structured market context (use this for index/rates/oil/macro context; supplement with fresh English financial sources as needed):
${MARKET_CONTEXT}

Trade date: ${TRADE_DATE}

You must review the actual market action of the recommended names and keep improving the strategy over time.
Use only reliable English financial/market sources when checking what happened.
Use the structured market context above as the default backbone for index/rates/oil/macro context before supplementing with broader reporting.
Final output must be entirely in Simplified Chinese except ticker symbols and terms like VIX, SPY, QQQ, VWAP, R/R, MFE, MAE.
Focus only on LONG setups from the S&P 500 and Nasdaq 100 universe.
Do not fabricate price action. If any data is unavailable, say unavailable explicitly.
Include yesterday and today open/close values for each reviewed ticker when available.
Use daily_ohlc from structured data as the strict source for yesterday/today OHLC fields when available, and never guess these numbers from prose or memory.
Historical fact fields in review are limited to: 昨日开盘价 / 昨日收盘价 / 今日开盘价 / 今日收盘价.
Treat all other levels or execution notes as analysis rather than historical facts.

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
- Evaluate whether the structured market context was used correctly or ignored when it should have been decisive.
- Evaluate separately whether the setup was more suitable for active monitoring or non-monitoring execution.
- Evaluate whether each stock was assigned to the correct execution track.
- For each reviewed stock, state the most important reason the assigned track was correct or incorrect.
- Evaluate whether recent stored strategy lessons were applied correctly, misapplied, or should now be revised.
- For every meaningful mismatch between forecast and reality, identify the main reason category: macro regime mismatch, sector mismatch, ticker-specific catalyst mismatch, structure/volume mismatch, or execution-rule mismatch.
- Convert the mismatch into future watchpoints that should matter next time this stock or setup appears.
- When a lesson feels durable, write it as a reusable rule instead of a one-off comment.

Required output format:
美股收盘后复盘
日期：YYYY-MM-DD

当日市场回顾
SPY：
QQQ：
VIX：
市场环境总结：

机器人 / 盯盘轨道复盘
#1 股票代码 – 结果评级（优秀 / 合格 / 失败）
昨日开盘价：
昨日收盘价：
今日开盘价：
今日收盘价：
今日高点：
今日低点：
盯盘版结果：
轨道分配是否正确：
轨道分配核心原因：
是否触发：
开盘后表现：
收盘结果：
MFE：
MAE：
判断问题：
执行问题：
偏差归因类别：
导致出入的核心原因：
下次再做这只股票/这类 setup 时要多看什么：
复盘结论：

#2 ... same structure

非盯盘手动轨道复盘
#1 股票代码 – 结果评级（优秀 / 合格 / 失败）
昨日开盘价：
昨日收盘价：
今日开盘价：
今日收盘价：
今日高点：
今日低点：
非盯盘版结果：
轨道分配是否正确：
轨道分配核心原因：
是否触发：
开盘后表现：
收盘结果：
MFE：
MAE：
判断问题：
执行问题：
偏差归因类别：
导致出入的核心原因：
下次再做这只股票/这类 setup 时要多看什么：
复盘结论：

#2 ... same structure

今日最佳与最差
最佳 setup：
最差 setup：
原因：

复盘摘要（结构化）
best_setup:
worst_setup:
main_mismatch_categories:
- 
- 
- 
monitoring_suitability_summary:
non_monitoring_suitability_summary:
track_assignment_lessons:
- 
- 
next_session_adjustments:
- 
- 
- 

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

长期规则候选
值得写回长期规则的内容：
未来需要持续跟踪的关注点：

Keep it concise but specific.
EOF
)
OUTPUT="$(openclaw agent --agent trading-agent --timeout 900 --message "$PROMPT")"
printf '%s\n' "$OUTPUT" | tee "$OUTFILE" >/dev/null
python3 "$(pwd)/scripts/enforce_review_prices.py" "$OUTFILE" "$MARKET_CONTEXT_FILE"
python3 "$(pwd)/scripts/extract_strategy_lessons.py" "$OUTFILE" "$LESSONS_FILE" "$LESSONS_JSONL"
FINAL_OUTPUT="$(cat "$OUTFILE")"
openclaw message send --channel telegram --target "$TELEGRAM_TARGET" --message "$FINAL_OUTPUT"
printf 'Saved post-market review to %s\n' "$OUTFILE"
printf 'Updated strategy lessons at %s\n' "$LESSONS_FILE"
printf 'Updated structured lessons at %s\n' "$LESSONS_JSONL"
rm -f "$MARKET_CONTEXT_FILE"
