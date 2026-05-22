---
name: coaching-calibrator
description: Recommend how to coach or delegate a task to an engineer, using Blanchard's Situational Leadership II. Use when asked how to delegate something, how to support or develop an engineer, or how to hand off a specific piece of work.
---

# coaching-calibrator

> **Status: v0.1 draft.** Structure is set; the recommendation wording is still being refined.

## Purpose

Given an engineer and a *specific task*, recommends how to lead that hand-off — how much direction, how much support — using Situational Leadership II. Stops managers from leading everyone the same way.

## Foundation — Situational Leadership II

Match leadership **style** to the person's **development level on that task**:

| Level | Competence / Commitment | Style |
|---|---|---|
| D1 | Low / High (eager beginner) | S1 Directing |
| D2 | Low–some / Low (disillusioned) | S2 Coaching |
| D3 | Moderate–high / Variable (capable, cautious) | S3 Supporting |
| D4 | High / High (self-reliant) | S4 Delegating |

See [`foundations/slii.md`](../../foundations/slii.md) for the full model.

## When to use

Deciding how to delegate, coach, support, or develop someone on a particular skill or piece of work.

## When not to

General performance reviews, or anything not tied to a *specific* task — SLII is per-task by design.

## How it works

1. Establish the **task** — never "this engineer" in the abstract; always "this engineer, on this task."
2. Gather competence + commitment signals for that task. Ask, if they're missing.
3. Place them D1–D4.
4. Recommend the matching style as concrete behaviours.

## Output — DRAFT, refine the specifics

- The diagnosed development level, with the reasoning.
- The matching style, expressed as **concrete behaviours** — not just "S2 Coaching" but what that looks like this week.
- A flag for the classic errors: managing everyone alike, delegating to a D1 (sink-or-swim), over-directing a D4 (micromanagement).

## Rules

- Always anchor to a specific task. The same person is a different D-level on different tasks.
- If competence/commitment signals are missing, ask — don't guess a level.
