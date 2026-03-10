# US Premarket Report Automation

This repository contains a working automation setup for sending a US equities premarket long watchlist to Telegram.

## What it does

It sends two recurring reports to Telegram:

1. **Primary report**
   - Schedule: **22:00 New Zealand Time (NZT), Monday to Friday**
   - Purpose: generate the next US trading day's long watchlist before sleep

2. **Overnight update**
   - Schedule: **03:00 New Zealand Time (NZT), Tuesday to Saturday**
   - Purpose: refresh the watchlist using overnight tone, premarket movers, and breaking news

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

Because of that, this repository uses a more reliable workaround:

## Working architecture

- **systemd user timers** for scheduling
- **OpenClaw CLI** for message generation and Telegram delivery
- delivery command pattern:

```bash
openclaw agent --channel telegram --to <TELEGRAM_TARGET> --deliver --message "..."
```

## Repository contents

- `scripts/premarket_primary_report.sh`
  - sends the 22:00 NZT primary report
- `scripts/premarket_overnight_update.sh`
  - sends the 03:00 NZT overnight refresh

## Scheduling used

### Timer 1
- Name: `premarket-primary-report.timer`
- Schedule: `Mon..Fri 22:00`
- Time zone: `Pacific/Auckland`

### Timer 2
- Name: `premarket-overnight-update.timer`
- Schedule: `Tue..Sat 03:00`
- Time zone: `Pacific/Auckland`

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
Description=22:00 NZT weekdays premarket primary report

[Timer]
OnCalendar=Mon..Fri 22:00
TimeZone=Pacific/Auckland
Persistent=true
Unit=premarket-primary-report.service

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

- exactly **3 ranked candidates**
- no fabricated market data
- fallback to previous day levels if premarket levels are unavailable
- concise output readable in under two minutes
- Telegram-friendly summary cards

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
