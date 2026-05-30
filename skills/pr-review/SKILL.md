---
name: pr-review
description: Review a pull request or code diff for engineering-leadership concerns (coupling, reviewability, convention drift, and test coverage of changed logic) and deliver the feedback with Radical Candor. Use when asked to review a PR, review a diff, or check code before merge.
---

# pr-review

## Purpose

Reviews a pull request the way an experienced engineering leader would: for what scales or sinks a *team*, not for style a linter already catches. It assesses the change against four dimensions, then delivers the feedback with Radical Candor: direct enough to be useful, framed with enough care to be heard.

## When to use

Reviewing a pull request, a diff, or a branch before merge.

## When not to

Pure formatting or style passes: that's CI's job, not this skill's. If the only findings would be lint, say the change looks clean and stop.

## Foundation — Radical Candor

Feedback rides two independent axes:

- **Care Personally** — you give a damn about the person, not just the code.
- **Challenge Directly** — you say the hard thing plainly, without hedging.

Both at once is **Radical Candor**. The failure modes to actively avoid:

- **Ruinous Empathy** — caring so much you soften a real defect until it reads as "nit:". The most common failure for thoughtful reviewers.
- **Obnoxious Aggression** — challenging without care: an unprioritised pile of criticism.
- **Manipulative Insincerity** — neither: vague praise, nothing actionable.

See [the Radical Candor foundation](https://github.com/kaszubski/engineering-leader-skills/blob/main/foundations/radical-candor.md) for the full 2×2.

## How it works

1. **Get the diff.**
   - A GitHub PR → `gh pr diff <number>`, plus `gh pr view <number>` for the description and intent.
   - A local branch → `git diff <base-branch>...HEAD`.
   - A diff pasted into the conversation → use it directly.
   If none is available, ask which to review.
2. **Read for intent first.** What is this PR *trying* to do? A review that misreads the goal is noise, so use the PR description and the commit messages.
3. **Assess the four dimensions** below. Cite a specific `file:line` or code snippet for every finding.
4. **Draft the review** in the output format.
5. **Run the Radical Candor self-check** before returning it.

## The four dimensions

Review for what costs a *team* over time. Ignore anything a linter or formatter already handles.

### 1. Coupling

Does the change add dependencies between things that should stay independent?

- A new import crossing a module or layer boundary.
- A change that forced edits in a seemingly unrelated module (shotgun surgery).
- Shared mutable state, or a `utils`/`helpers` module quietly becoming a dumping ground.

*Why it matters:* coupling is what makes a codebase slow to change for everyone who touches it next.

### 2. Reviewability

Can this PR be reviewed *honestly*?

- **Size** — a PR too large to hold in your head gets rubber-stamped, and rubber-stamping is review theatre.
- **Mixed concerns** — a refactor + a feature + a bugfix in one PR; each one hides the others.
- Does the diff tell a coherent story?

If the PR is genuinely too large or too mixed, *that finding is the headline*: recommend splitting it before reviewing the rest in detail.

### 3. Convention drift

Does the change respect the codebase's own model and language? (DDD lens — see [the DDD foundation](https://github.com/kaszubski/engineering-leader-skills/blob/main/foundations/ddd.md).)

- A new term or concept for something the codebase already names.
- A new pattern where an established one exists and would fit.
- Logic leaking across an established boundary.

*Why it matters:* every drift makes the next change harder; unchecked, one codebase quietly becomes several.

### 4. Tests on changed logic

Is new or changed *logic* actually exercised?

- Not coverage percentage. Coverage of the *risky lines*: new branches, conditions, edge cases.
- New behaviour shipped with no test.
- A bug fix with no regression test.

If the project has no visible test setup, note that, but don't demand tests blindly.

## Output format

Produce the review as text for the human to use. This skill does **not** post to GitHub; posting comments, and the merge decision, stay with the reviewer.

```
**Verdict:** <one line — e.g. "Solid change; two blocking items on coupling and a missing regression test.">

**Blocking** — resolve before merge
- `file:line` — <the specific problem> → <the concrete change>

**Non-blocking** — worth considering, reviewer's call
- <…>

**Done well**
- <specific and genuine — not filler>

**Self-check:** <one line — see below>
```

If there are no blocking items, say so plainly. If there are no genuine positives, omit the section rather than inventing one.

## The Radical Candor self-check

Before returning the review, test it against the 2×2:

- **Challenge Directly** — does every blocking item name a *specific* impact and a *concrete* change? Cut "consider maybe", vague unease, and questions that are really hidden assertions.
- **Care Personally** — is every comment on the *code*, not the coder? Does the framing assume competence and a shared goal?
- **Not Ruinous Empathy** — is any real defect disguised as a "nit:" or buried in politeness? Promote it to blocking.
- **Not Obnoxious Aggression** — is this an unprioritised pile? Every item must be sorted into blocking or non-blocking.

State the outcome in the self-check line. If the review fails the gate, fix it before returning; don't ship it with a caveat.

## Rules

- Not a linter. Never flag formatting, import order, or anything CI owns.
- One finding, one place: cite `file:line`.
- Advisory only: produce the review; never post it or merge.
- A clean PR is a valid result. Don't manufacture findings to look thorough.
