#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path


def canonical_watchpoint(text: str) -> str:
    t = text.strip()
    t = t.replace('是否还能继续走独立趋势', '是否仍能维持独立趋势')
    t = t.replace('是否仍能走出独立趋势而非仅剩缺口回吐', '是否仍能维持独立趋势而非转为缺口回吐')
    t = t.replace('China销量驱动能否持续转化为多日资金追价', 'China销量硬数据能否持续转化为多日资金追价')
    t = t.replace('China销量硬数据是否应在未来更早升级', 'China销量硬数据是否应更早升级')
    t = t.replace('在没有硬催化时是否长期只适合作为Watchlist而非主交易标的', '在缺少硬催化时是否应维持Watchlist而非主交易标的')
    t = re.sub(r'\s+', ' ', t)
    return t


def main() -> int:
    if len(sys.argv) != 2:
        print('Usage: merge_ticker_watchpoints.py <strategy-lessons-jsonl>', file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    if not path.exists():
        print('No JSONL file found.')
        return 0
    records = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]
    seen = set()
    merged = []
    for rec in records:
        if rec.get('kind') == 'future_watchpoint' and rec.get('ticker'):
            rec['text'] = canonical_watchpoint(rec.get('text', ''))
        key = (rec.get('date'), rec.get('kind'), rec.get('ticker'), rec.get('category'), rec.get('text'))
        if key in seen:
            continue
        seen.add(key)
        merged.append(rec)
    path.write_text(''.join(json.dumps(rec, ensure_ascii=False) + '\n' for rec in merged), encoding='utf-8')
    counts = defaultdict(int)
    for rec in merged:
        if rec.get('ticker'):
            counts[rec['ticker']] += 1
    print(f'Merged watchpoints in {path}')
    for k in sorted(counts):
        print(f'{k}: {counts[k]} records')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
