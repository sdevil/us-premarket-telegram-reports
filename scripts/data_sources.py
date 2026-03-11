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


def alpha_daily_ohlc(symbol: str):
    key = urllib.parse.quote(os.environ['ALPHA_VANTAGE_API_KEY'])
    data = get_json(f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={urllib.parse.quote(symbol)}&outputsize=compact&apikey={key}')
    series = data.get('Time Series (Daily)', {})
    if not series:
        return {'unavailable': True, 'error': 'missing daily series'}
    dates = sorted(series.keys(), reverse=True)
    out = {'latest_date': dates[0] if dates else None, 'source': 'alpha_vantage'}
    if len(dates) >= 1:
        d0 = series[dates[0]]
        out['latest'] = {
            'date': dates[0],
            'open': d0.get('1. open'),
            'high': d0.get('2. high'),
            'low': d0.get('3. low'),
            'close': d0.get('4. close'),
        }
    if len(dates) >= 2:
        d1 = series[dates[1]]
        out['previous'] = {
            'date': dates[1],
            'open': d1.get('1. open'),
            'high': d1.get('2. high'),
            'low': d1.get('3. low'),
            'close': d1.get('4. close'),
        }
    return out


def twelve_daily_ohlc(symbol: str):
    key = urllib.parse.quote(os.environ['TWELVE_DATA_API_KEY'])
    data = get_json(
        f'https://api.twelvedata.com/time_series?symbol={urllib.parse.quote(symbol)}&interval=1day&outputsize=2&apikey={key}',
        headers=DEFAULT_HEADERS,
    )
    values = data.get('values', [])
    if not values:
        return {'unavailable': True, 'error': 'missing time series'}
    out = {'latest_date': values[0].get('datetime'), 'source': 'twelve_data'}
    if len(values) >= 1:
        d0 = values[0]
        out['latest'] = {
            'date': d0.get('datetime'),
            'open': d0.get('open'),
            'high': d0.get('high'),
            'low': d0.get('low'),
            'close': d0.get('close'),
        }
    if len(values) >= 2:
        d1 = values[1]
        out['previous'] = {
            'date': d1.get('datetime'),
            'open': d1.get('open'),
            'high': d1.get('high'),
            'low': d1.get('low'),
            'close': d1.get('close'),
        }
    return out


def strict_daily_ohlc(symbol: str):
    primary = twelve_daily_ohlc(symbol)
    if isinstance(primary, dict) and not primary.get('unavailable') and primary.get('previous'):
        return primary
    fallback = alpha_daily_ohlc(symbol)
    return fallback
