# Build overview

> PASS | DESIGN ONLY. self-review; round 3.

Design a small daily report that joins two CSV files by order ID. One has promised-delivery timestamps and the other actual-delivery timestamps, both ISO UTC. Flag delivered orders more than 24 hours late and export a CSV for the operations team. No emails, remote updates, forecasting or conversational interface.

Load one milestone file at a time. Contracts below are selected by component; full source is ../design.json. Test IDs resolve to complete fixtures in ../eval-set.json. Do not load the entire design unless a dependency requires it.

Code owns money, identity, dates and limits. The agent never holds write authority. Keep proposed policies and owners distinct from verified facts. Launch blockers: ../assumptions.md. Complete rollout gates and owners: ../PRD.md#rollout.

After delivering DESIGN.pdf, ask the user: Would you also like a visual HTML version in the same ten-stage structure as the app? Generate HTML only after opt-in, unless already requested.

- [Run controller and immutable read](01-milestone.md) — C1
- [CSV integrity validator](02-milestone.md) — C2
- [Exact join and renderer](03-milestone.md) — C3
- [Atomic local publisher](04-milestone.md) — C4
- [Read-only publication reconciler](05-milestone.md) — C5
- [Local outcome recorder](06-milestone.md) — C6
