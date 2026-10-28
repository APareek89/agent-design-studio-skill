# Build overview

> NEEDS-WORK | DESIGN ONLY. independent-agent; round 1.

Design a complaint assistant for a telecom provider. Customers report network outages, poor speed and billing errors. The assistant should investigate using account, billing and service records, explain findings and resolve eligible service credits. Larger or unclear refunds need a human supervisor and may wait up to 48 hours. Keep customers informed, avoid duplicate refunds and use only the right customer's active service connection. Propose any missing policies as assumptions, not real company rules.


Load one milestone file at a time. Contracts below are selected by component; full source is ../design.json. Test IDs resolve to complete fixtures in ../eval-set.json. Do not load the entire design unless a dependency requires it.

Code owns money, identity, dates and limits. The agent never holds write authority. Keep proposed policies and owners distinct from verified facts. Launch blockers: ../assumptions.md.

After delivering DESIGN.pdf, ask the user: Would you also like a visual HTML version in the same ten-stage structure as the app? Generate HTML only after opt-in, unless already requested.

- [Secure the account, evidence and case proof](01-milestone.md) — C1, C11, C2, C3
- [Compute and approve exact plans](02-milestone.md) — C4, C5, C6
- [Post once and prove the result](03-milestone.md) — C10, C7, C8, C9
