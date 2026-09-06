# Engineering Leader Skills

Claude Code skills for engineering managers and tech leads, by [Matt Kaszubski](https://github.com/kaszubski).

> **`v0.3.0`, small and opinionated by design.** The triggers and rubrics sharpen as they meet real PRs and real teams; that iteration is the point, not a caveat. Issues welcome, especially where a skill misfired.

## What this is

A small, curated collection of Claude Code skills for the work of *leading* engineers: reviewing code, coaching people, reading a team's health. Not a grab-bag.

Most skills are anchored on an established leadership framework, operationalised so the framework actually changes the output. One of them, `repo-xray`, is the collection's measurement instrument: not framework-anchored, just careful, calibrated measurement. Either way, the collection shares one vocabulary.

The bet: plenty of general-purpose Claude skills exist; almost none are built deliberately *for engineering leaders*. This fills that gap.

## The skills

| Skill | What it does | Anchored on |
|---|---|---|
| `repo-xray` | Reads git + PR history and surfaces non-obvious team-health signals, narrated. Local, deterministic, advisory. | Measurement instrument (DDD lens, one signal) |
| `pr-review` | Reviews a PR for what scales or sinks a team (coupling, reviewability, convention drift), not style nits. | Radical Candor |
| `coaching-calibrator` | Given an engineer and a task, recommends how to coach or delegate it. | Situational Leadership II |
| `retro-facilitator` | Turns raw retro material into a facilitated retro: separates fact from story, converts blame into ownership. | Conscious Leadership |

## Examples

### `repo-xray`

> *"Run a repo-health x-ray on this project — last 365 days"*

Runs five signal queries (review concentration, knowledge silos, time-to-first-review, stale PRs, silent merges), then narrates them as a *calibrated* health note. Calibrated meaning: a 66% silent-merge rate on a two-person repo is not a 66% silent-merge rate on a thirty-person team, and the narration says so. Runs entirely on your machine with your own `git`/`gh` auth; nothing is posted.

---

### `pr-review`

> *"Review PR #42 on owner/repo"*

Returns a Radical Candor review: **Verdict / Blocking / Non-blocking / Done well / Self-check**. Cites `file:line`. Never posts to GitHub; advisory only.

<details>
<summary>Sample output (shortened from a real small UX PR review)</summary>

```
**Verdict:** Clean batch. Nothing blocking — one test reliability note.

**Non-blocking** — worth considering, reviewer's call
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

Diagnoses **competence and commitment separately**, lands on a development level (D1–D4), then prescribes the matching style (S1 Directing → S4 Delegating) as concrete behaviours for the week. Asks for missing signals rather than guessing a level, because SLII is a conversation, not a covert label.

---

### `retro-facilitator`

> *"Run a retro on Friday's outage — the deploy went out at 4pm and on-call spent the weekend on it."*

Structures the debrief through Conscious Leadership. It reads the room's state (above or below the line), splits every observation into a **verifiable fact and a labelled story**, turns victim/villain/hero framing into ownership spread across the people involved, then turns what they own into concrete experiments for next time. Here's the move a generic "what went well / badly" template skips: it won't let a story ride in as a fact, and it names no villains.

## Foundations

The skills draw on these frameworks, distilled *for application* in [`foundations/`](./foundations):

- [Radical Candor](./foundations/radical-candor.md) — Kim Scott
- [Situational Leadership II](./foundations/slii.md) — Ken Blanchard
- [Domain-Driven Design](./foundations/ddd.md) — Eric Evans
- [Conscious Leadership](./foundations/conscious-leadership.md) — Dethmer, Chapman & Klemp

These are *distillations for use*, not reproductions; each one credits and links its source.

## Install in Claude Code

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

`coaching-calibrator` and `retro-facilitator` need no external tools. `pr-review` can read a pasted diff; local branches need `git`, and GitHub PR retrieval needs authenticated `gh`. `repo-xray` needs Python 3.9+ and `git`; authenticated `gh` enables PR signals. Failed, unavailable, incomplete, or empty measurements are reported as `unknown`, never healthy.

## Getting started with your team

1. Install the skills using the Claude Code instructions above. The rubrics and
   examples are reusable across teams; installation paths and commands are
   platform-specific.
2. Optionally copy [the blank template](./examples/TEAM-CONTEXT.md) into your own
   project as `TEAM-CONTEXT.md`, or use context you already maintain. Fill only
   useful facts, their sources, an owner, and a review date. No form is required.
3. Point the agent to that context when asking for a review or repo x-ray. It
   retrieves relevant entries selectively. Without supplied context, it uses
   available repository evidence and asks only for material missing facts;
   absent documentation is not an unhealthy signal.
4. Try a [starter evaluation example](./evals/README.md), then a real small
   change. Review the evidence, proposed action, and any uncertainty before use.
5. Revisit context and repeat the starter cases when changing a skill or model,
   recording the actual versions and outcomes.

The [filled example](./examples/TEAM-CONTEXT.fictional.md) and evaluation fixtures
are public, **fictional teaching material**. They are never live team context and
should not be auto-loaded as such. Keep your actual context in your own project
or an appropriately restricted source, not in this public skills collection.
People-sensitive coaching or performance details belong in restricted material,
not public examples or evaluation results.

## Design principles

- **No framework theatre.** If a framework doesn't visibly change a skill's output, it gets cut.
- **Curation over volume.** A few excellent, opinionated skills. Never a dump.
- **Consistency is the product.** Every skill follows [`TEMPLATE.md`](./TEMPLATE.md) and shares the `foundations/` vocabulary.
- **Principle-based.** General engineering-leadership practice, nothing tied to a specific employer.

## Development

`repo-xray`'s signal engine has a test suite (stdlib `unittest`, no dependencies):

```
python3 -m unittest discover -s skills/repo-xray/tests
```

Repeatable [behavioral evaluation cases](./evals/README.md) cover the two daily skills. These are authored scenarios, not a claim that model evaluations have run. The prose contract remains the rubric in each `SKILL.md`. See [`CONTRIBUTING.md`](./CONTRIBUTING.md) for the bar a new skill has to clear.

## License

[MIT](./LICENSE). The framework distillations in `foundations/` summarise third-party works, each credited and linked in its own file.
