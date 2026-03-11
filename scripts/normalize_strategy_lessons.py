#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def canonical_text(text: str) -> str:
    t = text.strip()
    replacements = {
        '次日执行必须切换为gap-and-go框架，不得机械沿用旧计划': '次日执行必须切换为gap-and-go框架，不得机械沿用静态前高突破计划',
        '财报后第二天是否还能继续走独立趋势': '财报后第二天是否仍能继续走独立趋势',
        '这类China销量驱动能否稳定转化为次日开盘延续': 'China销量驱动能否持续转化为多日资金追价',
        '在没有硬催化时，活跃成交是否足以支撑可重复的突破策略': '在没有硬催化时是否长期只适合作为Watchlist而非主交易标的',
        '必须同时检查XBI方向；若XBI转弱，则默认降级': '必须同时检查XBI方向；XBI转弱时默认降级',
    }
    for src, dst in replacements.items():
        t = t.replace(src, dst)
    t = re.sub(r'\s+', ' ', t)
    return t


def infer_category(text: str, current: str | None) -> str | None:
    if current:
        return current
    lower = text.lower()
    if 'xbi' in lower or '临床' in text or 'fda' in lower:
        return 'biotech_regulatory'
    if 'gap-and-go' in lower or 'trigger' in text or 'watchlist' in lower:
        return 'structure_execution'
    if '油价' in text or 'spy' in lower or 'smh' in lower or 'macro' in lower:
        return 'macro_regime'
    return current


def main() -> int:
    if len(sys.argv) != 2:
        print('Usage: normalize_strategy_lessons.py <strategy-lessons-jsonl>', file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    if not path.exists():
        print('No JSONL file found; nothing to normalize.')
        return 0
    records = []
    seen = set()
    for raw in path.read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        if not line:
            continue
        rec = json.loads(line)
        rec['text'] = canonical_text(rec.get('text', ''))
        rec['category'] = infer_category(rec.get('text', ''), rec.get('category'))
        key = (rec.get('date'), rec.get('kind'), rec.get('ticker'), rec.get('category'), rec.get('text'))
        if key in seen:
            continue
        seen.add(key)
        records.append(rec)
    path.write_text(''.join(json.dumps(rec, ensure_ascii=False) + '\n' for rec in records), encoding='utf-8')
    print(f'Normalized {path}: kept {len(records)} records')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
