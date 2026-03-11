#!/usr/bin/env python3
from __future__ import annotations

import json
import sys

from data_sources import (
    best_effort,
    eia_brent,
    finnhub_news,
    finnhub_quote,
    fred_latest,
    load_env,
    polygon_prev,
    te_calendar,
)


def main() -> int:
    load_env()
    mode = sys.argv[1] if len(sys.argv) > 1 else 'premarket'
    out = {}
    for sym in ['SPY', 'QQQ', 'NVDA', 'AAPL', 'TSLA', 'ORCL', 'VRTX']:
        out[sym] = {
            'quote': best_effort(finnhub_quote, sym),
        }
    for sym in ['SPY', 'QQQ']:
        out[sym]['prev'] = best_effort(polygon_prev, sym)
    out['vix'] = best_effort(finnhub_quote, '^VIX')
    out['sectors'] = {
        'XLK': {'quote': best_effort(finnhub_quote, 'XLK')},
        'XLE': {'quote': best_effort(finnhub_quote, 'XLE')},
        'XBI': {'quote': best_effort(finnhub_quote, 'XBI')},
        'SMH': {'quote': best_effort(finnhub_quote, 'SMH')},
    }
    out['context_notes'] = [
        'Polygon prev data is optional fallback only; do not fail the whole report if it is unavailable or rate-limited.',
        'Use Finnhub quote as the primary lightweight market snapshot source.',
    ]
    out['rates'] = {
        'DGS10': best_effort(fred_latest, 'DGS10'),
        'DGS2': best_effort(fred_latest, 'DGS2'),
    }
    out['oil'] = best_effort(eia_brent)
    cal = best_effort(te_calendar)
    out['calendar_sample'] = cal[:8] if isinstance(cal, list) else cal
    if mode == 'premarket':
        nvda_news = best_effort(finnhub_news, 'NVDA', '2026-03-08', '2026-03-11')
        tsla_news = best_effort(finnhub_news, 'TSLA', '2026-03-08', '2026-03-11')
        aapl_news = best_effort(finnhub_news, 'AAPL', '2026-03-08', '2026-03-11')
        orcl_news = best_effort(finnhub_news, 'ORCL', '2026-03-08', '2026-03-11')
        vrtx_news = best_effort(finnhub_news, 'VRTX', '2026-03-08', '2026-03-11')
        out['ticker_news_sample'] = {
            'NVDA': nvda_news[:3] if isinstance(nvda_news, list) else nvda_news,
            'TSLA': tsla_news[:3] if isinstance(tsla_news, list) else tsla_news,
            'AAPL': aapl_news[:3] if isinstance(aapl_news, list) else aapl_news,
            'ORCL': orcl_news[:3] if isinstance(orcl_news, list) else orcl_news,
            'VRTX': vrtx_news[:3] if isinstance(vrtx_news, list) else vrtx_news,
        }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
