#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

RULES = [
    (
        r'波动相对可控，且入场与风控更容易预设成机械规则，较少依赖开盘瞬时微结构，更适合非盯盘的机械执行方案。它更适合预设机械触发、预设止损、且不依赖开盘前15分钟主观判断，',
        '波动相对可控，入场与风控可预设成机械规则，且较少依赖开盘前15分钟主观判断，',
    ),
    (
        r'强催化、强相对强度、最适合开盘后按量价动态确认',
        '强催化、强相对强度、依赖开盘后量价动态确认',
    ),
    (
        r'波动大、催化真实、开盘驱动潜力强，适合主动管理',
        '波动大、催化真实、依赖主动管理',
    ),
]


def main() -> int:
    if len(sys.argv) != 2:
        print('Usage: compress_track_reasoning.py <report-file>', file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    text = path.read_text(encoding='utf-8')
    for pat, repl in RULES:
        text = re.sub(pat, repl, text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    path.write_text(text, encoding='utf-8')
    print(f'Compressed track reasoning in {path}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
