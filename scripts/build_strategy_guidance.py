#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSONL = ROOT / 'skills/us-premarket-telegram-reports/references/strategy-lessons.jsonl'


def main() -> int:
    if not JSONL.exists():
        print('{"summary": [], "by_ticker": {}}')
        return 0
    records = [json.loads(line) for line in JSONL.read_text(encoding='utf-8').splitlines() if line.strip()]
    summary = []
    by_ticker: dict[str, list[str]] = {}
    by_category: dict[str, list[str]] = {}
    for rec in records[-30:]:
        text = rec.get('text', '')
        ticker = rec.get('ticker')
        category = rec.get('category')
        if ticker:
            by_ticker.setdefault(ticker, []).append(text)
        else:
            summary.append(text)
        if category:
            by_category.setdefault(category, []).append(text)
    out = {
        'summary': summary[-6:],
        'by_ticker': {k: v[-4:] for k, v in by_ticker.items()},
        'by_category': {k: v[-4:] for k, v in by_category.items()},
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
