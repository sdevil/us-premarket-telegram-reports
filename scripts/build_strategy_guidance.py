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
    for rec in records[-20:]:
        text = rec.get('text', '')
        ticker = rec.get('ticker')
        if ticker:
            by_ticker.setdefault(ticker, []).append(text)
        else:
            summary.append(text)
    # keep recent concise slices
    out = {
        'summary': summary[-6:],
        'by_ticker': {k: v[-4:] for k, v in by_ticker.items()},
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
