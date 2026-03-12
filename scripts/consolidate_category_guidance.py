#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print('Usage: consolidate_category_guidance.py <strategy-lessons-jsonl>', file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    if not path.exists():
        print('No JSONL file found.')
        return 0

    records = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]
    bucketed = defaultdict(list)
    passthrough = []
    for rec in records:
        cat = rec.get('category')
        if cat in {'structure_execution', 'biotech_regulatory', 'macro_regime', 'track_assignment'} and rec.get('ticker') is None:
            bucketed[cat].append(rec)
        else:
            passthrough.append(rec)

    synthesized = []
    if bucketed['structure_execution']:
        synthesized.append({
            'date': bucketed['structure_execution'][-1].get('date'),
            'kind': 'reusable_lesson',
            'text': '财报股若隔夜大幅越过原Trigger，次日执行统一切换为 gap-and-go 框架，不再机械沿用静态前高突破计划',
            'ticker': None,
            'category': 'structure_execution',
        })
    if bucketed['biotech_regulatory']:
        synthesized.append({
            'date': bucketed['biotech_regulatory'][-1].get('date'),
            'kind': 'reusable_lesson',
            'text': 'biotech单股催化第二天是否继续可做，必须先看XBI是否同向确认；XBI转弱时默认降级',
            'ticker': None,
            'category': 'biotech_regulatory',
        })
    if bucketed['macro_regime']:
        synthesized.append({
            'date': bucketed['macro_regime'][-1].get('date'),
            'kind': 'reusable_lesson',
            'text': '在SPY走弱、油价高、SMH强、XBI弱的环境下，优先AI基础设施强股，降低biotech和弱催化票权重',
            'ticker': None,
            'category': 'macro_regime',
        })
    if bucketed['track_assignment']:
        synthesized.append({
            'date': bucketed['track_assignment'][-1].get('date'),
            'kind': 'track_assignment_lesson',
            'text': '强财报跳空股优先归入机器人轨道；缺少硬催化与异常量的权重股默认留在Watchlist，不升级为主交易标的',
            'ticker': None,
            'category': 'track_assignment',
        })

    final_records = passthrough + synthesized
    path.write_text(''.join(json.dumps(rec, ensure_ascii=False) + '\n' for rec in final_records), encoding='utf-8')
    print(f'Consolidated category guidance in {path}: synthesized {len(synthesized)} category rules')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
