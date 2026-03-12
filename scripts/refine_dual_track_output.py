#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

REPLACEMENTS = [
    (r'该轨道今日无合格候选。', '该轨道今日无合格候选，维持空仓等待更清晰机会。'),
    (r'该轨道今日无第二个合格候选。', '该轨道今日无第二个合格候选，不强行凑数。'),
    (r'仅观察名单（可选）\n#1 股票代码 – 公司名称\n原因：', '仅观察名单（可选）\n若无明确观察标的，可写：该名单今日为空。'),
    (r'建议执行方式：机器人执行 / 需要盯盘确认 / 仅观察', '建议执行方式：请填写单一明确选择'),
    (r'建议执行方式：非盯盘可做 / 需要盯盘确认 / 仅观察', '建议执行方式：请填写单一明确选择'),
]


def main() -> int:
    if len(sys.argv) != 2:
        print('Usage: refine_dual_track_output.py <report-file>', file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    text = path.read_text(encoding='utf-8')
    for pat, repl in REPLACEMENTS:
        text = re.sub(pat, repl, text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    path.write_text(text, encoding='utf-8')
    print(f'Refined dual-track output in {path}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
