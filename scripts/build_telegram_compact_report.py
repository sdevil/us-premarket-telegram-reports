#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path


def extract(text: str, start: str, end_markers: list[str]) -> str:
    idx = text.find(start)
    if idx == -1:
        return ''
    sub = text[idx:]
    end_positions = [sub.find(m) for m in end_markers if sub.find(m) != -1 and m != start]
    end = min(end_positions) if end_positions else len(sub)
    return sub[:end].strip()


def main() -> int:
    if len(sys.argv) != 3:
        print('Usage: build_telegram_compact_report.py <full-report> <compact-output>', file=sys.stderr)
        return 2
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    text = src.read_text(encoding='utf-8')

    parts = []
    for header in ['美股盘前做多观察名单', '今日交易环境评估', '机器人 / 盯盘执行候选', '非盯盘手动执行候选', '仅观察名单（可选）', '预测摘要（结构化）', '开盘执行要点', '开盘备注', '关键观察点']:
        section = extract(text, header, ['机器人 / 盯盘执行候选', '非盯盘手动执行候选', '仅观察名单（可选）', '预测摘要（结构化）', '执行接口摘要（结构化）', 'Telegram 交易卡片', '开盘执行要点', '开盘备注', '关键观察点'])
        if section:
            parts.append(section)

    compact = '\n\n'.join(parts)
    compact = re.sub(r'\n{3,}', '\n\n', compact).strip()
    dst.write_text(compact, encoding='utf-8')
    print(f'Built compact Telegram report at {dst}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
