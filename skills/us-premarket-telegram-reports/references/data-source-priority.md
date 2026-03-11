# Data source priority

This file defines the current provider priority and fallback behavior for the US premarket report system.

## Current connected providers

- Finnhub
- Alpha Vantage
- FRED
- FMP
- NewsAPI
- Trading Economics
- EIA
- Twelve Data
- Polygon

## Priority by data type

### Lightweight market snapshot / quotes
1. Finnhub
2. Twelve Data
3. Alpha Vantage

Use for:
- SPY / QQQ / VIX quick checks
- ticker snapshot context
- lightweight market state

### Previous-day aggregate / fallback aggregate data
1. Polygon
2. Alpha Vantage

Rule:
- Polygon is optional fallback only under free-tier limits.
- Never fail the whole report because Polygon is rate-limited.

### Macro rates / yield context
1. FRED
2. If unavailable, mark unavailable explicitly rather than fabricating.

Rule:
- FRED should be treated as best-effort per series.
- One failed series must not break the full market context payload.

### Macro calendar
1. Trading Economics

Rule:
- Use a small sampled subset inside prompt context to avoid prompt bloat.

### Oil / energy context
1. EIA

Rule:
- Use Brent spot as a macro regime input, not as a direct stock trigger.

### Company news / ticker news
1. Finnhub company news
2. NewsAPI for supplemental broad news
3. FMP only where current non-legacy endpoints are available and useful

Rule:
- Prefer direct ticker news over broad keyword-only aggregation.
- NewsAPI is supplemental, not primary, for stock-specific catalysts.

## Operational rules

- Favor fewer, high-signal calls over many low-value calls.
- Treat rate-limited providers as non-fatal when possible.
- Use structured context as a starting point, then let the model supplement with fresh English financial sources.
- If a provider is unavailable, degrade gracefully and say unavailable where needed.
