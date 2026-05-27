# Engineering Leader Skills

Claude Code skills for engineering managers and tech leads — by [Matt Kaszubski](https://github.com/kaszubski).

> **Early days — `v0.1.0`.** Expect breaking changes. Triggers and rubrics will sharpen as the skills meet real PRs and real teams. Feedback in Issues welcome.

## What this is

A small, curated collection of Claude Code skills for the work of *leading* engineers — reviewing code, coaching people, reading a team's health. Not a grab-bag.

Most skills are anchored on an established leadership framework, operationalised so the framework actually changes the output. One — `repo-xray` — is the collection's measurement instrument: not framework-anchored, just careful, calibrated measurement. Either way, the collection shares one vocabulary.

The bet: plenty of general-purpose Claude skills exist; almost none are built deliberately *for engineering leaders*. This fills that gap.

## The skills

| Skill | What it does | Anchored on |
|---|---|---|
| `pr-review` | Reviews a PR for what scales or sinks a team — coupling, reviewability, convention drift — not style nits. | Radical Candor |
| `coaching-calibrator` | Given an engineer and a task, recommends how to coach or delegate it. | Situational Leadership II |
| `repo-xray` | Reads git + PR history and surfaces non-obvious team-health signals, narrated. | Measurement instrument (DDD lens, one signal) |

Roadmap: `retro-facilitator`, anchored on Conscious Leadership.

## Examples

### `pr-review`

> *"Review PR #42 on owner/repo"*

Returns a Radical Candor review: **Verdict / Blocking / Non-blocking / Done well / Self-check**. Cites `file:line`. Never posts to GitHub — advisory only.

<details>
<summary>Sample output (real review of a small UX PR)</summary>

```
**Verdict:** Clean batch. Nothing blocking — one bundling note and two polish items.

**Non-blocking** — worth considering, reviewer's call
- PR bundles three unrelated concerns. Marquee toggle, justify sweep, and arrow
  glyph swap have nothing in common except "UX walkthrough output." Small enough
  to hold in your head here, but the pattern degrades fast if a future "Batch N"
  puts a 50-line behavior change next to silent CSS edits.
- `e2e/marquee-toggle.spec.ts:50` — fixed `waitForTimeout(700)` after the pause
  click. You used `expect.poll` earlier in the same test. Mirror that pattern —
  the brittle version will flake under CI load.

**Done well**
- The pause test asserts behavior (`.worked__track-shift` transform stops
  advancing), not just `aria-pressed`. That's the test that catches a real
  regression.

**Self-check:** Passes Radical Candor — each item names file/line and a concrete change.
```

</details>

---

### `coaching-calibrator`

> *"Sarah is moving onto incident response. She handled one ticket before with help, isn't confident yet. How should I support her?"*

Diagnoses **competence and commitment separately**, lands on a development level (D1–D4), then prescribes the matching style (S1 Directing → S4 Delegating) as concrete behaviours for the week. Asks for missing signals rather than guessing a level — SLII is a conversation, not a covert label.

---

### `repo-xray`

> *"Run a repo-health x-ray on this project — last 365 days"*

Runs five signal queries (review concentration, knowledge silos, time-to-first-review, stale PRs, silent merges), then narrates them as a *calibrated* health note. Calibrated meaning: a 66% silent-merge rate on a two-person repo is not a 66% silent-merge rate on a thirty-person team, and the narration says so.

## Foundations

The skills draw on these frameworks, distilled *for application* in [`foundations/`](./foundations):

- [Radical Candor](./foundations/radical-candor.md) — Kim Scott
- [Situational Leadership II](./foundations/slii.md) — Ken Blanchard
- [Domain-Driven Design](./foundations/ddd.md) — Eric Evans
- [Conscious Leadership](./foundations/conscious-leadership.md) — Dethmer, Chapman & Klemp

These are *distillations for use*, not reproductions — each one credits and links its source.

## Install

### As a plugin (recommended)

In Claude Code:

```
/plugin marketplace add kaszubski/engineering-leader-skills
/plugin install engineering-leader-skills
```

### Manually

```
git clone https://github.com/kaszubski/engineering-leader-skills.git
cp -r engineering-leader-skills/skills/* ~/.claude/skills/
```

### Requirements

`pr-review` and `coaching-calibrator` have no dependencies. `repo-xray` — with either install method — needs Python 3, `git`, and the GitHub CLI (`gh`) on your PATH.

## Design principles

- **No framework theatre.** If a framework doesn't visibly change a skill's output, it gets cut.
- **Curation over volume.** A few excellent, opinionated skills — never a dump.
- **Consistency is the product.** Every skill follows [`TEMPLATE.md`](./TEMPLATE.md) and shares the `foundations/` vocabulary.
- **Principle-based.** General engineering-leadership practice — nothing tied to a specific employer.

## License

[MIT](./LICENSE). The framework distillations in `foundations/` summarise third-party works, each credited and linked in its own file.
