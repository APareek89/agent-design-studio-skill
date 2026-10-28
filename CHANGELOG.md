# Changelog

## 1.1.0 — unreleased review candidate (28 October 2026)

- Added lite/standard/full PDF modes; standard is now the default.
- Put a plain-language decision brief first; moved review scores to the back.
- Rendered vector task/workflow diagrams, a risk heat table and evaluation matrix.
- Split build context into bounded milestones and removed stale, unchanged generated files on re-export.
- Added explicit semantic declarations and seven rule families, with stronger writer-linked assertions and trusted record-input guards after independent code review.
- Added opt-in task/component checkpoints, dependency invalidation, run reports and S1–S12 scoring.
- Preserved failed reviews, historical seeds and unmeasured token usage; added independently reviewed synthetic designs and fresh repeat evaluations.

### Known limits

- Total host inference usage is unavailable in this environment. S11 token savings is unmeasured and must not pass on artifact size alone.
- Four additional support/AP/research/onboarding drafts remain explicitly `needs-work` after independent review (handoff content/receipt contracts and incomplete fixtures). Their reviews are preserved; only the telecom and health examples reached an independent pass.
- The fresh-repeat runs surfaced real domain/fixture regressions. Final feedback-repaired examples are not an untouched transfer benchmark. Two consecutive all-target passes have not been established.
- Fresh authors were run for the baseline and iterations01/03; not every intermediate code change received two fresh author sessions. Other iterations are explicitly recorded repairs, reviews or rerenders.
- Civic and CSV worked designs retain legacy schema1.0; their semantic coverage is unverified rather than falsely upgraded.
- Current automatic diagram layout explicitly stops above its readable node/capacity limits; larger graphs require a layout extension or embedded SVG before delivery.
- Semantic checks verify declared contracts and graph paths; they do not execute business assertions, verify external policy truth or certify runtime safety. Typed source labels can still be false; a reviewer must inspect evidence.
- No release tag, publication or push is part of this change. The original public v1 release remains unchanged until review.
