# Build overview

> NEEDS-WORK | DESIGN ONLY. independent-agent; round 1.

Read invoice documents, explain PO mismatches and prepare an AP analyst review packet. No posting, payment or supplier-master updates.

Load one milestone file at a time. Contracts below are selected by component; full source is ../design.json. Test IDs resolve to complete fixtures in ../eval-set.json. Do not load the entire design unless a dependency requires it.

Code owns money, identity, dates and limits. The agent never holds write authority. Keep proposed policies and owners distinct from verified facts. Launch blockers: ../assumptions.md. Complete rollout gates and owners: ../PRD.md#rollout.

After delivering DESIGN.pdf, ask the user: Would you also like a visual HTML version in the same ten-stage structure as the app? Generate HTML only after opt-in, unless already requested.

- [Scoped evidence intake](01-milestone.md) — C1, C2
- [Draft checks and human packet](02-milestone.md) — C3, C4, C5
