# Build overview

> PASS | DESIGN ONLY. self-review; round 1.

We want a research assistant for our 50 internal analysts. They spend hours hunting through our own research reports - about 4,000 PDFs going back six years, plus the weekly market notes - to answer questions such as "what did we say about warehouse automation payback last year" or "which reports cover cold-chain logistics in Vietnam". Today they search by filename and ask whoever wrote the report.

The assistant should answer questions from those reports and cite the page it took each statement from, so an analyst can open the source and check it. It must never take any action: no posting, no editing a report, no sending anything, no updating any system of record. If the reports do not answer the question it should say so plainly rather than guess.

Not every analyst may see every report. Some client work is restricted to the team that did it, and the assistant must respect those entitlements.

We expect roughly 3,000 questions a month from the 50 analysts. English only. We are not in a regulated industry, but an answer that is confidently wrong would cost us more client trust than a slow answer ever would. Success looks like an analyst getting a cited answer in under two minutes where it takes about twenty minutes today.

Load one milestone file at a time. Contracts below are selected by component; full source is ../design.json. Test IDs resolve to complete fixtures in ../_evidence/eval-set.json. Do not load the entire design unless a dependency requires it.

Code owns money, identity, dates and limits. The agent never holds write authority. Keep proposed policies and owners distinct from verified facts. Launch blockers: ../_evidence/assumptions.md. Complete rollout gates and owners: ../_evidence/PRD.md#rollout.

DESIGN.html is delivered with DESIGN.pdf in every mode; it is a read-only view of this design, not an approval tool. Deliver DESIGN.html and DESIGN.pdf together; neither grants write authority.

- [Retrieve only what this analyst may see](01-milestone.md) — C1, C2, C3
- [Decide whether the library can answer](02-milestone.md) — C6, C8
- [Answer, and prove every citation](03-milestone.md) — C4, C5, C7
