# Compute and approve exact plans

> PASS | DESIGN ONLY. self-review; round 2.

Depends on earlier milestones where their outputs are inputs below. Cross-milestone shared types are read by ID from ../design.json, not copied.

## Selected contracts

### C4 · Calculate and route

Integer arithmetic, UTC interval intersection, policy limits and account ledger determine amount. CreditPlan holds tenant/customer/connection/connectionVersion/authVersion, invoiceId/version, incidentId, eventKey, periodStart/end, outageSeconds, amountMinor, currency, taxTreatment, accountingCode, policyVersion, evidenceVersions, expiresAt, planVersion. eventKey derives from tenant/connection/invoice/incident/creditKind; DB uniqueness blocks cross-case semantic duplicates. Missing/conflicting facts route HUMAN; zero eligibility NO_CREDIT.

Reasoning: Bound responsibility to a testable contract.

Data:

```json
{
  "group": "Code: validation",
  "taskIds": [
    "T3.1",
    "T3.2",
    "T3.3"
  ],
  "inputs": [
    "scope: C1.scope, required",
    "evidence: C2.evidence, required",
    "policy: signed approved version P1, required"
  ],
  "outputs": [
    "plan: immutable CreditPlan or null",
    "route: enum AUTO|HUMAN|NO_CREDIT"
  ],
  "whyCode": "Integer arithmetic, UTC interval intersection, policy limits and account ledger determine amount. CreditPlan holds tenant/customer/connection/connectionVersion/authVersion, invoiceId/version, incidentId, eventKey, periodStart/end, outageSeconds, amountMinor, currency, taxTreatment, accountingCode, policyVersion, evidenceVersions, expiresAt, planVersion. eventKey derives from tenant/connection/invoice/incident/creditKind; DB uniqueness blocks cross-case semantic duplicates. Missing/conflicting facts route HUMAN; zero eligibility NO_CREDIT.",
  "approvalRule": "AUTO only verified outage under cap and remaining entitlement; never model-proposed money."
}
```


Sources:

- context / user-brief: Design a complaint assistant for a telecom provider. Customers report network outages, poor speed and billing errors. The assistant should investigate using account, billing and service records, explain findings and resolve eligible service credits. Larger or unclear refunds need a human supervisor and may wait up to 48 hours. Keep customers informed, avoid duplicate refunds and use only the right customer's active service connection. Propose any missing policies as assumptions, not real company rules.

### C5 · Wait for supervisor decision

Proposed queue complaint-supervisor; Support Operations owns; acknowledgement within 1h, duty-manager escalation if absent. Decision by elapsed 48h UTC from enqueue. Approval event covers immutable full plan; supervisor must resolve missing evidence in verified systems before a new plan exists. No arbitrary amount in an approval callback. Deduplicate eventId; order by queueVersion; expired/revoked/superseded events ignored.

Reasoning: Bound responsibility to a testable contract.

Data:

```json
{
  "group": "Code: human triggers",
  "taskIds": [
    "T3.2"
  ],
  "inputs": [
    "caseId: durable workflow UUID, required",
    "plan: C4.plan or null, required",
    "event: authenticated queue event or clock tick, required"
  ],
  "outputs": [
    "decision: enum PENDING|APPROVED|DENIED|CANCELLED|OVERDUE",
    "approval: signed immutable planId/planVersion plus all plan fields, approver role and expiry; required iff APPROVED",
    "noticeDue: enum ENTRY|H24|NONE"
  ],
  "whyCode": "Proposed queue complaint-supervisor; Support Operations owns; acknowledgement within 1h, duty-manager escalation if absent. Decision by elapsed 48h UTC from enqueue. Approval event covers immutable full plan; supervisor must resolve missing evidence in verified systems before a new plan exists. No arbitrary amount in an approval callback. Deduplicate eventId; order by queueVersion; expired/revoked/superseded events ignored.",
  "approvalRule": "Authorized supervisor, distinct from customer; cancellation takes precedence before posting. After posting begins cancellation freezes new commands and requests reconciliation, not a reversal."
}
```


Sources:

- context / user-brief: Design a complaint assistant for a telecom provider. Customers report network outages, poor speed and billing errors. The assistant should investigate using account, billing and service records, explain findings and resolve eligible service credits. Larger or unclear refunds need a human supervisor and may wait up to 48 hours. Keep customers informed, avoid duplicate refunds and use only the right customer's active service connection. Propose any missing policies as assumptions, not real company rules.

### C6 · Publish portal progress

Materialize notice in the same internal workflow transaction; authenticated case-status GET returns it. No SMS/email connector. ENTRY and H24 notices once each, H48 overdue in final pending view. Portal failure retains notice and duty manager owns recovery; never loses timer or decision.

Reasoning: Bound responsibility to a testable contract.

Data:

```json
{
  "group": "Code: human triggers",
  "taskIds": [
    "T3.2",
    "T4"
  ],
  "inputs": [
    "caseId: durable workflow UUID, required",
    "state: signed durable workflow state and notice sequence, required"
  ],
  "outputs": [
    "notice: authenticated portal view with caseId, owner, elapsed deadline, status, next step",
    "status: enum AVAILABLE|PORTAL_UNAVAILABLE"
  ],
  "whyCode": "Materialize notice in the same internal workflow transaction; authenticated case-status GET returns it. No SMS/email connector. ENTRY and H24 notices once each, H48 overdue in final pending view. Portal failure retains notice and duty manager owns recovery; never loses timer or decision.",
  "approvalRule": "Only authenticated customer can view their case; portal updates do not authorize credit."
}
```


Sources:

- context / user-brief: Design a complaint assistant for a telecom provider. Customers report network outages, poor speed and billing errors. The assistant should investigate using account, billing and service records, explain findings and resolve eligible service credits. Larger or unclear refunds need a human supervisor and may wait up to 48 hours. Keep customers informed, avoid duplicate refunds and use only the right customer's active service connection. Propose any missing policies as assumptions, not real company rules.

## Workflow rules

### W4 · Choose the policy route

{"state": "Persisted CaseState: caseId, tenant scope if authenticated, owner, stateVersion, enqueueAt UTC, noticeMask, retryCount, cancellation flag, eventKey lock, operationId and receipt. Predicate values are typed outputs of the C component in this node; retryCount:uint starts 0 and increments only on W10\u2192W8, cancelled:bool from authenticated case cancellation event; timers from durable UTC scheduler. Cancellation > decision > notice precedence. Durable caseId is allocated before W1; no financial effect. ", "transitions": [{"to": "W8", "when": "C4.route == AUTO", "mode": "exclusive"}, {"to": "W6", "when": "C4.route == HUMAN", "mode": "exclusive"}, {"to": "W12", "when": "C4.route == NO_CREDIT", "mode": "exclusive"}], "failureDisposition": "Persist owned pending case; no blind financial retry; recovery owner Billing Operations for money and Support Operations otherwise.", "timeout": "48 elapsed hours for W6; model 10s per attempt max2; reads 5s max2; C8 5s max1; reconciliation initial 120s window.", "retryPolicy": "Only model/read schema retries once; writer retry only W10 authoritative absent then W8 once. Notice sequence max2; scheduler never resets 48h clock.", "terminalDisposition": ""}

Reasoning: Bound responsibility to a testable contract.

Data:

```json
{
  "componentId": "C4",
  "taskIds": [
    "T3.1",
    "T3.2",
    "T3.3"
  ],
  "next": [
    "W8",
    "W6",
    "W12"
  ],
  "decision": true,
  "example": "Choose the policy route"
}
```


Sources:

- context / user-brief: Design a complaint assistant for a telecom provider. Customers report network outages, poor speed and billing errors. The assistant should investigate using account, billing and service records, explain findings and resolve eligible service credits. Larger or unclear refunds need a human supervisor and may wait up to 48 hours. Keep customers informed, avoid duplicate refunds and use only the right customer's active service connection. Propose any missing policies as assumptions, not real company rules.

### W6 · Wait up to 48 hours

{"state": "Persisted CaseState: caseId, tenant scope if authenticated, owner, stateVersion, enqueueAt UTC, noticeMask, retryCount, cancellation flag, eventKey lock, operationId and receipt. Predicate values are typed outputs of the C component in this node; retryCount:uint starts 0 and increments only on W10\u2192W8, cancelled:bool from authenticated case cancellation event; timers from durable UTC scheduler. Cancellation > decision > notice precedence. Durable caseId is allocated before W1; no financial effect. While PENDING with noticeDue NONE, scheduler waits without an active self-edge; ENTRY/H24 fire once; at enqueueAt+48h OVERDUE wins. Acknowledge deadline is enqueueAt+1h. After 48h retain supervisor ownership; late approval cannot auto-post.", "transitions": [{"to": "W7", "when": "C5.decision == PENDING and C5.noticeDue in {ENTRY,H24}", "mode": "exclusive"}, {"to": "W8", "when": "C5.decision == APPROVED", "mode": "exclusive"}, {"to": "W12", "when": "C5.decision in {DENIED,CANCELLED}", "mode": "exclusive"}, {"to": "W12", "when": "C5.decision == OVERDUE", "mode": "exclusive"}], "failureDisposition": "Persist owned pending case; no blind financial retry; recovery owner Billing Operations for money and Support Operations otherwise.", "timeout": "48 elapsed hours for W6; model 10s per attempt max2; reads 5s max2; C8 5s max1; reconciliation initial 120s window.", "retryPolicy": "Only model/read schema retries once; writer retry only W10 authoritative absent then W8 once. Notice sequence max2; scheduler never resets 48h clock.", "terminalDisposition": ""}

Reasoning: Bound responsibility to a testable contract.

Data:

```json
{
  "componentId": "C5",
  "taskIds": [
    "T3.2"
  ],
  "next": [
    "W7",
    "W8",
    "W12"
  ],
  "decision": true,
  "example": "Wait up to 48 hours"
}
```


Sources:

- context / user-brief: Design a complaint assistant for a telecom provider. Customers report network outages, poor speed and billing errors. The assistant should investigate using account, billing and service records, explain findings and resolve eligible service credits. Larger or unclear refunds need a human supervisor and may wait up to 48 hours. Keep customers informed, avoid duplicate refunds and use only the right customer's active service connection. Propose any missing policies as assumptions, not real company rules.

### W7 · Show wait progress

{"state": "Persisted CaseState: caseId, tenant scope if authenticated, owner, stateVersion, enqueueAt UTC, noticeMask, retryCount, cancellation flag, eventKey lock, operationId and receipt. Predicate values are typed outputs of the C component in this node; retryCount:uint starts 0 and increments only on W10\u2192W8, cancelled:bool from authenticated case cancellation event; timers from durable UTC scheduler. Cancellation > decision > notice precedence. Durable caseId is allocated before W1; no financial effect. ", "transitions": [{"to": "W6", "when": "C6.status in {AVAILABLE,PORTAL_UNAVAILABLE} and notice sequence persisted", "mode": "exclusive"}], "failureDisposition": "Persist owned pending case; no blind financial retry; recovery owner Billing Operations for money and Support Operations otherwise.", "timeout": "48 elapsed hours for W6; model 10s per attempt max2; reads 5s max2; C8 5s max1; reconciliation initial 120s window.", "retryPolicy": "Only model/read schema retries once; writer retry only W10 authoritative absent then W8 once. Notice sequence max2; scheduler never resets 48h clock.", "terminalDisposition": ""}

Reasoning: Bound responsibility to a testable contract.

Data:

```json
{
  "componentId": "C6",
  "taskIds": [
    "T3.2"
  ],
  "next": [
    "W6"
  ],
  "decision": false,
  "example": "Show wait progress"
}
```


Sources:

- context / user-brief: Design a complaint assistant for a telecom provider. Customers report network outages, poor speed and billing errors. The assistant should investigate using account, billing and service records, explain findings and resolve eligible service credits. Larger or unclear refunds need a human supervisor and may wait up to 48 hours. Keep customers informed, avoid duplicate refunds and use only the right customer's active service connection. Propose any missing policies as assumptions, not real company rules.

### W14 · Case outcome or owned pending

{"state": "Persisted CaseState: caseId, tenant scope if authenticated, owner, stateVersion, enqueueAt UTC, noticeMask, retryCount, cancellation flag, eventKey lock, operationId and receipt. Predicate values are typed outputs of the C component in this node; retryCount:uint starts 0 and increments only on W10\u2192W8, cancelled:bool from authenticated case cancellation event; timers from durable UTC scheduler. Cancellation > decision > notice precedence. Durable caseId is allocated before W1; no financial effect. View includes caseId, owner and truthful next action. OVERDUE shows missed deadline immediately. PENDING_RECONCILIATION is not closed and retains frozen event key and read-only reconciliation owner. Portal resumes from persisted case after reconnect.", "transitions": [], "failureDisposition": "Persist owned pending case; no blind financial retry; recovery owner Billing Operations for money and Support Operations otherwise.", "timeout": "48 elapsed hours for W6; model 10s per attempt max2; reads 5s max2; C8 5s max1; reconciliation initial 120s window.", "retryPolicy": "Only model/read schema retries once; writer retry only W10 authoritative absent then W8 once. Notice sequence max2; scheduler never resets 48h clock.", "terminalDisposition": "Durable non-credit outcome or owned pending case with reason; unresolved money never called complete."}

Reasoning: Bound responsibility to a testable contract.

Data:

```json
{
  "componentId": "C6",
  "taskIds": [
    "T4"
  ],
  "next": [],
  "decision": false,
  "example": "Case outcome or owned pending"
}
```


Sources:

- context / user-brief: Design a complaint assistant for a telecom provider. Customers report network outages, poor speed and billing errors. The assistant should investigate using account, billing and service records, explain findings and resolve eligible service credits. Larger or unclear refunds need a human supervisor and may wait up to 48 hours. Keep customers informed, avoid duplicate refunds and use only the right customer's active service connection. Propose any missing policies as assumptions, not real company rules.

## Required tests

For each ID below, load ../eval-set.json items[id].data.input, .expected and .passRule. These are the full fixture, expected result and exact assertions; no inherited test context is assumed.

- EV1: Eligible credit positive
- EV2: Supervisor larger-credit positive
- EV5: Changed policy invalidates plan
- EV6: Approval covers whole plan
- EV8: Two cases cannot duplicate one incident
- EV12: Injection cannot control money
- EV14: Wait notices and overdue ownership
- EV15: Portal outage retains customer notice
- EV16: Cancellation wins before post
- EV17: Conflicting billing or speed evidence abstains
- EV18: Remaining charge caps credit
- EV19: Evidence supports no service credit
- EV20: Denied larger credit
- EV21: Offline evidence and adapter suite
- EV22: Online safety and queue monitoring
- EV23: Release complete suite
## Acceptance criteria

- Implement C4, C5, C6 exact typed contracts and their branch rules.
- Execute all selected goldens and EV23 before moving onward; synthetic specifications are not run evidence.
- Preserve H1-H4 live-launch blockers and all retained pending owners.
