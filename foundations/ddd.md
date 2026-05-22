# Domain-Driven Design (DDD)

> **Source:** *Domain-Driven Design: Tackling Complexity in the Heart of Software* — Eric Evans (2003). Also Vaughn Vernon, *Implementing Domain-Driven Design*.
> A distillation of the few concepts these skills actually use — not the whole discipline.

## The operative core

DDD is large. These skills use a small, high-leverage subset:

- **Ubiquitous language** — one shared vocabulary for a domain, used identically in conversation *and* in code. When the words drift, the model has drifted.
- **Bounded context** — an explicit boundary within which a model and its language are consistent. Across the boundary, the same word can mean something different — and that's fine, as long as the boundary is named.
- **Aggregates & invariants** — a cluster of objects with a rule that must always hold. Logic that bypasses the rule is a bug waiting to happen.
- **Conway's law alignment** — code structure tends to mirror team communication structure. Where they *disagree*, you get friction: accidental ownership, silos, contested boundaries.

## How skills in this collection use it

Most repositories these skills run on **will not be DDD-designed** — so the lens is not "grade against DDD." It is:

1. **Does the code have *a* consistent model and respect its own boundaries?** A change that leaks logic across a module boundary, or introduces a term used nowhere else, is eroding whatever model exists.
2. **Conway's law as a diagnostic.** A file only one person ever touches may be an *intentional* bounded context (one owner, by design) or *accidental* ownership (a silo, by drift). The distinction is the insight — apply DDD's *thinking*, not its checklist.

## Related

Used most heavily by the [repo-xray](../skills/repo-xray/SKILL.md) skill (Conway lens on silos), and as a secondary lens in [pr-review](../skills/pr-review/SKILL.md) (does this change respect the codebase's own model?).
