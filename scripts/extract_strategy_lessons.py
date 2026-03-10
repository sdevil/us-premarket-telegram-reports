#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path


def extract_section(text: str, heading: str) -> str:
    pattern = rf"{re.escape(heading)}\n(.*?)(?:\n[A-ZA-Za-z一-龥].*：|\n[A-ZA-Za-z一-龥].*:\s*|\Z)"
    m = re.search(pattern, text, re.S)
    return m.group(1).strip() if m else ""


def extract_bullets(block: str) -> list[str]:
    lines = []
    for raw in block.splitlines():
        s = raw.strip()
        if not s:
            continue
        if s in {"值得写回长期规则的内容：", "未来需要持续跟踪的关注点：", "长期规则候选"}:
            continue
        s = re.sub(r"^[\-•*]\s*", "", s)
        s = re.sub(r"^\d+[\.)、]\s*", "", s)
        if s:
            lines.append(s)
    return lines


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: extract_strategy_lessons.py <review-file> <strategy-lessons-file>", file=sys.stderr)
        return 2

    review_path = Path(sys.argv[1])
    lessons_path = Path(sys.argv[2])
    text = review_path.read_text(encoding="utf-8")

    date_match = re.search(r"日期：\s*(\d{4}-\d{2}-\d{2})", text)
    trade_date = date_match.group(1) if date_match else review_path.stem[:10]

    durable = extract_section(text, "长期规则候选")
    watchpoints = extract_section(text, "未来需要持续跟踪的关注点：")
    if not watchpoints:
        # fallback if captured inside same section or not present as own heading
        tail = text.split("长期规则候选", 1)[-1] if "长期规则候选" in text else ""
        m = re.search(r"未来需要持续跟踪的关注点：\n(.*)$", tail, re.S)
        watchpoints = m.group(1).strip() if m else ""

    durable_items = extract_bullets(durable)
    watch_items = extract_bullets(watchpoints)

    if not durable_items and not watch_items:
        print("No durable lessons found; nothing appended.")
        return 0

    chunk = [f"\n### {trade_date}"]
    if durable_items:
        for item in durable_items:
            chunk.append(f"- Reusable lesson: {item}")
    if watch_items:
        for item in watch_items:
            chunk.append(f"- Future watchpoint: {item}")
    chunk.append("")

    with lessons_path.open("a", encoding="utf-8") as f:
        f.write("\n".join(chunk))

    print(f"Appended lessons for {trade_date} to {lessons_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
