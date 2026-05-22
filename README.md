# Engineering Leader Skills

Claude Code skills for engineering managers and tech leads — by [Matt Kaszubski](https://github.com/kaszubski).

> **Status: v0.1 — work in progress.** Private while the skills and the voice are still being shaped. Public launch to follow.

## What this is

A small, curated collection of Claude Code skills for the work of *leading* engineers — reviewing code, coaching people, reading a team's health. Not a grab-bag.

Every skill is anchored on an established framework, operationalised so the framework actually changes the output — and the whole collection shares one vocabulary.

The bet: plenty of general-purpose Claude skills exist; almost none are built deliberately *for engineering leaders*. This fills that gap.

## The skills

| Skill | What it does | Anchored on |
|---|---|---|
| `pr-review` | Reviews a PR for what scales or sinks a team — coupling, reviewability, convention drift — not style nits. | Radical Candor |
| `coaching-calibrator` | Given an engineer and a task, recommends how to coach or delegate it. | Situational Leadership II |
| `repo-xray` | Reads git + PR history and surfaces non-obvious team-health signals, narrated. | Domain-Driven Design |

Roadmap: `retro-facilitator`, anchored on Conscious Leadership.

## Foundations

Each skill builds on a framework, distilled *for application* in [`foundations/`](./foundations):

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

While this repo is private, the machine must be signed in to GitHub (`gh auth login`, or git credentials) for the marketplace to resolve.

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
