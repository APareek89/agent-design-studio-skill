# Prove handoff and recover

> PASS | DESIGN ONLY. self-review; round 4.

Depends on earlier milestones where their outputs are inputs below. Cross-milestone shared types are read by ID from ../design.json, not copied.

## Selected contracts

### C5 · Readback and reconciliation

GET packet by operation key under tenant-scoped recovery service; compares full body and assigned reviewer, not just status. Read every 10s up to three times. Signed callbacks deduplicated by record ID and event sequence; expired caller session does not remove service recovery authority. Ambiguous commit freezes changed intent and is owned by Platform on-call until lookup resolves. Never insert during recovery. absent/pending/unavailable after bound => unresolved operation retained for manual reconciliation, no completion. Cancellation before insert cancels run; after insert or unknown result records operator intent in operations ledger and cannot revoke a clinical claim decision, since none exists.

Reasoning: Keeps evidence, authority and recovery explicit.

Assumptions:

- H3

Data:

```json
{
  "group": "Code: tools",
  "taskIds": [
    "T4",
    "T5"
  ],
  "inputs": [
    "operationKey: required trusted key",
    "expectedBody: required immutable packet+escaped narrative",
    "recovery: required attempt 0..3 with trusted server clock"
  ],
  "outputs": [
    "result: found {recordId,queueId,reviewerId,bodyVersion}|absent|mismatch|pending|unavailable",
    "verifiedRecordId:string! on a proven record outcome; explicit projection of existing case/posting record ID, absent on failed or uncertain outcomes"
  ],
  "whyCode": "Identity, rule arithmetic, versions, operation keys and durable proof require repeatable code.",
  "approvalRule": "Authenticated claims preparation role may save draft only; no final decision or payment permission."
}
```


Sources:

- context / user-brief: Design a health insurance claim adjudication assistant for inpatient hospital claims. It should read submitted policy and hospital documents, assess coverage and eligible charges, recommend or process eligible claims, and route exceptions and rejections for review. Policies can change over time and bills may include room-rent limits. Protect personal medical data, explain decisions with evidence and propose any missing rules as assumptions, not verified insurance or medical advice.

- hypothesis / H3: Adapters support tenant-scoped reads and an atomic, conditional review-packet insert with unique submission key, immutable body, assigned reviewer and durable record lookup.

### C6 · Record proof check

Require nonempty durable packet record ID, matching tenant/submission/body versions and actual reviewer assignment. A provisional local ID or model phrase cannot prove completion. Existing queue owns acknowledgement and overdue alerts under H5; no person approval is claimed by mere assignment. Explicit proof projection: Only an authorized found readback with matching full record body, tenant, claim, operation and current version supplies recordId. Missing/empty/nonmatching ID rejects saved status.

Reasoning: Keeps evidence, authority and recovery explicit.

Assumptions:

- H3

Data:

```json
{
  "group": "Code: validation",
  "taskIds": [
    "T5"
  ],
  "inputs": [
    "readback: required C5 found record and expected immutable body",
    "verifiedRecordId:string! on a proven outcome; required nonempty trusted record projection, otherwise reject proof"
  ],
  "outputs": [
    "proof: valid {recordId,queueId,reviewerId}|invalid"
  ],
  "whyCode": "Identity, rule arithmetic, versions, operation keys and durable proof require repeatable code.",
  "approvalRule": "Authenticated claims preparation role may save draft only; no final decision or payment permission."
}
```


Sources:

- context / user-brief: Design a health insurance claim adjudication assistant for inpatient hospital claims. It should read submitted policy and hospital documents, assess coverage and eligible charges, recommend or process eligible claims, and route exceptions and rejections for review. Policies can change over time and bills may include room-rent limits. Protect personal medical data, explain decisions with evidence and propose any missing rules as assumptions, not verified insurance or medical advice.

- hypothesis / H3: Adapters support tenant-scoped reads and an atomic, conditional review-packet insert with unique submission key, immutable body, assigned reviewer and durable record lookup.

### C7 · Read-only status view

Renders session UI only; no messages or external writes. completed_review_packet means ready for review, not claim adjudicated. Pending recovery points to operation key and on-call; access denied discloses no member data. Reviewer queue sends existing-system notices under H5, requiring verification before launch.

Reasoning: Keeps evidence, authority and recovery explicit.

Assumptions:

- H3

Data:

```json
{
  "group": "Code: tools",
  "taskIds": [
    "T5"
  ],
  "inputs": [
    "status: required completed_review_packet|blocked|pending_reconciliation",
    "proof: optional required only for completed_review_packet"
  ],
  "outputs": [
    "view: required escaped staff status with existing record link or owned next step"
  ],
  "whyCode": "Identity, rule arithmetic, versions, operation keys and durable proof require repeatable code.",
  "approvalRule": "Authenticated claims preparation role may save draft only; no final decision or payment permission."
}
```


Sources:

- context / user-brief: Design a health insurance claim adjudication assistant for inpatient hospital claims. It should read submitted policy and hospital documents, assess coverage and eligible charges, recommend or process eligible claims, and route exceptions and rejections for review. Policies can change over time and bills may include room-rent limits. Protect personal medical data, explain decisions with evidence and propose any missing rules as assumptions, not verified insurance or medical advice.

- hypothesis / H3: Adapters support tenant-scoped reads and an atomic, conditional review-packet insert with unique submission key, immutable body, assigned reviewer and durable record lookup.

## Workflow rules

### W5 · Check saved record

{"state": "Check saved record", "transitions": [{"to": "W6", "when": "C5.result == found", "mode": "exclusive; result enum has one value; cancellation checked first before insert"}, {"to": "W8", "when": "C5.result in [absent,mismatch,pending,unavailable] after three reads", "mode": "exclusive; result enum has one value; cancellation checked first before insert"}], "failureDisposition": "W8 is blocked before insert; after uncertain insert it is pending_reconciliation owned by Platform on-call. No final claim outcome.", "timeout": "C2 30s per call; other I/O 10s per call; local validation 2s; status render 2s.", "retryPolicy": "C1 one read retry; C2 one retry then abstain; C4 zero retries; C5 three reads 10s apart, then W8. Local steps zero retries.", "terminalDisposition": "", "guardBindings": {"C1.result": "C1.case.result enum from authenticated API", "C2.valid": "code JSON and citation validator; retry_exhausted_with_abstention code counter <=2", "C3.status": "C3.status enum using fresh registry versions and authority", "C4.result": "typed adapter response or code timeout classification", "C5.result": "C5.result enum after bounded lookup; retry count server durable integer", "C6.proof": "C6.proof enum", "cancelled_before_insert": "authenticated staff cancel event bound to submission; serial transaction cancel check; after uncertain insert remains pending recovery"}}

Reasoning: Keeps evidence, authority and recovery explicit.

Assumptions:

- H1

Data:

```json
{
  "componentId": "C5",
  "taskIds": [
    "T4",
    "T5"
  ],
  "next": [
    "W6",
    "W8"
  ],
  "decision": true,
  "example": "S17: verified capped charges produce draft; saved packet RP17 is read back before ready-for-review status."
}
```


Sources:

- context / user-brief: Design a health insurance claim adjudication assistant for inpatient hospital claims. It should read submitted policy and hospital documents, assess coverage and eligible charges, recommend or process eligible claims, and route exceptions and rejections for review. Policies can change over time and bills may include room-rent limits. Protect personal medical data, explain decisions with evidence and propose any missing rules as assumptions, not verified insurance or medical advice.

- hypothesis / H1: First release creates review packets only. Claims staff approve all eligible recommendations, exceptions and rejection candidates; no settlement, denial notice or payment is automated.

### W6 · Prove handoff

{"state": "Prove handoff", "transitions": [{"to": "W7", "when": "C6.proof == valid", "mode": "exclusive; result enum has one value; cancellation checked first before insert"}, {"to": "W8", "when": "C6.proof == invalid", "mode": "exclusive; result enum has one value; cancellation checked first before insert"}], "failureDisposition": "W8 is blocked before insert; after uncertain insert it is pending_reconciliation owned by Platform on-call. No final claim outcome.", "timeout": "C2 30s per call; other I/O 10s per call; local validation 2s; status render 2s.", "retryPolicy": "C1 one read retry; C2 one retry then abstain; C4 zero retries; C5 three reads 10s apart, then W8. Local steps zero retries.", "terminalDisposition": "", "guardBindings": {"C1.result": "C1.case.result enum from authenticated API", "C2.valid": "code JSON and citation validator; retry_exhausted_with_abstention code counter <=2", "C3.status": "C3.status enum using fresh registry versions and authority", "C4.result": "typed adapter response or code timeout classification", "C5.result": "C5.result enum after bounded lookup; retry count server durable integer", "C6.proof": "C6.proof enum", "cancelled_before_insert": "authenticated staff cancel event bound to submission; serial transaction cancel check; after uncertain insert remains pending recovery"}, "bindings": {"verifiedRecordId": {"sourceComponentId": "C5", "sourceField": "verifiedRecordId"}}, "recordProofPolicy": "Only an authorized found readback with matching full record body, tenant, claim, operation and current version supplies recordId. Missing/empty/nonmatching ID rejects saved status."}

Reasoning: Keeps evidence, authority and recovery explicit.

Assumptions:

- H1

Data:

```json
{
  "componentId": "C6",
  "taskIds": [
    "T5"
  ],
  "next": [
    "W7",
    "W8"
  ],
  "decision": true,
  "example": "S17: verified capped charges produce draft; saved packet RP17 is read back before ready-for-review status."
}
```


Sources:

- context / user-brief: Design a health insurance claim adjudication assistant for inpatient hospital claims. It should read submitted policy and hospital documents, assess coverage and eligible charges, recommend or process eligible claims, and route exceptions and rejections for review. Policies can change over time and bills may include room-rent limits. Protect personal medical data, explain decisions with evidence and propose any missing rules as assumptions, not verified insurance or medical advice.

- hypothesis / H1: First release creates review packets only. Claims staff approve all eligible recommendations, exceptions and rejection candidates; no settlement, denial notice or payment is automated.

### W7 · Ready for staff review

{"state": "Ready for staff review", "transitions": [], "failureDisposition": "W8 is blocked before insert; after uncertain insert it is pending_reconciliation owned by Platform on-call. No final claim outcome.", "timeout": "C2 30s per call; other I/O 10s per call; local validation 2s; status render 2s.", "retryPolicy": "C1 one read retry; C2 one retry then abstain; C4 zero retries; C5 three reads 10s apart, then W8. Local steps zero retries.", "terminalDisposition": "Durable review packet and assigned reviewer confirmed; claim pending staff adjudication.", "guardBindings": {"C1.result": "C1.case.result enum from authenticated API", "C2.valid": "code JSON and citation validator; retry_exhausted_with_abstention code counter <=2", "C3.status": "C3.status enum using fresh registry versions and authority", "C4.result": "typed adapter response or code timeout classification", "C5.result": "C5.result enum after bounded lookup; retry count server durable integer", "C6.proof": "C6.proof enum", "cancelled_before_insert": "authenticated staff cancel event bound to submission; serial transaction cancel check; after uncertain insert remains pending recovery"}}

Reasoning: Keeps evidence, authority and recovery explicit.

Assumptions:

- H1

Data:

```json
{
  "componentId": "C7",
  "taskIds": [
    "T5"
  ],
  "next": [],
  "decision": false,
  "example": "S17: verified capped charges produce draft; saved packet RP17 is read back before ready-for-review status."
}
```


Sources:

- context / user-brief: Design a health insurance claim adjudication assistant for inpatient hospital claims. It should read submitted policy and hospital documents, assess coverage and eligible charges, recommend or process eligible claims, and route exceptions and rejections for review. Policies can change over time and bills may include room-rent limits. Protect personal medical data, explain decisions with evidence and propose any missing rules as assumptions, not verified insurance or medical advice.

- hypothesis / H1: First release creates review packets only. Claims staff approve all eligible recommendations, exceptions and rejection candidates; no settlement, denial notice or payment is automated.

### W8 · Show owned pending state

{"state": "Show owned pending state", "transitions": [], "failureDisposition": "W8 is blocked before insert; after uncertain insert it is pending_reconciliation owned by Platform on-call. No final claim outcome.", "timeout": "C2 30s per call; other I/O 10s per call; local validation 2s; status render 2s.", "retryPolicy": "C1 one read retry; C2 one retry then abstain; C4 zero retries; C5 three reads 10s apart, then W8. Local steps zero retries.", "terminalDisposition": "Blocked/pending state, owned next step and operation key if any; never claim processed.", "guardBindings": {"C1.result": "C1.case.result enum from authenticated API", "C2.valid": "code JSON and citation validator; retry_exhausted_with_abstention code counter <=2", "C3.status": "C3.status enum using fresh registry versions and authority", "C4.result": "typed adapter response or code timeout classification", "C5.result": "C5.result enum after bounded lookup; retry count server durable integer", "C6.proof": "C6.proof enum", "cancelled_before_insert": "authenticated staff cancel event bound to submission; serial transaction cancel check; after uncertain insert remains pending recovery"}}

Reasoning: Keeps evidence, authority and recovery explicit.

Assumptions:

- H1

Data:

```json
{
  "componentId": "C7",
  "taskIds": [
    "T5"
  ],
  "next": [],
  "decision": false,
  "example": "S17: verified capped charges produce draft; saved packet RP17 is read back before ready-for-review status."
}
```


Sources:

- context / user-brief: Design a health insurance claim adjudication assistant for inpatient hospital claims. It should read submitted policy and hospital documents, assess coverage and eligible charges, recommend or process eligible claims, and route exceptions and rejections for review. Policies can change over time and bills may include room-rent limits. Protect personal medical data, explain decisions with evidence and propose any missing rules as assumptions, not verified insurance or medical advice.

- hypothesis / H1: First release creates review packets only. Claims staff approve all eligible recommendations, exceptions and rejection candidates; no settlement, denial notice or payment is automated.

## Required tests

For each ID below, load ../eval-set.json items[id].data.input, .expected and .passRule. These are the full fixture, expected result and exact assertions; no inherited test context is assumed.

- EV1: Valid room cap draft
- EV8: Save committed but response lost
- EV9: Missing proof cannot complete
- EV10: Unknown remains owned and frozen
- EV15: Unassigned queue and overdue ownership
- EV18: Held-out evidence and rules
- EV19: Operational safety monitor
- EV20: All-case release gate
## Acceptance criteria

- All selected component contracts and EV assertions pass in the business harness; H1-H5 remain external evidence gates.
