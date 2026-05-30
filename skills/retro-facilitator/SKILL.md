---
name: retro-facilitator
description: Turn raw retrospective material (an incident, a sprint, a launch, a project that went sideways) into a facilitated retro that separates fact from story and converts blame into ownership, using Conscious Leadership. Use when asked to run or prepare a retrospective, debrief an incident or project, or make a postmortem blameless.
---

# retro-facilitator

## Purpose

Takes the raw material of a retrospective (what happened, what people are saying about it) and structures it into a retro that actually moves a team forward, using Conscious Leadership. It does the one thing a generic "what went well / what went badly" template can't: it separates the *verifiable fact* from the *story* laid on top, and converts blame (victim / villain / hero) into *ownership*. That conversion is the work; the rest is scaffolding.

## When to use

Running or preparing a retrospective, debriefing an incident, or writing a blameless postmortem for a sprint, launch, outage, or project.

## When not to

Reviewing a single pull request: that's `pr-review`. Deciding how to coach one person on a task: that's `coaching-calibrator`. A retro is about a *shared event* and the team's relationship to it, not one artifact or one individual.

## Foundation — Conscious Leadership

A retro fails the moment the room goes **below the line**: closed, defensive, committed to being *right* and to assigning fault. Three moves keep it above the line; each one visibly changes the output.

- **The Line.** At any moment a person is **above the line** (open, curious, learning) or **below** (defensive, blaming, protecting position). The first facilitation move is noticing which side the room is on, and naming it.
- **Facts vs. stories.** Separate the observable and verifiable (the *fact*) from the interpretation on top (the *story*). *"The deploy went out at 4pm Friday"* is a fact. *"Nobody cared about the risk"* is a story. Stories are allowed, but labelled as stories, not smuggled in as facts.
- **Radical responsibility, not the drama triangle.** Below-the-line debriefs cast people into the **drama triangle**: **victim** ("it happened *to* us"), **villain** ("*they* broke it"), **hero** ("I saved it"). Radical responsibility drops the triangle and asks each party: *what can I own here?*

See [the Conscious Leadership foundation](https://github.com/kaszubski/engineering-leader-skills/blob/main/foundations/conscious-leadership.md) for the full model.

## How it works

1. **Establish the event.** What is being retro'd: which incident, sprint, or project, over what window? If the input is a vague verdict (*"the launch was a mess"*), ask for the specific observations behind it. A retro on a conclusion is theatre; a retro runs on events.
2. **Read the room's state.** Scan the raw material for below-the-line signals: blame, defensiveness, certainty about others' motives, victim/villain/hero language. Name the state plainly. If it's below the line, say the first job is getting curious before getting conclusive.
3. **Split every observation into fact and story.** For each item, state the verifiable fact, then the interpretation as an explicitly labelled story. Surface where a story is being treated as a fact; that's usually where the team is stuck.
4. **Drop the drama triangle.** Find the victim / villain / hero framings. Reframe each as ownership: replace *"who caused this"* with *"what can each party own."* Spread ownership across roles; the point is shared responsibility, not relocating blame to a new target.
5. **Turn owned insight into experiments.** Convert what the team now owns into a small number of concrete experiments for the next iteration. Each one is a change someone owns, not a vague resolution to "do better."

## Output format

```
**Retro:** <the specific event and window — restated to confirm it is specific>

**Room state:** <above / below the line — the signals you read, named plainly>

**Facts vs. stories**
- Fact: <verifiable observation> · Story: <the interpretation on top, labelled as a story>
- <…one row per significant observation; flag any story currently being treated as fact>

**From blame to ownership**
- Was framed as <victim / villain / hero>: <the framing> → Ownership: <what each party can own>

**Experiments for next iteration**
- <concrete change> — owned by <role/person>, check at <next retro / date>

**Facilitator note:** <one line — the single most important shift for this retro to land>
```

If the input is a verdict with no underlying observations, ask for the events rather than producing a retro on a conclusion.

## Rules

- **Fact and story stay separate.** Never let an interpretation ride in as a fact; that split is the skill's core move, the thing a generic template skips.
- **No villains.** Reframe every blame into ownership spread across parties. If the output names a culprit, it has failed the foundation.
- **Curiosity before conclusions.** If the room is below the line, say so. Don't produce tidy action items on top of an unresolved defensive state.
- **Experiments, not resolutions.** Every forward item is a concrete, owned change with a check-in, not "communicate better."
- **Advisory and facilitative.** This structures the retro and the thinking; the conversation, and what the team commits to, stay with the people in the room.
