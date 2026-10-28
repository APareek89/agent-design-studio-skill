# Decide and staff the queue

> NEEDS-WORK | DESIGN ONLY. independent-agent; round 1.

Depends on earlier milestones where their outputs are inputs below. Cross-milestone shared types are read by ID from ../design.json, not copied.

## Selected contracts

### C4 · Rule and action validation

P1 in H1 computes integer minor-unit credit: floor(chargeMinor × union outageMinutes / cycleMinutes), then compare raw calculated amount to the 50000 automatic cap. Above cap routes HUMAN. Otherwise use min(calculated,chargeMinor-alreadyCreditedMinor). Requires positive charge/cycle, nonnegative already credited, verified outage minutes 0..cycle length and valid policy. Zero amount is NO_CREDIT. Above automatic cap routes HUMAN before capping, never silently pays a partial amount. Supervisor exception command may specify positive integer amount up to remaining original charge; unsupported cash refunds receive owned manual disposition. Approval binds complete command bytes: tenant/customer/connection, originalChargeId, cycle, outage IDs, amountMinor,currency,reason,allocation,policyVersion,accountVersion,operationId,expiresAt. Any changed field needs new decision. Fresh auth/account/policy/ledger rechecks at writer, including expiry and revocation; missing support BLOCKED.

Reasoning: Keeps authority explicit and failures owned.

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
    "scope: fresh account binding",
    "evidence: C2 authoritative records",
    "decision: optional supervisor signed immutable command reference",
    "caseState: cancellation/operation/version"
  ],
  "outputs": [
    "route: AUTO|HUMAN|NO_CREDIT|CANCELLED|BLOCKED",
    "commandRef: immutable command record or null",
    "reason: exact policy/guard code"
  ],
  "whyCode": "Enforce repeatable scope, exact arithmetic, state and durable evidence without probabilistic authority.",
  "approvalRule": "No model authority. Credit requires fresh policy or exact supervisor approval; notices require current scoped case and verified destination."
}
```


Sources:

- context / user-brief: Keep customers informed, avoid duplicate refunds and use only the right customer's active service connection.

### C5 · Durable supervisor queue

Internal workflow store owns queue assignment and durable events across session expiry. Proposed owner Support supervisor; independent billing approver for exceptions above P1. ACK within 2 elapsed hours; reminder 24h, escalation 48h to duty manager with owned unresolved case. Server timestamps, deduplicated events, compare-and-swap caseVersion. Approval token is actor-signed, single-use, exact command, 15-minute validity; writer separately verifies authority. Cancel before submit suppresses action; cancellation after uncertain submit freezes conflicting commands until lookup. Missing evidence permits owned provisional investigation.

Reasoning: Keeps authority explicit and failures owned.

Data:

```json
{
  "group": "Code: human triggers",
  "taskIds": [
    "T3.2",
    "T4"
  ],
  "inputs": [
    "caseId: scoped durable ID",
    "commandRef: optional immutable proposal",
    "events: ACK|APPROVE|DENY|CANCEL|OVERDUE with eventId/version/actor/time"
  ],
  "outputs": [
    "queueStatus: WAIT|APPROVED|DENIED|CANCELLED|OVERDUE|MISSING_EVIDENCE",
    "decisionRef: immutable approved command or null",
    "noticeEventPersisted: boolean from durable outbox transaction",
    "noticeEnvelope: verified destinationRef, noticeKey and immutable statusRef with nextUpdateAt"
  ],
  "whyCode": "Enforce repeatable scope, exact arithmetic, state and durable evidence without probabilistic authority.",
  "approvalRule": "No model authority. Credit requires fresh policy or exact supervisor approval; notices require current scoped case and verified destination."
}
```


Sources:

- context / user-brief: Keep customers informed, avoid duplicate refunds and use only the right customer's active service connection.

## Workflow rules

### W4 · Choose safe resolution

{"state": "C4.route authoritative; mutually exclusive enum. C4 creates immutable command only from trusted policy/evidence. Unknown command state cannot enter fresh action.", "transitions": [{"to": "W9", "when": "route == AUTO", "mode": "exclusive; first matching predicate wins"}, {"to": "W6", "when": "route == HUMAN or route == BLOCKED", "mode": "exclusive; first matching predicate wins"}, {"to": "W12", "when": "route == NO_CREDIT or route == CANCELLED", "mode": "exclusive; first matching predicate wins"}], "failureDisposition": "Persist owned case; no unproved success or blind second action.", "timeout": "Node-specific deadlines in component; server UTC elapsed timers.", "retryPolicy": "Only bounded read retries; no write retry without final absence proof.", "terminalDisposition": ""}

Reasoning: Keeps authority explicit and failures owned.

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
    "W9",
    "W6",
    "W12"
  ],
  "decision": true,
  "example": "CASE1 follows only recorded component result; guard variables below are authoritative."
}
```


Sources:

- context / user-brief: Keep customers informed, avoid duplicate refunds and use only the right customer's active service connection.

### W5 · Schedule customer waiting notice

{"state": "C5 reduces NOTICE_DUE event with stable eventId; persist statusRef, verified destinationRef and noticeKey from scoped account and current case. It records nextUpdateAt from server clock. Schedule once; overdue/ack/reminder events never reset original queue clock. External delivery failure never cancels queue ownership.", "transitions": [{"to": "W7", "when": "noticeEventPersisted == true", "mode": "exclusive"}], "failureDisposition": "Durable outbox retries internal persistence once then leaves duty-manager incident and authenticated in-app status; no unowned wait.", "timeout": "Immediate internal transaction, 2 seconds; one persistence retry.", "retryPolicy": "Deduplicate internal event ID; no repeated notice for same event.", "terminalDisposition": ""}

Reasoning: Keeps authority explicit and failures owned.

Data:

```json
{
  "componentId": "C5",
  "taskIds": [
    "T4"
  ],
  "next": [
    "W7"
  ],
  "decision": false,
  "example": "At intake create one queued status notice event before external send."
}
```


Sources:

- context / user-brief: Keep customers informed, avoid duplicate refunds and use only the right customer's active service connection.

### W6 · Wait for supervisor

{"state": "event is C5 durable event reducer: CANCEL before submit, then valid APPROVE/DENY, then timers. WAIT remains parked, not a busy loop. Emit initial queued notice immediately; 2h unacknowledged escalation notice, 24h reminder and 48h overdue notice. Each notice event once. At 48h preserve HUMAN_OWNED and duty manager, never deny automatically. Missing evidence remains investigation-owned; decision must supply trusted command before APPROVE. Late approval is new event requiring W8 validation.", "transitions": [{"to": "W5", "when": "event == NOTICE_DUE", "mode": "exclusive; first matching predicate wins"}, {"to": "W8", "when": "event == APPROVE", "mode": "exclusive; first matching predicate wins"}, {"to": "W12", "when": "event == DENY or event == CANCEL", "mode": "exclusive; first matching predicate wins"}, {"to": "W12", "when": "event == OVERDUE", "mode": "exclusive; first matching predicate wins"}], "failureDisposition": "Persist owned case; no unproved success or blind second action.", "timeout": "Node-specific deadlines in component; server UTC elapsed timers.", "retryPolicy": "Only bounded read retries; no write retry without final absence proof.", "terminalDisposition": ""}

Reasoning: Keeps authority explicit and failures owned.

Data:

```json
{
  "componentId": "C5",
  "taskIds": [
    "T3.2"
  ],
  "next": [
    "W5",
    "W8",
    "W12"
  ],
  "decision": true,
  "example": "CASE1 follows only recorded component result; guard variables below are authoritative."
}
```


Sources:

- context / user-brief: Keep customers informed, avoid duplicate refunds and use only the right customer's active service connection.

### W8 · Validate supervisor decision

{"state": "C4.route recomputed after C5 approval: AUTO means exact signed command validated and current scope valid. Expired/revoked/changed approval is BLOCKED and human case remains owned. At most one failed approval correction; subsequent failure leaves duty manager disposition via overdue event. Authorized exception amount from signed immutable record, not model text.", "transitions": [{"to": "W9", "when": "route == AUTO", "mode": "exclusive; first matching predicate wins"}, {"to": "W12", "when": "route == NO_CREDIT or route == CANCELLED", "mode": "exclusive; first matching predicate wins"}, {"to": "W6", "when": "route == HUMAN or route == BLOCKED", "mode": "exclusive; first matching predicate wins"}], "failureDisposition": "Persist owned case; no unproved success or blind second action.", "timeout": "Node-specific deadlines in component; server UTC elapsed timers.", "retryPolicy": "Only bounded read retries; no write retry without final absence proof.", "terminalDisposition": ""}

Reasoning: Keeps authority explicit and failures owned.

Data:

```json
{
  "componentId": "C4",
  "taskIds": [
    "T3.2",
    "T3.1"
  ],
  "next": [
    "W9",
    "W12",
    "W6"
  ],
  "decision": true,
  "example": "CASE1 follows only recorded component result; guard variables below are authoritative."
}
```


Sources:

- context / user-brief: Keep customers informed, avoid duplicate refunds and use only the right customer's active service connection.

## Required tests

For each ID below, load ../eval-set.json items[id].data.input, .expected and .passRule. These are the full fixture, expected result and exact assertions; no inherited test context is assumed.

- EV1: Valid outage arithmetic and proof
- EV3: Policy changed after decision
- EV4: Two operations same outage serialize
- EV5: Conflicting outage cannot authorize text instruction
- EV8: 48-hour queue retains owner and visible status
- EV9: Missing rule blocks calculation
- EV12: Large calculated credit goes to human
- EV13: Valid supervisor-bound credit
- EV14: Revocation wins after approval
- EV17: Cancellation before submit suppresses credit
- EV19: Poor speed investigated but not auto-credited
- EV21: Stratified end-to-end evidence review
- EV22: Operational safety monitors
- EV23: Release suite and approval evidence
## Acceptance criteria

- Implement exact selected contracts and every linked assertion; no new authority.
- Verified external dependencies H1-H4,H6 remain launch gates.
