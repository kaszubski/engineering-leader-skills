---
name: coaching-calibrator
description: Recommend how to coach, support, or delegate a specific task to an engineer, using Blanchard's Situational Leadership II to match your leadership style to their development level. Use when asked how to delegate work to someone, how to support or develop an engineer, or how to hand off a responsibility.
---

# coaching-calibrator

## Purpose

Given an engineer and a *specific task*, recommends how to lead the hand-off (how much direction, how much support) using Situational Leadership II. It stops the most common management mistake: leading everyone the same way.

## When to use

Deciding how to delegate, coach, support, or develop someone on a particular task or skill.

## When not to

General performance reviews, or anything not tied to a *specific* task. SLII is per-task by design; a person is a different development level on different work.

## Foundation — Situational Leadership II

There is no single best leadership style. Match the **style** to the person's **development level on that task**.

Development level combines two *independent* things:

- **Competence** — demonstrated skill and knowledge on this task.
- **Commitment** — motivation *and* confidence on this task.

| Level | Competence | Commitment | Looks like |
|---|---|---|---|
| **D1** | Low | High | Enthusiastic beginner — eager, hasn't done it |
| **D2** | Low–some | Low | Disillusioned learner — hit the hard part, confidence dropped |
| **D3** | Moderate–high | Variable / low confidence | Capable but cautious — can do it, doubts it |
| **D4** | High | High | Self-reliant achiever — competent and confident |

Style matches level: D1 → **S1 Directing**, D2 → **S2 Coaching**, D3 → **S3 Supporting**, D4 → **S4 Delegating**.

See [the SLII foundation](https://github.com/kaszubski/engineering-leader-skills/blob/main/foundations/slii.md) for the full model.

## How it works

1. **Establish the specific task.** If the request is about a person in general ("how do I manage Sarah"), ask: *on what task or skill area?* Never diagnose a person globally.
2. **Gather signals — competence and commitment separately.**
   - *Competence:* have they done this before? Successfully? Recently? Do they know the domain?
   - *Commitment:* are they motivated by it? Confident? Anxious? Have they hit a setback on it?
   If signals are missing, ask for them. Do not guess a level.
3. **Diagnose** the development level from the two reads.
4. **Recommend the matching style** as concrete behaviours — not just the label.
5. **Flag** the relevant classic error or regression risk.
6. Encourage the manager to **share the diagnosis with the person** — SLII works as a conversation, not a covert label.

## Diagnosis — separate the two reads

Competence and commitment move *independently*. The most common diagnostic error is collapsing them:

- **Low output is not always low competence.** It is often low *commitment*: a capable person who is disillusioned (D2) or anxious (D3). Directing them harder makes it worse.
- **Enthusiasm is not competence.** An eager, confident person who has never done the task is D1, not D4. The confidence fools managers into delegating.
- **"Used to be great, now struggling"** is usually a commitment drop or a regression, not lost skill.

Deceptive cases worth naming:

- High, reliable output *but* seeks reassurance and hedges decisions → **D3**, not D4. They need a sounding board, not a hand-off.
- Was a D4, then a failure / reorg / new stack → can regress to **D2** *on the same task*. Development level is not a ratchet.

## The four styles — concrete behaviours

### S1 Directing — for D1

Eager, but hasn't done it. Give explicit steps and a clear definition of done; show them, or pair on the first instance; check in on *progress* frequently; most decisions are yours for now. Don't read their enthusiasm as readiness.

### S2 Coaching — for D2

Hit the hard part; confidence has dropped. Still give direction, but now explain the *why*, not only the steps. Actively rebuild confidence; name what they are doing well. Involve them in decisions while still guiding. This is the most hands-on style: high direction *and* high support. Don't pull back early; D2 is where people quietly disengage.

### S3 Supporting — for D3

Capable but cautious. Lead with encouragement; share decisions, and ask "what do you think?" before offering your view. Step back from directing; they know how. Help them trust their own judgement. Trap: treating a D3 like a D4 and going silent when they need a sounding board.

### S4 Delegating — for D4

Competent and confident. Hand over the outcome and the decisions; agree what success looks like, then get out of the way. Stay available without hovering. Recognise the work. Trap: over-directing. A micromanaged D4 disengages, or leaves.

## Common errors to flag

- **One style for everyone** — the laziest and most common failure.
- **Delegating to a D1** — abandonment dressed up as empowerment.
- **Over-directing a D4** — micromanagement; they regress or leave.
- **Confusing D1 and D2** — both have low-ish competence, but D1 needs *direction* and D2 needs *confidence rebuilt*. Treat a D2 like a D1 and you crush already-low confidence.
- **Ignoring regression** — re-diagnose after a failure, a reorg, or a tech change. The level can drop.

## Output format

```
**Task:** <the specific task — restated to confirm it is specific>

**Diagnosis**
- Competence: <low / some / moderate–high / high> — <reasoning>
- Commitment: <high / low / variable> — <reasoning>
- Development level: **D<n>**

**Recommended style: S<n> <name>**
<2–4 concrete behaviours for this week — what to actually do>

**Watch for:** <the relevant classic error or regression risk>

**Share it:** <how to name this diagnosis with the person — SLII is a conversation>
```

If competence or commitment signals are missing, ask for them rather than producing a diagnosis.

## Rules

- Always anchor to a specific task. The same person is a different level on different work.
- Never guess a development level — if the signals are not there, ask.
- Recommend *behaviours*, never just the style label.
- The diagnosis is shared with the person, not a covert label applied to them.
