# Deployment notes

## Stable architecture

Use this path when reliability matters:

- `systemd --user` timers for scheduling
- `openclaw agent --channel telegram --to <target> --deliver` for transport
- environment variable `TELEGRAM_TARGET` for the destination

## Example timer cadence

- primary report: Mon–Fri 22:30 Pacific/Auckland
- overnight update: Mon–Fri 09:30 America/New_York

## Known failure pattern on the tested machine

OpenClaw built-in cron was observed failing in two different ways:

1. **isolated cron + announce**
   - run/session index entries appeared in session metadata
   - matching session transcript files were missing
   - Telegram delivery never happened

2. **main-session system-event cron**
   - job finished with `deliveryStatus = not-requested`
   - no Telegram message was delivered

## Recommended validation sequence

1. Test direct delivery manually:

```bash
export TELEGRAM_TARGET=<TELEGRAM_TARGET>
bash scripts/premarket_primary_report.sh
```

2. Only after direct delivery works, add systemd timers.
3. Avoid relying on built-in OpenClaw cron if the symptoms above appear.

## Current report-shaping rules

The production prompts were tightened after dry-run review.

Current expectations:

- top ideas should be ranked by **next-session tradability**, not brand recognition
- single-name catalysts beat generic sector-strength arguments
- if only two names truly qualify, the third slot should be presented as a **conditional watchlist** rather than a fake equal-strength pick
- the report is allowed to say that quality drops off sharply after the first two names
- overnight updates should emphasize **open-drive tradability** even more than the evening primary report

## Packaging

Package the skill with:

```bash
python3 /usr/lib/node_modules/openclaw/skills/skill-creator/scripts/package_skill.py skills/us-premarket-telegram-reports dist
```
