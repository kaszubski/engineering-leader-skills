---
name: repo-xray
description: Analyze a git repository's team-health signals — review concentration, knowledge silos, stale PRs, time-to-first-review, silent merges — and narrate them as a calibrated health note. Use when asked about repo health, team health, code-review health, or what a project's metrics are not showing.
---

# repo-xray

> **Status: v0.1 draft.** The script `scripts/signals.py` is scaffolded; signal computations are TODO.

## Purpose

Reads a repository's git and GitHub PR history and surfaces the signals teams *don't* dashboard — then narrates them into a short, calibrated health note. The point is the non-obvious: not commit counts, but where the team is quietly fragile.

## Foundation — Domain-Driven Design (Conway lens)

Most repos this runs on are not DDD-designed, so the lens is not "grade against DDD." It is: do the code's boundaries match the team's? A single-author file may be an *intentional* bounded context or *accidental* ownership — that distinction is the insight. See [`foundations/ddd.md`](../../foundations/ddd.md).

## When to use

Any request about repo health, team health, code-review bottlenecks, or "what are our metrics missing."

## How it works

1. **Run the script** — `python3 scripts/signals.py --repo <path> --days <N>` (relative to this skill directory). It prints a JSON blob of signals.
2. **Do not recompute anything.** All counting lives in the script — LLMs miscount. Read its JSON; never re-derive the numbers.
3. **Narrate** the JSON into a health note.

Requires Python 3 and `git`. `gh` is optional — without it, GitHub PR signals are skipped and the script runs git-only.

## The signals

Knowledge silos · review concentration · time-to-first-review (and its drift) · stale PRs · silent merges. Each carries a severity: `ok` / `watch` / `concern`.

## Output

- A short **health note** first — plain English, calibrated, connecting signals to each other.
- Then a per-signal table with the raw numbers and severity.

## Rules

- **Calibration over alarm.** A health tool that cries wolf gets uninstalled. Do not inflate `watch` into `concern`.
- All numbers come from the script. The model narrates; it never counts.
