# Analyst research assistant for the internal report library

> PASS | DESIGN ONLY. self-review; round 1. A proposed design, not an approved or built system.

## Open first

1. `DESIGN.html`: the clickable read-only view. Decision brief, then the ten steps, then assumptions and review.
2. `DESIGN.pdf`: the same design as a readable report (at most 12 pages).

## Files

- `DESIGN.html`: Read-only visual view; no approval controls, no network assets.
- `DESIGN.pdf`: Decision brief on page 1, then the design steps.
- `build/`: 00-overview.md plus 3 milestone file(s), each under 25 KB in standard mode.
- `design.json`: The single source for every ID, contract and fixture.
- `review.json`: Review record; earlier rounds are kept as review-round-N.json.
- `validation.json`: Structural checks and generated-file hashes.
- `run-report.json`: Timing, sizes, pages and validator results, when recorded.
- `_evidence/eval-set.json`: Complete evaluation fixtures and assertions.
- `_evidence/fmea-register.csv`: Scored risks with controls, owners and linked tests.
- `_evidence/assumptions.md`: Proposed facts with owners, verification and launch blockers.
- `_evidence/PRD.md`: Readable summary of all ten stages.
- `_evidence/architecture.md`: Exact component, workflow, architecture and model contracts.

## Expected information

12 of 12 required items covered; justified: COV15.
Coverage checks look for expected information; they do not judge its quality. Details: validation.json.

Code owns money, identity, dates and limits. Models suggest or explain; they hold no write authority. A design review is not stakeholder approval, measured accuracy or an executed business control.
