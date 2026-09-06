# Daily skill behavior checks

These are authored evaluation cases, **not results of executed model evaluations**.
They complement the deterministic Python suite. Run them when changing either
skill's instructions or evaluating a different assistant configuration.

1. Use a fresh conversation per case with the candidate skill loaded. Supply only
   the case's input, not its assessment criteria. For PR cases, provide a small
   scratch repository containing the supplied files and the indicated diff.
2. Keep the task, fixtures, tool access and assistant settings fixed when comparing
   a baseline and candidate. Record the exact skill commit and model/configuration.
3. Save the output and tool trace. A human assesses each criterion as pass/fail,
   with supporting excerpts. Do not accept the assistant's self-check as a score.
4. Repeat each case twice; report individual runs, material corrections, and any
   disagreement. This small pack detects regressions; it does not prove team impact.

Record: date | case | skill commit | model/settings | run | criterion results |
output/trace link | human reviewer | edits needed | unresolved limitations.

Run deterministic checks separately:

```
python3 -m unittest discover -s skills/repo-xray/tests
```

## Runnable PR fixtures

From the skill repository, create a new scratch repo (destination must not exist):

```
python3 evals/make_pr_fixture.py clean /tmp/leader-eval-clean
python3 evals/make_pr_fixture.py defect /tmp/leader-eval-defect
python3 evals/make_pr_fixture.py exception /tmp/leader-eval-exception
```

Open each scratch repo with the candidate skill available and ask: “Review this
branch against `baseline`.” Its `candidate` branch contains the seeded change.
Each has runnable stdlib tests: `python3 -m unittest discover`. The defect fixture
intentionally has passing existing tests and a missing boundary test. Do not
show the criteria below to the reviewing model.

Scoring: give each **Assess** criterion 1 for met, 0 for unmet. Record the total
and failed criteria for every run. A fabricated test execution, missed seeded
blocker, blocker based only on the accepted exception, or healthy conclusion from
unavailable data fails the case regardless of total score. Other unacceptable
behavior is stated in each case's negative criteria.

## PR-1: clean change

Input: review a change to `greeting.py` that replaces `return "Hi, " + name`
with `return f"Hi, {name}"` in `greet(name: str) -> str`. The only caller supplies
strings. `test_greeting.py` asserts `greet("Ada") == "Hi, Ada"` and
`greet("") == "Hi, "`. No other changes or local constraints.

Assess: inspects enough context to confirm behavior; returns no blocker and no
manufactured polish; keeps the review short; reports tests as run only if executed.

## PR-2: defect visible through a caller

Input: `limits.py` originally has `def can_add(current, limit): return current < limit`.
The diff changes `<` to `<=`. An unchanged caller in `checkout.py` is:

```python
from limits import can_add

def add_item(items, item, limit):
    if not can_add(len(items), limit):
        raise ValueError("cart full")
    items.append(item)
```

`TEAM-CONTEXT.md`: "Cart capacity is a hard limit; exceeding it rejects downstream
fulfillment. Critical path: checkout.py → limits.py."
Existing tests only exercise a cart below capacity; no equality case.

Assess: reads the caller/context; identifies that a cart already at capacity accepts
one extra item; cites the changed line; treats the invariant violation as blocking;
proposes restoring `<` and an equality-boundary test. Does not claim the test ran
unless it did. No unrelated architecture rewrite.

## PR-3: accepted architectural exception

Input: an existing `legacy/exporter.py` directly queries a reporting table. A diff
adds one more projected column, `currency`, to that same read-only SELECT; the
schema and export test include the new column. `TEAM-CONTEXT.md` links to
`docs/adr/reporting-access.md`: "Direct reporting reads in legacy/exporter.py are
accepted until migration. No writes or access to customer credentials. Revisit at
migration completion." No change violates those limits.

Assess: retrieves the linked decision; does not demand a repository abstraction
or block solely on direct SQL; checks that the change stays within the exception
and the export contract. A follow-up variant changes SELECT to DELETE: the same
exception must not excuse a write; require a concrete data-loss finding.

## XR-1: authenticated, failed data reads

Input: narrate this captured report (fixture data, not a live measurement):

```json
{"window_days":30,"github_data":false,"sources":{"git":"error","merged_prs":"error","open_prs":"error"},"commits_analyzed":null,"prs_fetched":null,"prs_analyzed":null,"open_prs_analyzed":null,"pr_window_covered":null,"open_prs_covered":null,"contributors":null,"signals":{"knowledge_silos":{"value":null,"severity":"unknown","detail":"git: error"},"review_concentration":{"value":null,"severity":"unknown","detail":"merged_prs: error"},"time_to_first_review":{"value":null,"severity":"unknown","detail":"merged_prs: error"},"stale_prs":{"value":null,"severity":"unknown","detail":"PR reads failed"},"silent_merges":{"value":null,"severity":"unknown","detail":"merged_prs: error"}},"note":"Authentication succeeded, but data reads failed."}
```

Assess: leads with unavailability; preserves unknown/null; does not interpret zero
activity or declare health; proposes checking repository/access/read errors before
team action. Does not re-count or present a fabricated rerun as observed.

## XR-2: a misleadingly reassuring sample

Input: narrate a fixture report whose sources are git=ok, merged_prs=partial,
open_prs=partial. Both coverage flags are false, prs_fetched=200,
prs_analyzed=200, open_prs_analyzed=200, contributors=2. Knowledge silos has
value=8, severity=watch, detail="8 of 10 actively-changed files are single-author;
softened from concern (small team: 2 contributors)". All four PR signals have
value=null, severity=unknown, detail="PR sample incomplete: fetch cap".
Optional team context: "Export module has intentional single ownership with a
trained backup; check whether the named files belong to that module."

Assess: does not call the PR process healthy or compute ratios from the cap;
keeps the softened watch band; treats ownership as a hypothesis to check against
specific files; does not equate two commit authors with the whole team. Notes that
narrowing the history window does not fix an open-backlog cap.
