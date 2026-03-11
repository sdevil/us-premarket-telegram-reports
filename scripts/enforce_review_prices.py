#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

FIELDS = {
    '昨日开盘价': ('previous', 'open'),
    '昨日收盘价': ('previous', 'close'),
    '今日开盘价': ('latest', 'open'),
    '今日收盘价': ('latest', 'close'),
}


def build_price_map(ctx: dict) -> dict[str, dict[str, str]]:
    out = {}
    for ticker, payload in ctx.items():
        if not isinstance(payload, dict):
            continue
        daily = payload.get('daily_ohlc')
        if not isinstance(daily, dict):
            continue
        out[ticker.upper()] = daily
    return out


def replace_fields(section: str, daily: dict) -> str:
    for label, (bucket, key) in FIELDS.items():
        value = daily.get(bucket, {}).get(key, 'unavailable') if isinstance(daily.get(bucket), dict) else 'unavailable'
        section = re.sub(rf'{label}：.*', f'{label}：{value}', section)
    return section


def main() -> int:
    if len(sys.argv) != 3:
        print('Usage: enforce_review_prices.py <review-file> <market-context-json>', file=sys.stderr)
        return 2
    review_path = Path(sys.argv[1])
    ctx_path = Path(sys.argv[2])
    text = review_path.read_text(encoding='utf-8')
    ctx = json.loads(ctx_path.read_text(encoding='utf-8'))
    price_map = build_price_map(ctx)

    for ticker, daily in price_map.items():
        pattern = rf'((?:#\d+\s+)?{re.escape(ticker)}\s*[–-][\s\S]*?)(?=\n#\d+\s+|\n今日最佳与最差|\n复盘摘要（结构化）|\Z)'
        text = re.sub(pattern, lambda m: replace_fields(m.group(1), daily), text)

    review_path.write_text(text, encoding='utf-8')
    print(f'Enforced review OHLC fields in {review_path}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
