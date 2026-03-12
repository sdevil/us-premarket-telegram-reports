#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path


def normalize_block(block: str) -> str:
    lines = block.splitlines()
    out = []
    for line in lines:
        if re.match(r'^- ticker:', line):
            out.append('  ' + line)
        elif re.match(r'^(trigger|entry|stop|target|size|setup_score|win_probability):', line):
            out.append('    ' + line)
        else:
            out.append(line)
    return '\n'.join(out)


def main() -> int:
    if len(sys.argv) != 2:
        print('Usage: normalize_execution_blocks.py <report>', file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    text = path.read_text(encoding='utf-8')
    for header in ['robot_track_orders:', 'manual_track_orders:']:
        idx = text.find(header)
        if idx == -1:
            continue
    text = re.sub(r'(?ms)(robot_track_orders:\n.*?)(\n\nmanual_track_orders:)', lambda m: normalize_block(m.group(1)) + m.group(2), text)
    text = re.sub(r'(?ms)(manual_track_orders:\n.*?)(\n\nTelegram 交易卡片)', lambda m: normalize_block(m.group(1)) + m.group(2), text)
    path.write_text(text, encoding='utf-8')
    print(f'Normalized execution blocks in {path}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
