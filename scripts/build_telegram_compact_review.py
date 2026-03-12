#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

SECTIONS = [
    '美股收盘后复盘',
    '当日市场回顾',
    '机器人 / 盯盘轨道复盘',
    '非盯盘手动轨道复盘',
    '今日最佳与最差',
    '复盘摘要（结构化）',
    '明日策略调整',
    '给明天盘前模型的提示',
]


def extract(text: str, start: str, end_markers: list[str]) -> str:
    idx = text.find(start)
    if idx == -1:
        return ''
    sub = text[idx:]
    ends = [sub.find(m) for m in end_markers if sub.find(m) != -1 and m != start]
    end = min(ends) if ends else len(sub)
    return sub[:end].strip()


def main() -> int:
    if len(sys.argv) != 3:
        print('Usage: build_telegram_compact_review.py <full-review> <compact-output>', file=sys.stderr)
        return 2
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    text = src.read_text(encoding='utf-8')
    parts = []
    for s in SECTIONS:
        sec = extract(text, s, SECTIONS)
        if sec:
            parts.append(sec)
    dst.write_text('\n\n'.join(parts).strip(), encoding='utf-8')
    print(f'Built compact Telegram review at {dst}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
