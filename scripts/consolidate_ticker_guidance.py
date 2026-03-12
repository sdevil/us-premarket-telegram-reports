#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print('Usage: consolidate_ticker_guidance.py <strategy-lessons-jsonl>', file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    if not path.exists():
        print('No JSONL file found.')
        return 0

    records = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]
    by_ticker = defaultdict(list)
    others = []
    for rec in records:
        ticker = rec.get('ticker')
        if rec.get('kind') == 'future_watchpoint' and ticker:
            by_ticker[ticker].append(rec)
        else:
            others.append(rec)

    synthesized = []
    for ticker, recs in by_ticker.items():
        texts = [r.get('text', '') for r in recs]
        if ticker == 'ORCL':
            text = 'ORCL财报后强势延续能否从第二天持续到第三天，还是转为缺口回吐与高位换手'
        elif ticker == 'TSLA':
            text = 'TSLA China销量硬数据是否足以支持更早升级，以及能否持续转化为多日资金追价'
        elif ticker == 'NVDA':
            text = 'NVDA在缺少硬催化时是否应继续维持Watchlist，而不是升级为主交易标的'
        else:
            text = texts[0]
        synthesized.append({
            'date': recs[-1].get('date'),
            'kind': 'future_watchpoint',
            'text': text,
            'ticker': ticker,
            'category': recs[-1].get('category'),
        })

    final_records = others + synthesized
    path.write_text(''.join(json.dumps(rec, ensure_ascii=False) + '\n' for rec in final_records), encoding='utf-8')
    print(f'Consolidated ticker guidance in {path}: {len(synthesized)} ticker watchpoints synthesized')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
