# Save a safe review packet

> PASS | DESIGN ONLY. self-review; round 2.

Depends on earlier milestones where their outputs are inputs below. Cross-milestone shared types are read by ID from ../design.json, not copied.

## Selected contracts

### C4 · Review packet store

Proposed adapter POST review-packets atomically inserts immutable packet and assignment, notifies staff through the existing queue, and stores operation key under a unique constraint. No payment or final-adjudication capability. Server rechecks authority, claimVersion and ruleVersion inside the transaction; 10s timeout. Exact duplicate returns existing record after body equality; changed intent conflicts. No write retry after timeout. Readback is required even on success.

Reasoning: Keeps evidence, authority and recovery explicit.

Assumptions:

- H3

Data:

```json
{
  "group": "Code: tools",
  "taskIds": [
    "T4"
  ],
  "inputs": [
    "packet: required immutable C3 packet, one claim and one tenant",
    "narrative: required C2 narrative or literal abstention; escaped and stored as untrusted draft",
    "operationKey: required trusted submissionId+claimVersion+bodyVersion"
  ],
  "outputs": [
    "result: committed {recordId,bodyVersion,queueId,reviewerId}|conflict|denied|invalid|TIMEOUT|unknown_commit"
  ],
  "whyCode": "Identity, rule arithmetic, versions, operation keys and durable proof require repeatable code.",
  "approvalRule": "Authenticated claims preparation role may save draft only; no final decision or payment permission."
}
```


Sources:

- context / user-brief: Design a health insurance claim adjudication assistant for inpatient hospital claims. It should read submitted policy and hospital documents, assess coverage and eligible charges, recommend or process eligible claims, and route exceptions and rejections for review. Policies can change over time and bills may include room-rent limits. Protect personal medical data, explain decisions with evidence and propose any missing rules as assumptions, not verified insurance or medical advice.

- hypothesis / H3: Adapters support tenant-scoped reads and an atomic, conditional review-packet insert with unique submission key, immutable body, assigned reviewer and durable record lookup.

## Workflow rules

### W4 · Save review packet

{"state": "Save review packet", "transitions": [{"to": "W5", "when": "C4.result == committed", "mode": "exclusive; result enum has one value; cancellation checked first before insert"}, {"to": "W5", "when": "C4.result == TIMEOUT", "mode": "exclusive; result enum has one value; cancellation checked first before insert"}, {"to": "W5", "when": "C4.result == unknown_commit", "mode": "exclusive; result enum has one value; cancellation checked first before insert"}, {"to": "W5", "when": "C4.result == conflict", "mode": "exclusive; result enum has one value; cancellation checked first before insert"}, {"to": "W8", "when": "C4.result in [denied,invalid]", "mode": "exclusive; result enum has one value; cancellation checked first before insert"}], "failureDisposition": "W8 is blocked before insert; after uncertain insert it is pending_reconciliation owned by Platform on-call. No final claim outcome.", "timeout": "C2 30s per call; other I/O 10s per call; local validation 2s; status render 2s.", "retryPolicy": "C1 one read retry; C2 one retry then abstain; C4 zero retries; C5 three reads 10s apart, then W8. Local steps zero retries.", "terminalDisposition": "", "guardBindings": {"C1.result": "C1.case.result enum from authenticated API", "C2.valid": "code JSON and citation validator; retry_exhausted_with_abstention code counter <=2", "C3.status": "C3.status enum using fresh registry versions and authority", "C4.result": "typed adapter response or code timeout classification", "C5.result": "C5.result enum after bounded lookup; retry count server durable integer", "C6.proof": "C6.proof enum", "cancelled_before_insert": "authenticated staff cancel event bound to submission; serial transaction cancel check; after uncertain insert remains pending recovery"}}

Reasoning: Keeps evidence, authority and recovery explicit.

Assumptions:

- H1

Data:

```json
{
  "componentId": "C4",
  "taskIds": [
    "T4"
  ],
  "next": [
    "W5",
    "W8"
  ],
  "decision": true,
  "example": "S17: verified capped charges produce draft; saved packet RP17 is read back before ready-for-review status."
}
```


Sources:

- context / user-brief: Design a health insurance claim adjudication assistant for inpatient hospital claims. It should read submitted policy and hospital documents, assess coverage and eligible charges, recommend or process eligible claims, and route exceptions and rejections for review. Policies can change over time and bills may include room-rent limits. Protect personal medical data, explain decisions with evidence and propose any missing rules as assumptions, not verified insurance or medical advice.

- hypothesis / H1: First release creates review packets only. Claims staff approve all eligible recommendations, exceptions and rejection candidates; no settlement, denial notice or payment is automated.

## Required tests

For each ID below, load ../eval-set.json items[id].data.input, .expected and .passRule. These are the full fixture, expected result and exact assertions; no inherited test context is assumed.

- EV1: Valid room cap draft
- EV6: Concurrent duplicate
- EV7: Revoked role at commit
- EV8: Save committed but response lost
- EV10: Unknown remains owned and frozen
- EV12: Concurrent policy change
- EV15: Unassigned queue and overdue ownership
- EV16: Exclusion is a review candidate
- EV18: Held-out evidence and rules
- EV19: Operational safety monitor
- EV20: All-case release gate
## Acceptance criteria

- All selected component contracts and EV assertions pass in the business harness; H1-H5 remain external evidence gates.
