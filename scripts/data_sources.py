#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
ENV = ROOT / '.env'
DEFAULT_HEADERS = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'}


def load_env(path: Path = ENV) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        os.environ.setdefault(k.strip(), v.strip())


def get_json(url: str, headers: dict[str, str] | None = None, timeout: int = 60):
    req = urllib.request.Request(url, headers=headers or DEFAULT_HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
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
    return get_json(f'https://api.polygon.io/v2/aggs/ticker/{urllib.parse.quote(symbol)}/prev?adjusted=true&apiKey={key}')


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
