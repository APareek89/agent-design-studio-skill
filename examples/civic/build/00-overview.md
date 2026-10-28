# Build overview

> PASS | DESIGN ONLY. self-review; round 2.

I need a system for a small city team to handle streetlight repair requests: classify reports, find existing tickets and route to the right maintenance crew. Five operators handle about 200 reports a day. It must not remotely control equipment.

Load one milestone file at a time. Contracts below are selected by component; full source is ../design.json. Test IDs resolve to complete fixtures in ../eval-set.json. Do not load the entire design unless a dependency requires it.

Code owns money, identity, dates and limits. The agent never holds write authority. Keep proposed policies and owners distinct from verified facts. Launch blockers: ../assumptions.md. Complete rollout gates and owners: ../PRD.md#rollout.

After delivering DESIGN.pdf, ask the user: Would you also like a visual HTML version in the same ten-stage structure as the app? Generate HTML only after opt-in, unless already requested.

- [Intake and scope gate part 1](01-milestone.md) — C1
- [Authoritative context read adapter part 1](02-milestone.md) — C2
- [Bounded text triage judgement part 1](03-milestone.md) — C3
- [Route resolver and immutable plan validator part 1](04-milestone.md) — C4
- [Operator decision queue part 1](05-milestone.md) — C5
- [Conditional ticket writer part 1](06-milestone.md) — C6
- [Read-only commit reconciler part 1](07-milestone.md) — C7
- [Case journal, owner timers and status projection part 1](08-milestone.md) — C8
- [Case journal, owner timers and status projection part 2](09-milestone.md) — C8
- [Case journal, owner timers and status projection part 3](10-milestone.md) — C8
