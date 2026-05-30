# Changelog

All notable changes to this project are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this project aims for
[Semantic Versioning](https://semver.org/spec/v2.0.0.html) once past `v0.x`.

## [Unreleased]

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

[Unreleased]: https://github.com/kaszubski/engineering-leader-skills/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/kaszubski/engineering-leader-skills/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/kaszubski/engineering-leader-skills/releases/tag/v0.1.0
