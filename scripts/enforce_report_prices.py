#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PRICE_LABELS = {
    '昨日开盘价': 'open',
    '昨日收盘价': 'close',
    '昨日高点': 'high',
    '昨日低点': 'low',
}


def build_price_map(ctx: dict) -> dict[str, dict[str, str]]:
    out = {}
    for ticker, payload in ctx.items():
        if not isinstance(payload, dict):
            continue
        daily = payload.get('daily_ohlc')
        if not isinstance(daily, dict):
            continue
        prev = daily.get('previous')
        if isinstance(prev, dict):
            out[ticker.upper()] = {k: str(v) for k, v in prev.items() if v is not None}
    return out


def enforce_section(section: str, prices: dict[str, str]) -> str:
    for label, key in PRICE_LABELS.items():
        value = prices.get(key, 'unavailable')
        section = re.sub(rf'{label}：.*', f'{label}：{value}', section)
    return section


def main() -> int:
    if len(sys.argv) != 3:
        print('Usage: enforce_report_prices.py <report-file> <market-context-json>', file=sys.stderr)
        return 2
    report_path = Path(sys.argv[1])
    ctx_path = Path(sys.argv[2])
    text = report_path.read_text(encoding='utf-8')
    ctx = json.loads(ctx_path.read_text(encoding='utf-8'))
    price_map = build_price_map(ctx)

    for ticker, prices in price_map.items():
        # Replace within the block after "#n TICKER" or "TICKER –"
        pattern = rf'((?:#\d+\s+)?{re.escape(ticker)}\s*[–-][\s\S]*?)(?=\n#\d+\s+|\nTelegram 交易卡片|\n预测摘要（结构化）|\Z)'
        def repl(m):
            return enforce_section(m.group(1), prices)
        text = re.sub(pattern, repl, text)

    report_path.write_text(text, encoding='utf-8')
    print(f'Enforced previous-day OHLC fields in {report_path}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
