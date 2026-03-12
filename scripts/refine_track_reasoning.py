#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

REWRITE_RULES = [
    (
        r'更像“中等催化 \+ 更稳定执行”',
        '更适合预设机械触发、预设止损、且不依赖开盘前15分钟主观判断',
    ),
    (
        r'波动更可控、执行更机械',
        '波动相对可控，且入场与风控更容易预设成机械规则',
    ),
    (
        r'适合作为非盯盘手动方案',
        '更适合非盯盘的机械执行方案',
    ),
]


def main() -> int:
    if len(sys.argv) != 2:
        print('Usage: refine_track_reasoning.py <report-file>', file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    text = path.read_text(encoding='utf-8')
    for pat, repl in REWRITE_RULES:
        text = re.sub(pat, repl, text)
    path.write_text(text, encoding='utf-8')
    print(f'Refined track reasoning in {path}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
