# Stress harness

Fifteen mutations of the telecom example, plus seven edge briefs. The harness
found the cases v1.3 fixes; the expected outcomes are now pinned in
`tests/test_stress.py`, so a change that turns a rejection into a render, or a
render into a rejection, fails the suite.

## Running it

```
python3 -I evals/stress/mutate.py skills/agent-design-studio examples/telecom evals/stress/out
```

It writes one folder per mutation under `out/`, each with the mutated
`design.json` and a copy of the example's review, then runs `validate` and the
HTML renderer over each and prints a line per variant. The committed `out/`
folders hold the `design.json` files the tests read; the rendered HTML and PDF
are not committed, because they are reproducible and large.

## What each mutation bends

| Variant | What it does | Expected in v1.3 |
| --- | --- | --- |
| 01 | Script tags and event handlers in the title, brief, tasks and reader layer | renders, escaped |
| 02 | Devanagari, Arabic, Chinese and emoji in titles and labels | renders in HTML and PDF, text intact |
| 03 | A 350-character edge predicate and unbreakable tokens | renders, no plate overlap |
| 04 | Twelve design calls instead of five | rejected: `maxItems=5` |
| 05 | An empty risk register | rejected: `minItems=1` |
| 06 | An empty model stage | rejected (see `docs/decisions.md`) |
| 07 | Two tasks sharing one ID | rejected: duplicate item ID |
| 08 | A retry edge from the last node back to the second | renders |
| 09 | Severity 0, occurrence -1, detection 11 | rejected: number below 1 |
| 10 | A fourth level in the task tree | rejected, naming the depth limit |
| 11 | Twelve extra top-level tasks with nothing serving them | rejected: leaf with no serving component |
| 12 | A fan-out of eight from one node | renders, no plate collisions |
| 13 | No `presentation` block (schema 1.0 input) | renders a derived brief with nothing cut |
| 14 | A 60 KB brief | `export --mode standard` passes |
| 15 | Empty task titles and descriptions | rejected: does not match any allowed schema |

## Edge briefs

`evals/briefs/edge/` holds seven briefs the classifier must read correctly:
empty, vague, Hindi, read-only, autonomous trading, not-an-agent and a 60,000
word one. `expected.json` records the profile each must produce, and S14 in
`scripts/score_run.py` scores the classifier on all seven.

## Adding a mutation

Add it to `mutate.py` and add its expected outcome to `OUTCOMES` in
`tests/test_stress.py`. The suite fails on a mutation with no recorded
outcome: an outcome nobody wrote down is not a decision.
