#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
ENV = ROOT / '.env'


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        os.environ.setdefault(k.strip(), v.strip())


def get_json(url: str, headers: dict[str, str] | None = None):
    req = urllib.request.Request(url, headers=headers or {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode('utf-8'))


def best_effort(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Exception as exc:
        return {'unavailable': True, 'error': str(exc)}


def finnhub_quote(symbol: str):
    key = urllib.parse.quote(os.environ['FINNHUB_API_KEY'])
    return get_json(f'https://finnhub.io/api/v1/quote?symbol={urllib.parse.quote(symbol)}&token={key}')


def finnhub_news(symbol: str, frm: str, to: str):
    key = urllib.parse.quote(os.environ['FINNHUB_API_KEY'])
    return get_json(f'https://finnhub.io/api/v1/company-news?symbol={urllib.parse.quote(symbol)}&from={frm}&to={to}&token={key}')


def polygon_prev(symbol: str):
    key = urllib.parse.quote(os.environ['POLYGON_API_KEY'])
    try:
        return get_json(f'https://api.polygon.io/v2/aggs/ticker/{urllib.parse.quote(symbol)}/prev?adjusted=true&apiKey={key}')
    except Exception:
        return None


def fred_latest(series: str):
    key = urllib.parse.quote(os.environ['FRED_API_KEY'])
    data = get_json(f'https://api.stlouisfed.org/fred/series/observations?series_id={series}&api_key={key}&file_type=json&limit=1&sort_order=desc')
    obs = data.get('observations', [])
    return obs[-1] if obs else None


def te_calendar():
    login = urllib.parse.quote(os.environ['TRADING_ECONOMICS_LOGIN'])
    return get_json(f'https://api.tradingeconomics.com/calendar?c={login}&f=json')


def eia_brent():
    key = urllib.parse.quote(os.environ['EIA_API_KEY'])
    data = get_json(f'https://api.eia.gov/v2/petroleum/pri/spt/data/?api_key={key}&frequency=daily&data[0]=value&facets[product][]=EPCBRENT&sort[0][column]=period&sort[0][direction]=desc&length=1')
    rows = data.get('response', {}).get('data', [])
    return rows[0] if rows else None


def main() -> int:
    load_env(ENV)
    mode = sys.argv[1] if len(sys.argv) > 1 else 'premarket'
    out = {}
    for sym in ['SPY', 'QQQ', 'NVDA', 'AAPL', 'TSLA']:
        out[sym] = {
            'quote': best_effort(finnhub_quote, sym),
        }
    for sym in ['SPY', 'QQQ']:
        out[sym]['prev'] = best_effort(polygon_prev, sym)
    out['vix'] = best_effort(finnhub_quote, '^VIX')
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
        out['ticker_news_sample'] = {
            'NVDA': nvda_news[:3] if isinstance(nvda_news, list) else nvda_news,
            'TSLA': tsla_news[:3] if isinstance(tsla_news, list) else tsla_news,
            'AAPL': aapl_news[:3] if isinstance(aapl_news, list) else aapl_news,
        }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
