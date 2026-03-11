#!/usr/bin/env python3
from __future__ import annotations

import json
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


def append_markdown(lessons_path: Path, trade_date: str, durable_items: list[str], watch_items: list[str]) -> None:
    chunk = [f"\n### {trade_date}"]
    for item in durable_items:
        chunk.append(f"- Reusable lesson: {item}")
    for item in watch_items:
        chunk.append(f"- Future watchpoint: {item}")
    chunk.append("")
    with lessons_path.open("a", encoding="utf-8") as f:
        f.write("\n".join(chunk))


def classify_text(text: str) -> tuple[str | None, str | None]:
    upper = text.upper()
    ticker = None
    for candidate in ["TSLA", "AAPL", "NVDA", "ORCL", "VRTX", "MU", "AVGO", "AMD", "SMCI", "META", "AMZN", "MSFT", "GOOGL", "LLY", "REGN"]:
        if candidate in upper:
            ticker = candidate
            break
    category = None
    lower = text.lower()
    if any(k in lower for k in ["macro", "油价", "中东", "伊朗", "fed", "rates", "关税", "sanction", "vix"]):
        category = "macro_regime"
    elif any(k in lower for k in ["trial", "fda", "clinical", "临床", "监管"]):
        category = "biotech_regulatory"
    elif any(k in lower for k in ["musk", "tesla", "robotaxi", "fsd"]):
        category = "ticker_specific_tsla"
    elif any(k in lower for k in ["volume", "breakout", "突破", "vwap", "trigger", "开盘"]):
        category = "structure_execution"
    return ticker, category


def append_jsonl(jsonl_path: Path, trade_date: str, durable_items: list[str], watch_items: list[str]) -> None:
    with jsonl_path.open("a", encoding="utf-8") as f:
        for kind, items in [("reusable_lesson", durable_items), ("future_watchpoint", watch_items)]:
            for item in items:
                ticker, category = classify_text(item)
                rec = {
                    "date": trade_date,
                    "kind": kind,
                    "text": item,
                    "ticker": ticker,
                    "category": category,
                }
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def main() -> int:
    if len(sys.argv) not in {3, 4}:
        print("Usage: extract_strategy_lessons.py <review-file> <strategy-lessons-file> [strategy-lessons-jsonl]", file=sys.stderr)
        return 2

    review_path = Path(sys.argv[1])
    lessons_path = Path(sys.argv[2])
    jsonl_path = Path(sys.argv[3]) if len(sys.argv) == 4 else None
    text = review_path.read_text(encoding="utf-8")

    date_match = re.search(r"日期：\s*(\d{4}-\d{2}-\d{2})", text)
    trade_date = date_match.group(1) if date_match else review_path.stem[:10]

    durable = extract_section(text, "长期规则候选")
    watchpoints = extract_section(text, "未来需要持续跟踪的关注点：")
    if not watchpoints:
        tail = text.split("长期规则候选", 1)[-1] if "长期规则候选" in text else ""
        m = re.search(r"未来需要持续跟踪的关注点：\n(.*)$", tail, re.S)
        watchpoints = m.group(1).strip() if m else ""

    durable_items = extract_bullets(durable)
    watch_items = extract_bullets(watchpoints)

    if not durable_items and not watch_items:
        print("No durable lessons found; nothing appended.")
        return 0

    append_markdown(lessons_path, trade_date, durable_items, watch_items)
    if jsonl_path is not None:
        append_jsonl(jsonl_path, trade_date, durable_items, watch_items)

    print(f"Appended lessons for {trade_date} to {lessons_path}")
    if jsonl_path is not None:
        print(f"Updated structured lessons at {jsonl_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
