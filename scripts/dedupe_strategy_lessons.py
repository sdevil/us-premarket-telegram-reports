#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


def norm_text(text: str) -> str:
    return ' '.join(text.strip().split())


def main() -> int:
    if len(sys.argv) != 2:
        print('Usage: dedupe_strategy_lessons.py <strategy-lessons-jsonl>', file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    if not path.exists():
        print('No JSONL file found; nothing to dedupe.')
        return 0
    seen = set()
    kept = []
    for raw in path.read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        if not line:
            continue
        rec = json.loads(line)
        key = (
            rec.get('date'),
            rec.get('kind'),
            rec.get('ticker'),
            rec.get('category'),
            norm_text(rec.get('text', '')),
        )
        if key in seen:
            continue
        seen.add(key)
        kept.append(rec)
    path.write_text(''.join(json.dumps(rec, ensure_ascii=False) + '\n' for rec in kept), encoding='utf-8')
    print(f'Deduped {path}: kept {len(kept)} unique records')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
