# Contributing

Thanks for the interest. This collection is small and opinionated on purpose: curation over volume. The bar for a new skill is high, and that's the point.

## The bar

Before proposing a skill, check it against the collection's design principles:

- **No framework theatre.** If the framework (or measurement lens) doesn't *visibly* change the skill's output, it gets cut. The rubric is where the framework must show up.
- **Curation over volume.** A few excellent, opinionated skills, never a dump. "It would be useful" isn't enough; it has to earn its place next to the others.
- **Consistency is the product.** Every skill follows [`TEMPLATE.md`](./TEMPLATE.md) and shares the vocabulary in [`foundations/`](./foundations).
- **Principle-based.** General engineering-leadership practice, nothing tied to a specific employer or toolchain.

## Adding a skill

1. Read [`TEMPLATE.md`](./TEMPLATE.md) and copy its shape exactly: frontmatter (`name`, `description`), then the body sections in order.
2. Anchor it. Either operationalise an established framework (inline only its *operative core*; the canon lives in `foundations/`), or, like `repo-xray`, declare it a measurement instrument and say so plainly. Don't fake an anchor.
3. Write the `description` as the trigger. Name the situations it should fire on explicitly: too vague never fires, too broad fires on everything.
4. Make the framework change the output. If your rubric reads like a generic checklist, the anchor isn't doing work yet.
5. Anything that requires counting or exact computation goes in a `scripts/` file, not in prose. LLMs miscount.

## Tests

Skills are mostly prose; their contract is the rubric in each `SKILL.md`. For changes to `pr-review` or `repo-xray`, use the [behavioral evaluation pack](./evals/README.md) and report which cases were actually run, with skill/model configuration and human assessment. Authored cases alone are not evidence of model behavior. Deterministic code has automated tests. If your skill ships a script, it ships tests: stdlib `unittest`, zero dependencies, matching `skills/repo-xray/tests/`.

Run the existing suite:

```
python3 -m unittest discover -s skills/repo-xray/tests
```

CI runs these and validates the plugin manifests on every PR (Python 3.9 and 3.12).

## Pull requests

- One concern per PR: a new skill, or a fix, not both. (The `pr-review` skill in this repo will tell you the same thing.)
- Keep commits logical and the working tree green at each step.
- Update [`CHANGELOG.md`](./CHANGELOG.md) under `[Unreleased]`.

## Feedback without code

Triggers and rubrics sharpen by meeting real PRs and real teams. If a skill misfires, over-fires, or gives advice that didn't land, open an Issue with the situation and what you expected. That feedback is as valuable as a patch.
