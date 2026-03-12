#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

HEADERS = [
    '机器人 / 盯盘执行候选',
    '非盯盘手动执行候选',
    '仅观察名单（可选）',
    '预测摘要（结构化）',
]


def ensure_header(text: str, header: str, before: str | None = None, placeholder: str | None = None) -> str:
    if header in text:
        return text
    insert = header + '\n'
    if placeholder:
        insert += placeholder.rstrip() + '\n\n'
    if before and before in text:
        return text.replace(before, insert + before)
    return text.rstrip() + '\n\n' + insert


def main() -> int:
    if len(sys.argv) != 2:
        print('Usage: enforce_dual_track_structure.py <report-file>', file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    text = path.read_text(encoding='utf-8')

    text = ensure_header(
        text,
        '机器人 / 盯盘执行候选',
        before='非盯盘手动执行候选',
        placeholder='该轨道今日无合格候选。',
    )
    text = ensure_header(
        text,
        '非盯盘手动执行候选',
        before='仅观察名单（可选）',
        placeholder='该轨道今日无合格候选。',
    )
    text = ensure_header(
        text,
        '仅观察名单（可选）',
        before='预测摘要（结构化）',
        placeholder='该名单今日为空。',
    )
    text = ensure_header(
        text,
        '预测摘要（结构化）',
        before='Telegram 交易卡片',
        placeholder='market_suitability:\nrisk_level:\nmacro_drivers:\n- \n- \n- \nmonitoring_candidates:\n- \n- \nnon_monitoring_candidates:\n- \n- \nwatchlist_ticker:\nprediction_notes:\n- \n- \n-',
    )

    path.write_text(text, encoding='utf-8')
    print(f'Enforced dual-track structure in {path}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
