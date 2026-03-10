---
name: us-premarket-telegram-reports
description: Build, package, and deploy an automated US equities premarket watchlist workflow that sends Telegram reports on a schedule. Use when creating or maintaining an OpenClaw skill for institutional-quality LONG-only premarket reports, systemd timer scheduling, Telegram delivery via `openclaw agent --deliver`, bilingual packaging notes, or when built-in OpenClaw cron is unreliable and a stable workaround is needed.
---

# US Premarket Telegram Reports

Create a working automation that sends three recurring US-market reports to Telegram:

1. **Primary report** — 22:30 Pacific/Auckland, Mon–Fri
2. **Overnight update** — 09:30 America/New_York, Mon–Fri
3. **Post-market review** — 17:00 America/New_York, Mon–Fri

Keep the solution operational first. If built-in OpenClaw cron is unreliable, prefer a direct delivery path using `openclaw agent --channel telegram --to <target> --deliver` triggered by systemd user timers.

## Workflow

1. Confirm the delivery target and schedule.
2. Verify Telegram delivery with a direct `openclaw agent --deliver` test before automating.
3. Use prompts that enforce:
   - English financial research sources
   - Simplified Chinese final output
   - LONG only
   - S&P 500 + Nasdaq 100 only
   - exactly 3 ranked candidates
   - explicit fallback to previous-day levels when premarket data is unavailable
4. If OpenClaw cron works reliably on the machine, it may be used.
5. If OpenClaw cron is unreliable, install the systemd timer workaround from this skill.
6. Package the skill after validating it.

## Preferred execution path

Prefer these scripts when you need a stable implementation:

- `scripts/premarket_primary_report.sh`
- `scripts/premarket_overnight_update.sh`
- `scripts/postmarket_review.sh`

These scripts call OpenClaw directly for report generation/review and Telegram delivery.
The premarket scripts also archive their generated output under `reports/`, and the review script writes post-close analysis under `reviews/`.

## Timer deployment

When using the workaround, install these user units under `~/.config/systemd/user/`:

- `premarket-primary-report.service`
- `premarket-primary-report.timer`
- `premarket-overnight-update.service`
- `premarket-overnight-update.timer`
- `postmarket-review.service`
- `postmarket-review.timer`

Then run:

```bash
systemctl --user daemon-reload
systemctl --user enable --now premarket-primary-report.timer
systemctl --user enable --now premarket-overnight-update.timer
systemctl --user list-timers --all | grep 'premarket-'
```

## Prompt constraints

Enforce all of the following in the automation prompt:

- use Yahoo Finance, Nasdaq Market Activity, Reuters Markets, CNBC Markets when available
- output final report in Simplified Chinese
- keep ticker symbols in English
- focus on institutional-quality setups only
- require strong catalyst, relative volume, liquidity, sector alignment, risk/reward
- do not fabricate market data
- if premarket levels are unavailable, say so explicitly and use previous-day levels
- include a Telegram-friendly summary block
- apply ticker-specific catalyst weighting when relevant instead of treating all names identically
- interpret Trump/policy-style social posts as macro/sector signals first unless they directly target a single company
- apply a top-down macro/geopolitical regime filter before ranking names
- use post-market review to perform mismatch attribution and extract reusable future watchpoints

## If OpenClaw cron is broken

Treat these as failure signals:

- isolated cron runs create session index entries without matching session transcript files
- `cron runs` stays empty while the job appears to run
- main-session cron finishes with `deliveryStatus = not-requested`
- Telegram never receives the scheduled output despite direct `openclaw agent --deliver` working

If those appear, stop using built-in cron for this workflow and switch to systemd timers plus direct CLI delivery.

## Resources

### scripts/
- `premarket_primary_report.sh`: sends the evening primary report
- `premarket_overnight_update.sh`: sends the overnight refresh

### references/
- `deployment-notes.md`: operational lessons and known failure modes
- `ticker-catalyst-map.md`: ticker-specific and macro-special-source weighting guidance
- `macro-geopolitical-map.md`: top-down market regime and geopolitical impact guidance
- `strategy-lessons.md`: durable lessons and reusable watchpoints extracted from review
