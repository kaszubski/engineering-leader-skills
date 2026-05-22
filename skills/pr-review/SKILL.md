---
name: pr-review
description: Review a pull request or code diff for engineering-leadership concerns — coupling, reviewability, convention drift, and test coverage of changed logic — and deliver the feedback with Radical Candor. Use when asked to review a PR, review a diff, or check code before merge.
---

# pr-review

> **Status: v0.1 draft.** Structure is set; the rubric wording is still being refined.

## Purpose

Reviews a pull request the way an engineering leader would — for what scales or sinks a team, not for style nits a linter already catches. It anchors the *delivery* of that feedback in Radical Candor.

## Foundation — Radical Candor

Feedback rides two axes: **Care Personally** and **Challenge Directly**. The target is both at once. The failure modes to actively avoid:

- **Ruinous Empathy** — a real defect softened until it reads as "nit:". The most common failure.
- **Obnoxious Aggression** — an unprioritised pile of criticism.

See [the Radical Candor foundation](https://github.com/kaszubski/engineering-leader-skills/blob/main/foundations/radical-candor.md) for the full 2×2.

## When to use

Reviewing a PR, a diff, or a branch before merge.

## When not to

Pure style/formatting passes — that's a linter's job, not this skill's.

## How it works

1. Get the diff (`git diff`, or the PR's changes).
2. Assess it against the rubric below.
3. Deliver the review per the Radical Candor rules.

## Review rubric — DRAFT, refine the specifics

Assess four areas; ignore style nits:

1. **Coupling** — does this change add hidden dependencies between modules that should stay independent?
2. **Reviewability** — is the PR small and coherent enough to review *honestly*? A 2,000-line PR gets rubber-stamped.
3. **Convention drift** — does it respect the codebase's own model and language? (DDD secondary lens — see [the DDD foundation](https://github.com/kaszubski/engineering-leader-skills/blob/main/foundations/ddd.md).)
4. **Tests on changed logic** — is new or changed *logic* covered? Not coverage percentage — coverage of the risky lines.

## Output

- **Blocking** vs **non-blocking** — clearly separated. Candor without priority is noise.
- Each blocking item: the *specific* impact + a concrete change.
- Framing assumes competence and a shared goal. Comment on the code, not the coder.
- A self-check line: did any comment soften a real defect (Ruinous Empathy) or pile on unprioritised nits (Obnoxious Aggression)?

## Rules

- No framework theatre — if Radical Candor isn't visibly shaping the review, the skill failed.
- Don't restate what a linter or CI already reports.
