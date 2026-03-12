#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

LIMIT = 3500


def split_text(text: str, limit: int = LIMIT) -> list[str]:
    text = text.strip()
    if len(text) <= limit:
        return [text]
    parts = []
    remaining = text
    while len(remaining) > limit:
        cut = remaining.rfind('\n\n', 0, limit)
        if cut == -1:
            cut = remaining.rfind('\n', 0, limit)
        if cut == -1:
            cut = limit
        parts.append(remaining[:cut].strip())
        remaining = remaining[cut:].strip()
    if remaining:
        parts.append(remaining)
    return parts


def main() -> int:
    if len(sys.argv) != 3:
        print('Usage: send_telegram_text_split.py <target> <text-file>', file=sys.stderr)
        return 2
    target = sys.argv[1]
    text = Path(sys.argv[2]).read_text(encoding='utf-8')
    parts = split_text(text)
    total = len(parts)
    for i, part in enumerate(parts, start=1):
        payload = part if total == 1 else f'（第{i}/{total}条）\n\n{part}'
        subprocess.run([
            'openclaw', 'message', 'send',
            '--channel', 'telegram',
            '--target', target,
            '--message', payload,
        ], check=True)
    print(f'Sent {total} Telegram message part(s)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
