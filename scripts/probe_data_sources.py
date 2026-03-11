#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
ENV = ROOT / ".env"


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def get_json(url: str, headers: dict[str, str] | None = None) -> object:
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def probe_finnhub() -> tuple[bool, str]:
    key = os.environ.get("FINNHUB_API_KEY")
    data = get_json(f"https://finnhub.io/api/v1/quote?symbol=AAPL&token={urllib.parse.quote(key or '')}")
    return (isinstance(data, dict) and "c" in data, f"quote keys={list(data)[:5]}")


def probe_alpha_vantage() -> tuple[bool, str]:
    key = os.environ.get("ALPHA_VANTAGE_API_KEY")
    data = get_json(f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=IBM&apikey={urllib.parse.quote(key or '')}")
    ok = isinstance(data, dict) and "Global Quote" in data
    return ok, f"keys={list(data)[:4]}"


def probe_fred() -> tuple[bool, str]:
    key = os.environ.get("FRED_API_KEY")
    data = get_json(f"https://api.stlouisfed.org/fred/series/observations?series_id=DGS10&api_key={urllib.parse.quote(key or '')}&file_type=json&limit=1&sort_order=desc")
    ok = isinstance(data, dict) and "observations" in data
    return ok, f"count={len(data.get('observations', [])) if isinstance(data, dict) else 0}"


def probe_fmp() -> tuple[bool, str]:
    key = os.environ.get("FMP_API_KEY")
    data = get_json(f"https://financialmodelingprep.com/stable/quote?symbol=AAPL&apikey={urllib.parse.quote(key or '')}")
    ok = isinstance(data, list) and len(data) > 0
    return ok, f"items={len(data) if isinstance(data, list) else 'n/a'}"


def probe_newsapi() -> tuple[bool, str]:
    key = os.environ.get("NEWSAPI_API_KEY")
    data = get_json(f"https://newsapi.org/v2/everything?q=Apple&language=en&pageSize=1&apiKey={urllib.parse.quote(key or '')}")
    ok = isinstance(data, dict) and data.get("status") == "ok"
    return ok, f"totalResults={data.get('totalResults') if isinstance(data, dict) else 'n/a'}"


def probe_trading_economics() -> tuple[bool, str]:
    login = os.environ.get("TRADING_ECONOMICS_LOGIN")
    data = get_json(f"https://api.tradingeconomics.com/calendar?c={urllib.parse.quote(login or '')}&f=json")
    ok = isinstance(data, list)
    return ok, f"items={len(data) if isinstance(data, list) else 'n/a'}"


def probe_eia() -> tuple[bool, str]:
    key = os.environ.get("EIA_API_KEY")
    data = get_json(f"https://api.eia.gov/v2/petroleum/pri/spt/data/?api_key={urllib.parse.quote(key or '')}&frequency=daily&data[0]=value&facets[product][]=EPCBRENT&sort[0][column]=period&sort[0][direction]=desc&length=1")
    ok = isinstance(data, dict) and data.get("response", {}).get("data")
    return ok, f"items={len(data.get('response', {}).get('data', [])) if isinstance(data, dict) else 'n/a'}"


def probe_twelve_data() -> tuple[bool, str]:
    key = os.environ.get("TWELVE_DATA_API_KEY")
    data = get_json(
        f"https://api.twelvedata.com/quote?symbol=AAPL&apikey={urllib.parse.quote(key or '')}",
        headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"},
    )
    ok = isinstance(data, dict) and data.get("symbol") == "AAPL"
    return ok, f"symbol={data.get('symbol') if isinstance(data, dict) else 'n/a'}"


def probe_polygon() -> tuple[bool, str]:
    key = os.environ.get("POLYGON_API_KEY")
    data = get_json(f"https://api.polygon.io/v2/aggs/ticker/AAPL/prev?adjusted=true&apiKey={urllib.parse.quote(key or '')}")
    ok = isinstance(data, dict) and data.get("status") == "OK"
    return ok, f"results={len(data.get('results', [])) if isinstance(data, dict) else 'n/a'}"


PROBES = [
    ("finnhub", probe_finnhub),
    ("alpha_vantage", probe_alpha_vantage),
    ("fred", probe_fred),
    ("fmp", probe_fmp),
    ("newsapi", probe_newsapi),
    ("trading_economics", probe_trading_economics),
    ("eia", probe_eia),
    ("twelve_data", probe_twelve_data),
    ("polygon", probe_polygon),
]


def main() -> int:
    load_env(ENV)
    failed = False
    for name, fn in PROBES:
        try:
            ok, detail = fn()
            status = "OK" if ok else "FAIL"
            print(f"[{status}] {name}: {detail}")
            failed = failed or not ok
        except Exception as exc:
            print(f"[ERROR] {name}: {exc}")
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
