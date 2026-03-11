# US Premarket Report Automation

This repository contains a working automation setup for sending a US equities premarket long watchlist to Telegram.

## What it does

It sends three recurring reports to Telegram:

1. **Primary report**
   - Schedule: **22:30 New Zealand Time (NZT), Monday to Friday**
   - Purpose: generate the next US trading day's long watchlist before sleep

2. **Overnight update**
   - Schedule: **09:30 New York time, Monday to Friday**
   - Purpose: refresh the watchlist around the regular US market open using overnight tone, premarket movers, and breaking news

3. **Post-market review**
   - Schedule: **17:00 New York time, Monday to Friday**
   - Purpose: review the actual session after the close, score the morning ideas, and extract lessons for continuous strategy improvement

## Scope

The generated report is designed to:

- focus on **LONG opportunities only**
- scan only **S&P 500** and **Nasdaq 100** names
- prefer **institutional-quality setups**
- prioritize:
  - strong catalysts
  - strong relative volume
  - high liquidity
  - institutional participation
  - strong sector alignment
  - favorable risk/reward
- use **English financial research sources**
- output the final report in **Simplified Chinese**

## Why this version exists

OpenClaw's built-in cron path was found unreliable on this machine during testing:

- isolated cron runs created run/session index entries without corresponding session transcript files
- main-session system-event cron runs completed, but did not reliably produce delivered Telegram messages

Because of that, this repository uses a more reliable workaround.

## Working architecture

- **systemd user timers** for scheduling
- **OpenClaw CLI** for message generation and Telegram delivery
- delivery command pattern:

```bash
openclaw agent --channel telegram --to <TELEGRAM_TARGET> --deliver --message "..."
```

## Repository contents

- `scripts/premarket_primary_report.sh`
  - sends the 22:30 NZT primary report
  - saves a local archive under `reports/`
- `scripts/premarket_overnight_update.sh`
  - sends the New York market-open update
  - saves a local archive under `reports/`
- `scripts/postmarket_review.sh`
  - reviews the same trade date after the US close
  - reads archived report files from `reports/`
  - writes a review file under `reviews/`

## Scheduling used

### Timer 1
- Name: `premarket-primary-report.timer`
- Schedule: `Mon..Fri 22:30`
- Time zone: `Pacific/Auckland`

### Timer 2
- Name: `premarket-overnight-update.timer`
- Schedule: `Mon..Fri 09:30`
- Time zone: `America/New_York`

### Timer 3
- Name: `postmarket-review.timer`
- Schedule: `Mon..Fri 17:00`
- Time zone: `America/New_York`

## systemd unit examples

### `premarket-primary-report.service`
```ini
[Unit]
Description=OpenClaw US premarket primary report

[Service]
Type=oneshot
WorkingDirectory=<WORKSPACE_PATH>
ExecStart=<WORKSPACE_PATH>/scripts/premarket_primary_report.sh
```

### `premarket-primary-report.timer`
```ini
[Unit]
Description=22:30 NZT weekdays premarket primary report

[Timer]
OnCalendar=Mon..Fri 22:30 Pacific/Auckland
Persistent=true
Unit=premarket-primary-report.service

[Install]
WantedBy=timers.target
```

### `premarket-overnight-update.timer`
```ini
[Unit]
Description=09:30 New York time weekdays premarket overnight update

[Timer]
OnCalendar=Mon..Fri 09:30 America/New_York
Persistent=true
Unit=premarket-overnight-update.service

[Install]
WantedBy=timers.target
```

## Setup notes

1. Make the scripts executable:

```bash
chmod +x scripts/premarket_primary_report.sh scripts/premarket_overnight_update.sh
```

2. Install the systemd user service/timer files under:

```bash
~/.config/systemd/user/
```

3. Reload and enable:

```bash
systemctl --user daemon-reload
systemctl --user enable --now premarket-primary-report.timer
systemctl --user enable --now premarket-overnight-update.timer
```

## Prompt design principles

The report prompt explicitly requires:

- exactly **3 ranked outputs**
- no fabricated market data
- fallback to previous day levels if premarket levels are unavailable
- concise output readable in under two minutes
- Telegram-friendly summary cards
- ranking by **next-day tradability**, not company prestige
- preference for **single-name catalysts** over generic sector sympathy
- if only two names are truly strong, the third item should be downgraded to a **conditional watchlist / fallback name** instead of pretending all three are equal

### Current prompt behavior

Both the primary report and the overnight update now use the same stricter selection philosophy:

- the first two names should be the real high-conviction setups when available
- the third slot may be labeled as a **Watchlist** candidate if setup quality drops off
- the report should explicitly admit when quality falls sharply after the top two names
- large-cap AI leaders should not be included automatically just because they are liquid or famous
- ticker-specific catalysts should override generic one-size-fits-all weighting when relevant
- macro/policy social-post signals (for example Trump-related posts) should be interpreted at the market/sector level first, not blindly treated as direct single-stock catalysts

### Ticker-specific catalyst weighting

The system now includes a first-pass ticker weighting layer in:

- `skills/us-premarket-telegram-reports/references/ticker-catalyst-map.md`

This reference tells the report logic to weigh different sources differently for different names. Examples:

- `TSLA` -> Musk/Tesla posts, deliveries, FSD/robotaxi, China pricing/delivery
- `AAPL` -> product events, supply chain, China demand, hardware/services cycle
- `NVDA` / `AMD` / `AVGO` / `MU` -> AI infrastructure demand, capex, policy/export restrictions, conference/product-cycle signals
- `VRTX` / biotech names -> clinical/FDA/regulatory signals

### Macro and geopolitical regime layer

The system now also includes a top-down macro filter in:

- `skills/us-premarket-telegram-reports/references/macro-geopolitical-map.md`

This layer forces the report logic to ask whether a major event changes the odds before ranking individual names. Examples:

- Middle East / Iran escalation -> oil, defense, inflation, VIX, risk-off pressure
- tariff/trade escalation -> China exposure, industrials, semis, supply chains
- Fed/rates shock -> duration sensitivity, high-multiple growth risk

### Review now learns from forecast error

Post-market review is no longer just a summary.
It now asks for:

- mismatch attribution
- root-cause category
- future watchpoints for the same stock or setup
- candidate lessons worth writing into long-term strategy rules

The review flow now also appends extracted durable lessons into:

- `skills/us-premarket-telegram-reports/references/strategy-lessons.md`
- `skills/us-premarket-telegram-reports/references/strategy-lessons.jsonl`

The Markdown file is for human review; the JSONL file is for future structured analysis by ticker, regime, or lesson type.

### Connected data layer

The workflow now includes a local structured market-context step powered by connected APIs.
Current priority and fallback rules are documented in:

- `skills/us-premarket-telegram-reports/references/data-source-priority.md`

The scripts currently use:
- Finnhub for lightweight quote/news context
- FRED for rates
- Trading Economics for macro calendar
- EIA for oil context
- Polygon as optional aggregate fallback
- Twelve Data / Alpha Vantage as supplemental quote/market-data backups

To keep provider logic maintainable, shared data access now lives in:

- `scripts/data_sources.py`

This module centralizes provider calls and best-effort fallback handling for the market-context builder.

## Lessons learned

### 1. Delivery path matters more than scheduling elegance
A theoretically cleaner built-in scheduler is not useful if it cannot reliably create runnable sessions or deliver messages.

### 2. Separate research generation from transport assumptions
Using `openclaw agent --deliver` directly makes the transport path observable and testable.

### 3. Fail safe on missing data
If reliable premarket levels are unavailable, the automation should explicitly say so instead of inventing values.

### 4. Constrain the stock universe
Restricting the scan to S&P 500 and Nasdaq 100 significantly improves liquidity quality and reduces junk setups.

## Status

This repository reflects the **working workaround version** that was successfully wired to Telegram delivery using the OpenClaw CLI plus systemd timers.

## Chinese documentation

See: `README.zh-CN.md`
