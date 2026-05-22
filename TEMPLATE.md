# Skill template

Copy this shape when adding a new skill. Every skill in this collection follows it — that consistency *is* the product.

```
skills/<skill-name>/
├── SKILL.md
└── scripts/        (optional — only if the skill needs deterministic code)
```

## SKILL.md frontmatter

```yaml
---
name: <skill-name>
description: <what it does + when Claude should invoke it. This is the trigger —
  write it like product copy. Name the situations explicitly. Too vague never
  fires; too broad fires on everything.>
---
```

## SKILL.md body — sections

1. **Purpose** — one paragraph: what this does, who it's for.
2. **Foundation** — which framework it anchors on; inline the *operative core* only (the 2×2, the grid). The full canon lives in `foundations/`.
3. **When to use / when not to** — keep the trigger sharp.
4. **How it works** — the steps Claude follows.
5. **Output** — the exact shape of what the skill produces.
6. **Rubric / rules** — the operative detail. This is where the framework must visibly change the output.

## Rules

- **The framework must change the output.** If it doesn't, cut it — no framework theatre.
- Inline only the operative subset of a foundation; `foundations/` holds the canon.
- Keep skills principle-based and self-contained — no runtime dependency on files outside the skill directory.
- Anything that requires counting or exact computation belongs in a `scripts/` file, not in prose instructions.
