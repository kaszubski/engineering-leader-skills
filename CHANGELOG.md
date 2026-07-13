# Changelog

All notable changes to this project are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this project aims for
[Semantic Versioning](https://semver.org/spec/v2.0.0.html) once past `v0.x`.

## [Unreleased]

## [0.3.0] — 2026-07-13

### Fixed
- **`repo-xray` PR signals now honour the `--days` window.** `gh pr list`
  returns the most recent merged PRs regardless of age, so a `--days 30` run
  computed review concentration, stale PRs, and silent merges over arbitrarily
  old history. Merged PRs are now filtered to the window, and the old
  `prs_truncated` flag is replaced by `pr_window_covered` — false only when
  the fetch cap was hit *before* reaching the window start, which is the case
  that actually loses data.
- **Contributor counting respects `.mailmap`** (`%aN` instead of `%an`), so
  one person under two names no longer counts as two contributors — that
  count drives the small-team severity calibration.

### Added
- **CI smoke-runs the `repo-xray` engine end-to-end** against the checked-out
  repo itself and validates its JSON output — catches wiring breakage
  (argparse, the git subprocess path, report shape) that unit tests on the
  signal functions can't. Checkout now fetches full history so the run has
  real git log data; with `gh` unauthenticated on runners, it also exercises
  git-only mode.

### Changed
- **`repo-xray`'s stale-PR signal now sees PRs that never merged.** It counts
  currently-open non-draft PRs older than the threshold alongside merged PRs
  that were slow to land; previously the most literal "stale PR" — one sitting
  open with no merge in sight — was invisible.
- **Bot reviews no longer count as review.** Reviews by bots (dependabot, CI
  apps, `app/*` logins) are excluded from review concentration,
  time-to-first-review, and silent merges: a merge approved only by a bot is
  a silent merge, and an instant bot review no longer masks a slow human one.
- **`pr-review` is calibrated against padding clean PRs.** Launch testing
  showed the skill producing several non-blocking items on PRs it judged
  clean — thoroughness theatre. The rubric now says a clean PR gets a short
  review (cap non-blocking items at what you'd genuinely raise in person),
  and the Radical Candor self-check gains a proportionality gate.

## [0.2.1] — 2026-05-31

### Fixed
- **`repo-xray` no longer presents a truncated PR sample as the full history.**
  `gh pr list` caps at 200 merged PRs; on a busy repo that means every PR-based
  signal was silently computed on a recent slice. The engine now reports a
  `prs_truncated` flag and a note when the cap is hit, and the skill is told to
  say so up front in the health note.

### Added
- **CI** (`.github/workflows/ci.yml`) — runs the `repo-xray` test suite and
  validates the plugin manifests on every push and PR, across Python 3.9 and 3.12.
- **`CONTRIBUTING.md`** — the bar a new skill has to clear (no framework
  theatre, curation over volume, `TEMPLATE.md` shape, scripts ship tests).

### Changed
- **Docs** — humanised the prose across the README, skills, and foundations
  (varied punctuation, fewer AI-writing tells); reordered the README to lead
  with `repo-xray`; firmed up the version banner. No skill behaviour changed.

## [0.2.0] — 2026-05-30

### Added
- **`retro-facilitator` skill** — turns raw retrospective material into a
  facilitated retro, anchored on Conscious Leadership: reads the room's
  above/below-the-line state, splits every observation into fact vs. labelled
  story, and converts blame (victim/villain/hero) into ownership. Moves
  `retro-facilitator` off the roadmap and into the collection.
- **Test suite for `repo-xray`'s signal engine** (`skills/repo-xray/tests/`) —
  stdlib `unittest`, zero dependencies. Covers every signal, the severity
  bands, `parse_iso`, the small-team calibration, and the `git log --numstat`
  parser end-to-end against a real temp repo. Makes the "trust the code, don't
  let the model count" premise earned rather than asserted.

### Changed
- **`repo-xray` now calibrates for team size in the engine, not just the
  narration.** The script reports a `contributors` count and softens the three
  team-size-sensitive signals (knowledge silos, review concentration, silent
  merges) by one severity band on a 1–2 contributor repo, recording why in the
  signal detail. Closes the gap between the skill's calibration promise and the
  fixed ratio bands it actually applied.

## [0.1.0] — 2026-05-27

Initial release. Early days — expect breaking changes as triggers and rubrics
sharpen against real PRs and real teams.

### Added
- **`pr-review`** — reviews a PR for coupling, reviewability, convention drift,
  and tests on changed logic, delivered with Radical Candor. Advisory only.
- **`coaching-calibrator`** — recommends how to coach or delegate a specific
  task to an engineer, using Situational Leadership II.
- **`repo-xray`** — narrates non-obvious team-health signals from git + PR
  history; the collection's measurement instrument.
- **`foundations/`** — distilled-for-use summaries of Radical Candor,
  Situational Leadership II, Domain-Driven Design, and Conscious Leadership.
- **`TEMPLATE.md`** — the shape every skill in the collection follows.

[Unreleased]: https://github.com/kaszubski/engineering-leader-skills/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/kaszubski/engineering-leader-skills/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/kaszubski/engineering-leader-skills/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/kaszubski/engineering-leader-skills/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/kaszubski/engineering-leader-skills/releases/tag/v0.1.0
