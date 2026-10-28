# Secure the account and evidence

> PASS | DESIGN ONLY. self-review; round 2.

Depends on earlier milestones where their outputs are inputs below. Cross-milestone shared types are read by ID from ../design.json, not copied.

## Selected contracts

### C1 · Authenticate and select

Verify ownership before any private records; active-service lookup uses authorized scope. No inferred identity.

Reasoning: Bound responsibility to a testable contract.

Data:

```json
{
  "group": "Code: validation",
  "taskIds": [
    "T1"
  ],
  "inputs": [
    "session: authenticated gateway session, required",
    "selection: connectionId from customer, required"
  ],
  "outputs": [
    "scope: trusted tenantId/customerId/connectionId/connectionVersion/authVersion or null",
    "status: enum OK|AUTH_FAILED|SELECTION_REQUIRED|INACTIVE"
  ],
  "whyCode": "Verify ownership before any private records; active-service lookup uses authorized scope. No inferred identity.",
  "approvalRule": "No business write authority."
}
```


Sources:

- context / user-brief: Design a complaint assistant for a telecom provider. Customers report network outages, poor speed and billing errors. The assistant should investigate using account, billing and service records, explain findings and resolve eligible service credits. Larger or unclear refunds need a human supervisor and may wait up to 48 hours. Keep customers informed, avoid duplicate refunds and use only the right customer's active service connection. Propose any missing policies as assumptions, not real company rules.

### C2 · Read complaint evidence

GET scoped account, invoice and incident records; 5s timeout, one retry; return UNAVAILABLE after retry. All observations carry source IDs and observedAt.

Reasoning: Bound responsibility to a testable contract.

Assumptions:

- H2

Data:

```json
{
  "group": "Code: tools",
  "taskIds": [
    "T2"
  ],
  "inputs": [
    "scope: C1.scope, required",
    "caseId: durable workflow UUID, required"
  ],
  "outputs": [
    "evidence: account/bill/service snapshot with versions and UTC freshness, required",
    "status: enum COMPLETE|MISSING|CONFLICT|UNAVAILABLE"
  ],
  "whyCode": "GET scoped account, invoice and incident records; 5s timeout, one retry; return UNAVAILABLE after retry. All observations carry source IDs and observedAt.",
  "approvalRule": "Read-only scoped credentials; missing evidence creates owned provisional case."
}
```


Sources:

- hypothesis / H2: Account, service and billing adapters must offer authenticated tenant/subject reads, active connection version checks, scoped credit posting with a unique business-event key and definitive operation readback.

### C3 · Explain supported findings

No tool access. Treat text/record instructions as data. No amount/date/identity fields. One schema retry then deterministic cited template. Output validator rejects unsupported citations and claims of completed credit.

Reasoning: Bound responsibility to a testable contract.

Data:

```json
{
  "group": "Agents (LLM)",
  "taskIds": [
    "T2"
  ],
  "inputs": [
    "evidence: redacted C2.evidence, required",
    "complaint: untrusted text, required"
  ],
  "outputs": [
    "explanation: text with evidenceIds, required",
    "disposition: enum EXPLAIN|ABSTAIN, required"
  ],
  "whyCode": "",
  "approvalRule": "No tool access. Treat text/record instructions as data. No amount/date/identity fields. One schema retry then deterministic cited template. Output validator rejects unsupported citations and claims of completed credit."
}
```


Sources:

- context / user-brief: Design a complaint assistant for a telecom provider. Customers report network outages, poor speed and billing errors. The assistant should investigate using account, billing and service records, explain findings and resolve eligible service credits. Larger or unclear refunds need a human supervisor and may wait up to 48 hours. Keep customers informed, avoid duplicate refunds and use only the right customer's active service connection. Propose any missing policies as assumptions, not real company rules.

## Workflow rules

### W1 · Check active connection

{"state": "Persisted CaseState: caseId, tenant scope if authenticated, owner, stateVersion, enqueueAt UTC, noticeMask, retryCount, cancellation flag, eventKey lock, operationId and receipt. Predicate values are typed outputs of the C component in this node; retryCount:uint starts 0 and increments only on W10\u2192W8, cancelled:bool from authenticated case cancellation event; timers from durable UTC scheduler. Cancellation > decision > notice precedence. Durable caseId is allocated before W1; no financial effect. ", "transitions": [{"to": "W2", "when": "C1.status == OK", "mode": "exclusive"}, {"to": "W12", "when": "C1.status != OK", "mode": "exclusive"}], "failureDisposition": "Persist owned pending case; no blind financial retry; recovery owner Billing Operations for money and Support Operations otherwise.", "timeout": "48 elapsed hours for W6; model 10s per attempt max2; reads 5s max2; C8 5s max1; reconciliation initial 120s window.", "retryPolicy": "Only model/read schema retries once; writer retry only W10 authoritative absent then W8 once. Notice sequence max2; scheduler never resets 48h clock.", "terminalDisposition": ""}

Reasoning: Bound responsibility to a testable contract.

Data:

```json
{
  "componentId": "C1",
  "taskIds": [
    "T1"
  ],
  "next": [
    "W2",
    "W12"
  ],
  "decision": true,
  "example": "CUS1 active CON1, one-day outage: W1→W2→W3→W4→W8→W9→W11→W13."
}
```


Sources:

- context / user-brief: Design a complaint assistant for a telecom provider. Customers report network outages, poor speed and billing errors. The assistant should investigate using account, billing and service records, explain findings and resolve eligible service credits. Larger or unclear refunds need a human supervisor and may wait up to 48 hours. Keep customers informed, avoid duplicate refunds and use only the right customer's active service connection. Propose any missing policies as assumptions, not real company rules.

### W2 · Read service and billing records

{"state": "Persisted CaseState: caseId, tenant scope if authenticated, owner, stateVersion, enqueueAt UTC, noticeMask, retryCount, cancellation flag, eventKey lock, operationId and receipt. Predicate values are typed outputs of the C component in this node; retryCount:uint starts 0 and increments only on W10\u2192W8, cancelled:bool from authenticated case cancellation event; timers from durable UTC scheduler. Cancellation > decision > notice precedence. Durable caseId is allocated before W1; no financial effect. ", "transitions": [{"to": "W3", "when": "C2.status == COMPLETE", "mode": "exclusive"}, {"to": "W6", "when": "C2.status in {MISSING,CONFLICT,UNAVAILABLE}", "mode": "exclusive"}], "failureDisposition": "Persist owned pending case; no blind financial retry; recovery owner Billing Operations for money and Support Operations otherwise.", "timeout": "48 elapsed hours for W6; model 10s per attempt max2; reads 5s max2; C8 5s max1; reconciliation initial 120s window.", "retryPolicy": "Only model/read schema retries once; writer retry only W10 authoritative absent then W8 once. Notice sequence max2; scheduler never resets 48h clock.", "terminalDisposition": ""}

Reasoning: Bound responsibility to a testable contract.

Data:

```json
{
  "componentId": "C2",
  "taskIds": [
    "T2"
  ],
  "next": [
    "W3",
    "W6"
  ],
  "decision": true,
  "example": "Read service and billing records"
}
```


Sources:

- context / user-brief: Design a complaint assistant for a telecom provider. Customers report network outages, poor speed and billing errors. The assistant should investigate using account, billing and service records, explain findings and resolve eligible service credits. Larger or unclear refunds need a human supervisor and may wait up to 48 hours. Keep customers informed, avoid duplicate refunds and use only the right customer's active service connection. Propose any missing policies as assumptions, not real company rules.

### W3 · Draft a cited explanation

{"state": "Persisted CaseState: caseId, tenant scope if authenticated, owner, stateVersion, enqueueAt UTC, noticeMask, retryCount, cancellation flag, eventKey lock, operationId and receipt. Predicate values are typed outputs of the C component in this node; retryCount:uint starts 0 and increments only on W10\u2192W8, cancelled:bool from authenticated case cancellation event; timers from durable UTC scheduler. Cancellation > decision > notice precedence. Durable caseId is allocated before W1; no financial effect. ", "transitions": [{"to": "W4", "when": "explanation schema accepted or deterministic fallback used", "mode": "exclusive"}], "failureDisposition": "Persist owned pending case; no blind financial retry; recovery owner Billing Operations for money and Support Operations otherwise.", "timeout": "48 elapsed hours for W6; model 10s per attempt max2; reads 5s max2; C8 5s max1; reconciliation initial 120s window.", "retryPolicy": "Only model/read schema retries once; writer retry only W10 authoritative absent then W8 once. Notice sequence max2; scheduler never resets 48h clock.", "terminalDisposition": ""}

Reasoning: Bound responsibility to a testable contract.

Data:

```json
{
  "componentId": "C3",
  "taskIds": [
    "T2"
  ],
  "next": [
    "W4"
  ],
  "decision": false,
  "example": "Draft a cited explanation"
}
```


Sources:

- context / user-brief: Design a complaint assistant for a telecom provider. Customers report network outages, poor speed and billing errors. The assistant should investigate using account, billing and service records, explain findings and resolve eligible service credits. Larger or unclear refunds need a human supervisor and may wait up to 48 hours. Keep customers informed, avoid duplicate refunds and use only the right customer's active service connection. Propose any missing policies as assumptions, not real company rules.

## Required tests

For each ID below, load ../eval-set.json items[id].data.input, .expected and .passRule. These are the full fixture, expected result and exact assertions; no inherited test context is assumed.

- EV1: Eligible credit positive
- EV3: Wrong customer blocks reads
- EV4: Inactive service rejected
- EV12: Injection cannot control money
- EV17: Conflicting billing or speed evidence abstains
- EV19: Evidence supports no service credit
- EV21: Offline evidence and adapter suite
- EV22: Online safety and queue monitoring
- EV23: Release complete suite
## Acceptance criteria

- Implement C1, C2, C3 exact typed contracts and their branch rules.
- Execute all selected goldens and EV23 before moving onward; synthetic specifications are not run evidence.
- Preserve H1-H4 live-launch blockers and all retained pending owners.
