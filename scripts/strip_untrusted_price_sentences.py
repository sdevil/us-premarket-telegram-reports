#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

# Remove common narrative patterns that restate yesterday OHLC numerically,
# because these are the easiest places for model drift to sneak in.
PATTERNS = [
    r'昨日从[^。\n]*?[开收高低点][^。\n]*[。]?',
    r'昨日[^。\n]*?开到[^。\n]*?收[^。\n]*[。]?',
    r'昨日[^。\n]*?收于[^。\n]*[。]?',
    r'昨日[^。\n]*?开于[^。\n]*?高于[^。\n]*?低于[^。\n]*?收于[^。\n]*[。]?',
]


def main() -> int:
    if len(sys.argv) != 2:
        print('Usage: strip_untrusted_price_sentences.py <report-file>', file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    text = path.read_text(encoding='utf-8')
    original = text
    for pat in PATTERNS:
        text = re.sub(pat, '', text)
    # Clean accidental double punctuation / blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'：\s*\n', '：\n', text)
    path.write_text(text, encoding='utf-8')
    changed = 'yes' if text != original else 'no'
    print(f'Stripped untrusted narrative price sentences from {path} (changed={changed})')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
