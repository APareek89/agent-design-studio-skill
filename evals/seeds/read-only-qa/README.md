# Read-only seed: analyst research assistant

A worked design from a brief that never writes, added in v1.3. The telecom and
health-claims examples both post to a system of record, so until this one
nothing exercised the read-only profile end to end.

## What it is

An assistant for 50 internal analysts that answers questions from 4,000
internal report PDFs and cites the page behind every claim, declines when the
reports do not answer, and takes no action on any system.

| | |
| --- | --- |
| Stages | 6 context, 10 task items, 8 components, 9 workflow nodes, 5 stack cards, 2 model plans, 6 risks, 11 evaluations, 6 rollout cards, 1 handoff |
| Semantics | 9 nodes, 10 transitions, 6 goldens, **0 write actions** |
| Validation | passes, `semanticCoverage: verified-declarations`, no warnings |
| Coverage | 12 of 12 required covered, 0 recommended missing, COV15 justified |
| Review | **self-review**, round 1, pass. D5 and D6 at 4, the other ten at 3 |
| PDF | 10 pages, standard mode |

## What it exercises that the other two seeds cannot

- `intake.briefProfile.writes = false`, which switches on the read-only rules.
- **SEM008**: the answer golden pair. EV1 answers with two citations, EV2
  refuses with zero, each naming a component whose declared effect is `read`
  and the citation field it asserts on. SEM003 has nothing to check here
  because there is no write action class.
- **COV16**: a citation golden, a refusal golden and a statement of who may
  see which documents.
- **COV17**: all six read-only risk families — stale source (FM1), missing
  citation (FM2), answer outside the corpus (FM3), prompt injection carried in
  a report (FM4), leaking content the reader may not see (FM5), and a
  confident answer when the corpus is silent (FM6).
- **COV11 as "n/a"**: there is no money write for a human trigger to gate, and
  the coverage report says so with the reason instead of marking it missing.
- The authority table reading "answers with citation", "answers with caveat",
  "declines" rather than acts alone and human decides.
- Fix 9's run conditions: this was authored with no sub-agent, no web search
  and no browser, and page 1 of the PDF and every HTML view say so.

`tests/test_read_only_seed.py` checks all of it, and three of its tests remove
what the profile requires to prove the rules fire rather than passing
vacuously.

## Rebuilding it

```bash
python3 -I evals/seeds/read-only-qa/author_design.py
```

`author_design.py` builds `design.json` from scratch. The failure-mode to
evaluation relation is written once in its `COVERAGE` table and read in both
directions, and each milestone's test list is derived from its components, so
neither can drift out of agreement.

## Honest limits

- **The review is a self-review.** The same agent authored the design and
  scored it against the rubric; no separate reviewing agent was available.
  These scores should carry less weight than the ones on telecom and
  health-claims, which were reviewed by a different agent. `review.json` says
  this first, and the run conditions repeat it on every rendered view.
- **Nothing was executed.** Every golden, offline set and online check is a
  specification. No index, model or report corpus exists.
- **No web research.** All nine tool candidates are `verified: false` names to
  check, not recommendations.
- **The library is assumed, not inspected.** H1, H2 and H5 block launch, and
  the design does not work if any of them is false.
