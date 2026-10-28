# Build overview

> PASS | DESIGN ONLY. self-review; round 3.

Design a health insurance claim adjudication assistant for inpatient hospital claims. It should read submitted policy and hospital documents, assess coverage and eligible charges, recommend or process eligible claims, and route exceptions and rejections for review. Policies can change over time and bills may include room-rent limits. Protect personal medical data, explain decisions with evidence and propose any missing rules as assumptions, not verified insurance or medical advice.


Load one milestone file at a time. Contracts below are selected by component; full source is ../design.json. Test IDs resolve to complete fixtures in ../eval-set.json. Do not load the entire design unless a dependency requires it.

Code owns money, identity, dates and limits. The agent never holds write authority. Keep proposed policies and owners distinct from verified facts. Launch blockers: ../assumptions.md.

After delivering DESIGN.pdf, ask the user: Would you also like a visual HTML version in the same ten-stage structure as the app? Generate HTML only after opt-in, unless already requested.

- [Access and admitted evidence](01-milestone.md) — C1, C2
- [Explanation and rule engine](02-milestone.md) — C3, C4
- [Staff review and waiting status](03-milestone.md) — C5, C6
- [Safe save, readback and proof](04-milestone.md) — C7, C8, C9
