---
name: repo-xray
description: Analyze a git repository's team-health signals (review concentration, knowledge silos, stale PRs, time-to-first-review, silent merges) and narrate them as a calibrated health note. Use when asked about repo health, team health, code-review health, or what a project's metrics are not showing.
---

# repo-xray

## Purpose

Reads a repository's git and GitHub PR history and surfaces the signals teams *don't* dashboard, then narrates them into a short, calibrated health note. The point is the non-obvious: not commit counts, but where the team is quietly fragile.

Within this collection, repo-xray is the **measurement instrument**: the one skill *not* anchored on a leadership framework. `pr-review` and `coaching-calibrator` operationalise a framework; repo-xray operationalises careful measurement itself.

## The DDD lens — one signal only

repo-xray is not framework-anchored, and pretending otherwise would be the framework theatre this collection exists to avoid. It uses one lens, in one place: **Domain-Driven Design's Conway's-law thinking**, applied to the *knowledge-silos* signal. A file only one person ever touches may be an *intentional* bounded context (one owner, by design) or *accidental* ownership (a silo, by drift); naming that distinction is the insight. The other four signals are plain measurement, DDD-free. See [the DDD foundation](https://github.com/kaszubski/engineering-leader-skills/blob/main/foundations/ddd.md) for the lens.

## When to use

Any request about repo health, team health, code-review bottlenecks, or "what are our metrics missing."

## When not to

Reviewing a single pull request: that's `pr-review`. repo-xray reads *aggregate* history; it is not a substitute for reading the code itself.

## How it works

1. **Run the bundled script.** `signals.py` lives in this skill's own `scripts/` directory. When installed as part of the plugin, the path is `${CLAUDE_PLUGIN_ROOT}/skills/repo-xray/scripts/signals.py`. Run it with the *target* repository as `--repo`:
   `python3 <skill-scripts-dir>/signals.py --repo <target-repo> --days <N>`
   `--repo` is the repository being analyzed (usually the user's current project), not where the script lives.
2. **Do not recompute anything.** All counting lives in the script, because LLMs miscount. Read its JSON output; never re-derive the numbers.
3. **Check data quality before interpretation.** Read `sources`, coverage flags, sample counts, and `note`. Preserve `unknown` severities: failed, unavailable, incomplete, or empty measurements are not healthy results. `github_data` means both PR reads succeeded, not that all samples are complete.
4. **Retrieve relevant team context, then narrate.** Use context the user points to, or `TEAM-CONTEXT.md` in the target repository if present. Read only entries relevant to the signals (ownership, critical paths, accepted tradeoffs, constraints, review date); follow linked decisions selectively. Never use bundled fictional examples as live team context. Without context, use observed data and explicitly label explanations as hypotheses; ask only for material missing facts, with no mandatory form. Missing team documentation is not an unhealthy signal. Commit authors are a proxy for contributors, not a verified team roster. Metrics alone do not establish causes or individual performance.

Requires Python 3 and `git`. `gh` is optional; without it, GitHub PR signals are skipped and the script runs git-only.

## The signals

Knowledge silos · review concentration · time-to-first-review (and its drift) · stale PRs · silent merges. Each carries a severity: `ok` / `watch` / `concern` / `unknown`. `unknown` means there is no trustworthy measurement to grade, including a successful read with no eligible samples.

Three measurement choices worth knowing when narrating: PR signals are bounded to the same `--days` window as the git signals; *stale PRs* counts both merged PRs that took too long to land and currently-open non-draft PRs already older than the threshold; and bot reviews (dependabot, CI apps) never count as review — a merge approved only by a bot is a silent merge.

**Team-size calibration is in the engine.** The script reports a `contributors` count (distinct commit authors in the window). For a 1–2 contributor repo it softens the three team-size-sensitive signals (knowledge silos, review concentration, silent merges) by one band and records that in the signal's `detail`: with almost no one else, single-author files and unreviewed merges are *structural*, not a process failure. When you see a softened signal, carry that calibration through in the narration: explain *why* it's softened, and never quietly re-inflate it.

## Output

- A short **health note** first: plain English, calibrated, connecting signals to each other.
- Then a per-signal table with the raw numbers and severity; render null values as unavailable, never zero.
- When action is warranted, propose one proportionate next check or experiment, separating the observed signal from the explanation to validate. Do not force an action from unknown data beyond resolving its limits.

## Rules

- **Calibration over alarm.** A health tool that cries wolf gets uninstalled. Do not inflate `watch` into `concern`.
- All numbers come from the script. The model narrates; it never counts.
- **Honour the sample's limits.** `sources` distinguishes `ok`, `empty`, `error`, `unavailable`, and `partial`. Coverage flags are null when the source could not be read. A fetch at the cap makes coverage uncertain for merged or open data; dependent signals then return `unknown`, even if an old merge appears in the sample. State the limitation up front. `gh` orders by creation date, so old merges do not prove merge-window coverage. Changing `--days` does not bypass either fetch cap; complete/paginated retrieval is needed to establish coverage.
- **Name the populations.** Merged PRs belong to the requested merge-date window; open PRs are a snapshot of the current non-draft backlog, including older work. Time-to-first-review covers reviewed merged PRs only. Do not describe these as all work or all waiting time.
