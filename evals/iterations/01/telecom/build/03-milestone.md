# Post once and prove the result

> PASS | DESIGN ONLY. self-review; round 2.

Depends on earlier milestones where their outputs are inputs below. Cross-milestone shared types are read by ID from ../design.json, not copied.

## Selected contracts

### C10 · Verify outcome proof

Read persisted case row and ledger receipt; match tenant/customer/connection/eventKey/operation/amount/currency. Credit completion needs postingId; pending/no-credit/cancelled needs caseId and owner/reason. Record proof failure keeps case open under Billing Operations.

Reasoning: Bound responsibility to a testable contract.

Data:

```json
{
  "group": "Code: validation",
  "taskIds": [
    "T3.3",
    "T4"
  ],
  "inputs": [
    "case: persisted internal workflow caseId/status/owner, required",
    "receipt: C8 or C9 proof iff credit claimed"
  ],
  "outputs": [
    "status: enum PROVEN_CREDIT|PROVEN_CASE|MISSING_PROOF",
    "summary: customer-safe outcome and next step"
  ],
  "whyCode": "Read persisted case row and ledger receipt; match tenant/customer/connection/eventKey/operation/amount/currency. Credit completion needs postingId; pending/no-credit/cancelled needs caseId and owner/reason. Record proof failure keeps case open under Billing Operations.",
  "approvalRule": "Only PROVEN_CREDIT may claim credit posted; cancellation after commit is credited-with-review, never silently undone."
}
```


Sources:

- context / user-brief: Design a complaint assistant for a telecom provider. Customers report network outages, poor speed and billing errors. The assistant should investigate using account, billing and service records, explain findings and resolve eligible service credits. Larger or unclear refunds need a human supervisor and may wait up to 48 hours. Keep customers informed, avoid duplicate refunds and use only the right customer's active service connection. Propose any missing policies as assumptions, not real company rules.

### C7 · Recheck posting authority

Re-fetch active connection/ownership, policy and invoice versions, remaining entitlement and eventKey immediately before reservation/post. Lock event key and compare plan/approval versions/expiry. Code reconstructs every financial field from authoritative evidence; changed plan requires a new approval. API must recheck versions atomically at commit or H2 fails.

Reasoning: Bound responsibility to a testable contract.

Assumptions:

- H2

Data:

```json
{
  "group": "Code: validation",
  "taskIds": [
    "T3.1"
  ],
  "inputs": [
    "plan: immutable C4 plan or supervisor-approved replacement, required",
    "approval: signed C5 approval iff HUMAN, otherwise policy authority",
    "state: live account/policy/ledger and cancellation state, required"
  ],
  "outputs": [
    "validatedPlan: exact trusted plan or null",
    "status: enum VALID|STALE|REVOKED|DUPLICATE|CANCELLED|UNAVAILABLE"
  ],
  "whyCode": "Re-fetch active connection/ownership, policy and invoice versions, remaining entitlement and eventKey immediately before reservation/post. Lock event key and compare plan/approval versions/expiry. Code reconstructs every financial field from authoritative evidence; changed plan requires a new approval. API must recheck versions atomically at commit or H2 fails.",
  "approvalRule": "Policy AUTO or supervisor signature binds full immutable plan including amount/currency/period/tax/accounting. Customer logout does not revoke an already delegated policy operation; explicit authority revocation does."
}
```


Sources:

- hypothesis / H2: Account, service and billing adapters must offer authenticated tenant/subject reads, active connection version checks, scoped credit posting with a unique business-event key and definitive operation readback.

### C8 · Post one service credit

POST service-credit resource with exact trusted plan, operationId and eventKey. 5s timeout; no internal retry. Backend atomic unique event key and preconditions required. POSTED means durable ledger receipt, not HTTP 200 alone. All rejects imply zero new posting; ambiguous responses use UNKNOWN_COMMIT.

Reasoning: Bound responsibility to a testable contract.

Assumptions:

- H2

Data:

```json
{
  "group": "Code: tools",
  "taskIds": [
    "T3.1"
  ],
  "inputs": [
    "plan: C7.validatedPlan, required",
    "operationId: durable UUID bound one-to-one to eventKey, required"
  ],
  "outputs": [
    "result: enum POSTED|REJECTED|TIMEOUT|UNKNOWN_COMMIT",
    "postingId: nonempty ledger ID iff POSTED",
    "receipt: eventKey/operationId/planVersion/amountMinor/currency/connectionId proof iff POSTED",
    "reason: enum NONE|STALE|REVOKED|DUPLICATE|CANCELLED|INVALID"
  ],
  "whyCode": "POST service-credit resource with exact trusted plan, operationId and eventKey. 5s timeout; no internal retry. Backend atomic unique event key and preconditions required. POSTED means durable ledger receipt, not HTTP 200 alone. All rejects imply zero new posting; ambiguous responses use UNKNOWN_COMMIT.",
  "approvalRule": "Separate credit-only credential for tenant/active connection; no cash refund, invoice edit or model tool grant."
}
```


Sources:

- hypothesis / H2: Account, service and billing adapters must offer authenticated tenant/subject reads, active connection version checks, scoped credit posting with a unique business-event key and definitive operation readback.

### C9 · Reconcile uncertain posting

Read authoritative operation ledger by operationId and eventKey under durable service identity. Query at 5s, 30s and 120s max; COMMITTED verifies receipt, DEFINITIVELY_ABSENT requires final provider guarantee and can re-enter C7 once with same key/operation. Otherwise freeze event key as pending reconciliation for Billing Operations; hourly read-only checks for 24h then duty-manager ownership. Never expire reservation into another writer.

Reasoning: Bound responsibility to a testable contract.

Assumptions:

- H2

Data:

```json
{
  "group": "Code: tools",
  "taskIds": [
    "T3.1",
    "T4"
  ],
  "inputs": [
    "operationId: C8 operationId, required",
    "eventKey: immutable plan eventKey, required"
  ],
  "outputs": [
    "result: enum COMMITTED|DEFINITIVELY_ABSENT|UNRESOLVED",
    "postingId: required iff COMMITTED",
    "receipt: original financial proof iff COMMITTED"
  ],
  "whyCode": "Read authoritative operation ledger by operationId and eventKey under durable service identity. Query at 5s, 30s and 120s max; COMMITTED verifies receipt, DEFINITIVELY_ABSENT requires final provider guarantee and can re-enter C7 once with same key/operation. Otherwise freeze event key as pending reconciliation for Billing Operations; hourly read-only checks for 24h then duty-manager ownership. Never expire reservation into another writer.",
  "approvalRule": "Read-only survives customer session expiry; conflicting new intent cannot post while unknown."
}
```


Sources:

- hypothesis / H2: Account, service and billing adapters must offer authenticated tenant/subject reads, active connection version checks, scoped credit posting with a unique business-event key and definitive operation readback.

## Workflow rules

### W8 · Recheck amount and permission

{"state": "Persisted CaseState: caseId, tenant scope if authenticated, owner, stateVersion, enqueueAt UTC, noticeMask, retryCount, cancellation flag, eventKey lock, operationId and receipt. Predicate values are typed outputs of the C component in this node; retryCount:uint starts 0 and increments only on W10\u2192W8, cancelled:bool from authenticated case cancellation event; timers from durable UTC scheduler. Cancellation > decision > notice precedence. Durable caseId is allocated before W1; no financial effect. ", "transitions": [{"to": "W9", "when": "C7.status == VALID", "mode": "exclusive"}, {"to": "W12", "when": "C7.status != VALID", "mode": "exclusive"}], "failureDisposition": "Persist owned pending case; no blind financial retry; recovery owner Billing Operations for money and Support Operations otherwise.", "timeout": "48 elapsed hours for W6; model 10s per attempt max2; reads 5s max2; C8 5s max1; reconciliation initial 120s window.", "retryPolicy": "Only model/read schema retries once; writer retry only W10 authoritative absent then W8 once. Notice sequence max2; scheduler never resets 48h clock.", "terminalDisposition": ""}

Reasoning: Bound responsibility to a testable contract.

Data:

```json
{
  "componentId": "C7",
  "taskIds": [
    "T3.1"
  ],
  "next": [
    "W9",
    "W12"
  ],
  "decision": true,
  "example": "Recheck amount and permission"
}
```


Sources:

- context / user-brief: Design a complaint assistant for a telecom provider. Customers report network outages, poor speed and billing errors. The assistant should investigate using account, billing and service records, explain findings and resolve eligible service credits. Larger or unclear refunds need a human supervisor and may wait up to 48 hours. Keep customers informed, avoid duplicate refunds and use only the right customer's active service connection. Propose any missing policies as assumptions, not real company rules.

### W9 · Post the service credit

{"state": "Persisted CaseState: caseId, tenant scope if authenticated, owner, stateVersion, enqueueAt UTC, noticeMask, retryCount, cancellation flag, eventKey lock, operationId and receipt. Predicate values are typed outputs of the C component in this node; retryCount:uint starts 0 and increments only on W10\u2192W8, cancelled:bool from authenticated case cancellation event; timers from durable UTC scheduler. Cancellation > decision > notice precedence. Durable caseId is allocated before W1; no financial effect. ", "transitions": [{"to": "W11", "when": "C8.result == POSTED", "mode": "exclusive"}, {"to": "W12", "when": "C8.result == REJECTED", "mode": "exclusive"}, {"to": "W10", "when": "C8.result == TIMEOUT", "mode": "exclusive"}, {"to": "W10", "when": "C8.result == UNKNOWN_COMMIT", "mode": "exclusive"}], "failureDisposition": "Persist owned pending case; no blind financial retry; recovery owner Billing Operations for money and Support Operations otherwise.", "timeout": "48 elapsed hours for W6; model 10s per attempt max2; reads 5s max2; C8 5s max1; reconciliation initial 120s window.", "retryPolicy": "Only model/read schema retries once; writer retry only W10 authoritative absent then W8 once. Notice sequence max2; scheduler never resets 48h clock.", "terminalDisposition": ""}

Reasoning: Bound responsibility to a testable contract.

Data:

```json
{
  "componentId": "C8",
  "taskIds": [
    "T3.1"
  ],
  "next": [
    "W11",
    "W12",
    "W10"
  ],
  "decision": true,
  "example": "Post the service credit"
}
```


Sources:

- context / user-brief: Design a complaint assistant for a telecom provider. Customers report network outages, poor speed and billing errors. The assistant should investigate using account, billing and service records, explain findings and resolve eligible service credits. Larger or unclear refunds need a human supervisor and may wait up to 48 hours. Keep customers informed, avoid duplicate refunds and use only the right customer's active service connection. Propose any missing policies as assumptions, not real company rules.

### W10 · Check an uncertain posting

{"state": "Persisted CaseState: caseId, tenant scope if authenticated, owner, stateVersion, enqueueAt UTC, noticeMask, retryCount, cancellation flag, eventKey lock, operationId and receipt. Predicate values are typed outputs of the C component in this node; retryCount:uint starts 0 and increments only on W10\u2192W8, cancelled:bool from authenticated case cancellation event; timers from durable UTC scheduler. Cancellation > decision > notice precedence. Durable caseId is allocated before W1; no financial effect. ", "transitions": [{"to": "W11", "when": "C9.result == COMMITTED", "mode": "exclusive"}, {"to": "W8", "when": "C9.result == DEFINITIVELY_ABSENT and retryCount < 1 and not cancelled", "mode": "exclusive"}, {"to": "W12", "when": "C9.result == UNRESOLVED or (C9.result == DEFINITIVELY_ABSENT and (retryCount >= 1 or cancelled))", "mode": "exclusive"}], "failureDisposition": "Persist owned pending case; no blind financial retry; recovery owner Billing Operations for money and Support Operations otherwise.", "timeout": "48 elapsed hours for W6; model 10s per attempt max2; reads 5s max2; C8 5s max1; reconciliation initial 120s window.", "retryPolicy": "Only model/read schema retries once; writer retry only W10 authoritative absent then W8 once. Notice sequence max2; scheduler never resets 48h clock.", "terminalDisposition": ""}

Reasoning: Bound responsibility to a testable contract.

Data:

```json
{
  "componentId": "C9",
  "taskIds": [
    "T3.1",
    "T4"
  ],
  "next": [
    "W11",
    "W8",
    "W12"
  ],
  "decision": true,
  "example": "Check an uncertain posting"
}
```


Sources:

- context / user-brief: Design a complaint assistant for a telecom provider. Customers report network outages, poor speed and billing errors. The assistant should investigate using account, billing and service records, explain findings and resolve eligible service credits. Larger or unclear refunds need a human supervisor and may wait up to 48 hours. Keep customers informed, avoid duplicate refunds and use only the right customer's active service connection. Propose any missing policies as assumptions, not real company rules.

### W11 · Verify credit proof

{"state": "Persisted CaseState: caseId, tenant scope if authenticated, owner, stateVersion, enqueueAt UTC, noticeMask, retryCount, cancellation flag, eventKey lock, operationId and receipt. Predicate values are typed outputs of the C component in this node; retryCount:uint starts 0 and increments only on W10\u2192W8, cancelled:bool from authenticated case cancellation event; timers from durable UTC scheduler. Cancellation > decision > notice precedence. Durable caseId is allocated before W1; no financial effect. ", "transitions": [{"to": "W13", "when": "C10.status == PROVEN_CREDIT", "mode": "exclusive"}, {"to": "W12", "when": "C10.status != PROVEN_CREDIT", "mode": "exclusive"}], "failureDisposition": "Persist owned pending case; no blind financial retry; recovery owner Billing Operations for money and Support Operations otherwise.", "timeout": "48 elapsed hours for W6; model 10s per attempt max2; reads 5s max2; C8 5s max1; reconciliation initial 120s window.", "retryPolicy": "Only model/read schema retries once; writer retry only W10 authoritative absent then W8 once. Notice sequence max2; scheduler never resets 48h clock.", "terminalDisposition": ""}

Reasoning: Bound responsibility to a testable contract.

Data:

```json
{
  "componentId": "C10",
  "taskIds": [
    "T4"
  ],
  "next": [
    "W13",
    "W12"
  ],
  "decision": true,
  "example": "Verify credit proof"
}
```


Sources:

- context / user-brief: Design a complaint assistant for a telecom provider. Customers report network outages, poor speed and billing errors. The assistant should investigate using account, billing and service records, explain findings and resolve eligible service credits. Larger or unclear refunds need a human supervisor and may wait up to 48 hours. Keep customers informed, avoid duplicate refunds and use only the right customer's active service connection. Propose any missing policies as assumptions, not real company rules.

### W12 · Keep case proof and owner

{"state": "Persisted CaseState: caseId, tenant scope if authenticated, owner, stateVersion, enqueueAt UTC, noticeMask, retryCount, cancellation flag, eventKey lock, operationId and receipt. Predicate values are typed outputs of the C component in this node; retryCount:uint starts 0 and increments only on W10\u2192W8, cancelled:bool from authenticated case cancellation event; timers from durable UTC scheduler. Cancellation > decision > notice precedence. Durable caseId is allocated before W1; no financial effect. Preserve reason AUTH_FAILED/SELECTION_REQUIRED/INACTIVE/NO_CREDIT/DENIED/CANCELLED/STALE/REVOKED/DUPLICATE/OVERDUE/UNAVAILABLE/PENDING_RECONCILIATION/MISSING_PROOF from prior event. If case persistence cannot be read, do not exit: operational alarm and durable transaction recovery; no customer completion.", "transitions": [{"to": "W14", "when": "caseId exists; C10.status in {PROVEN_CASE,MISSING_PROOF}", "mode": "exclusive"}], "failureDisposition": "Persist owned pending case; no blind financial retry; recovery owner Billing Operations for money and Support Operations otherwise.", "timeout": "48 elapsed hours for W6; model 10s per attempt max2; reads 5s max2; C8 5s max1; reconciliation initial 120s window.", "retryPolicy": "Only model/read schema retries once; writer retry only W10 authoritative absent then W8 once. Notice sequence max2; scheduler never resets 48h clock.", "terminalDisposition": ""}

Reasoning: Bound responsibility to a testable contract.

Data:

```json
{
  "componentId": "C10",
  "taskIds": [
    "T3.3",
    "T4"
  ],
  "next": [
    "W14"
  ],
  "decision": false,
  "example": "Keep case proof and owner"
}
```


Sources:

- context / user-brief: Design a complaint assistant for a telecom provider. Customers report network outages, poor speed and billing errors. The assistant should investigate using account, billing and service records, explain findings and resolve eligible service credits. Larger or unclear refunds need a human supervisor and may wait up to 48 hours. Keep customers informed, avoid duplicate refunds and use only the right customer's active service connection. Propose any missing policies as assumptions, not real company rules.

### W13 · Credit confirmed

{"state": "Persisted CaseState: caseId, tenant scope if authenticated, owner, stateVersion, enqueueAt UTC, noticeMask, retryCount, cancellation flag, eventKey lock, operationId and receipt. Predicate values are typed outputs of the C component in this node; retryCount:uint starts 0 and increments only on W10\u2192W8, cancelled:bool from authenticated case cancellation event; timers from durable UTC scheduler. Cancellation > decision > notice precedence. Durable caseId is allocated before W1; no financial effect. ", "transitions": [], "failureDisposition": "Persist owned pending case; no blind financial retry; recovery owner Billing Operations for money and Support Operations otherwise.", "timeout": "48 elapsed hours for W6; model 10s per attempt max2; reads 5s max2; C8 5s max1; reconciliation initial 120s window.", "retryPolicy": "Only model/read schema retries once; writer retry only W10 authoritative absent then W8 once. Notice sequence max2; scheduler never resets 48h clock.", "terminalDisposition": "Proven posted credit with postingId and caseId."}

Reasoning: Bound responsibility to a testable contract.

Data:

```json
{
  "componentId": "C10",
  "taskIds": [
    "T4"
  ],
  "next": [],
  "decision": false,
  "example": "Credit confirmed"
}
```


Sources:

- context / user-brief: Design a complaint assistant for a telecom provider. Customers report network outages, poor speed and billing errors. The assistant should investigate using account, billing and service records, explain findings and resolve eligible service credits. Larger or unclear refunds need a human supervisor and may wait up to 48 hours. Keep customers informed, avoid duplicate refunds and use only the right customer's active service connection. Propose any missing policies as assumptions, not real company rules.

## Required tests

For each ID below, load ../eval-set.json items[id].data.input, .expected and .passRule. These are the full fixture, expected result and exact assertions; no inherited test context is assumed.

- EV1: Eligible credit positive
- EV2: Supervisor larger-credit positive
- EV3: Wrong customer blocks reads
- EV4: Inactive service rejected
- EV5: Changed policy invalidates plan
- EV6: Approval covers whole plan
- EV7: Revoked authority prevents credit
- EV8: Two cases cannot duplicate one incident
- EV9: Timeout committed and duplicate callback
- EV10: Definitive absence permits one guarded retry
- EV11: Unknown commit stays frozen
- EV12: Injection cannot control money
- EV13: Success response without record is not completion
- EV14: Wait notices and overdue ownership
- EV16: Cancellation wins before post
- EV18: Remaining charge caps credit
- EV19: Evidence supports no service credit
- EV20: Denied larger credit
- EV21: Offline evidence and adapter suite
- EV22: Online safety and queue monitoring
- EV23: Release complete suite
## Acceptance criteria

- Implement C7, C8, C9, C10 exact typed contracts and their branch rules.
- Execute all selected goldens and EV23 before moving onward; synthetic specifications are not run evidence.
- Preserve H1-H4 live-launch blockers and all retained pending owners.
