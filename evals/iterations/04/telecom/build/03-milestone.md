# Credit, notify and reconcile

> NEEDS-WORK | DESIGN ONLY. independent-agent; round 1.

Depends on earlier milestones where their outputs are inputs below. Cross-milestone shared types are read by ID from ../design.json, not copied.

## Selected contracts

### C6 · Customer status delivery

Send only minimized status; template says pending, approved-not-posted, credited with proof, overdue or unresolved. Never says refunded on approval alone. 5s timeout; no direct retry after uncertain send. Query by noticeKey; once confirmed absent retry once under same key. Failed channel remains visible in-app and duty manager owns delivery issue. No private account data on unauthenticated channel.

Reasoning: Keeps authority explicit and failures owned.

Data:

```json
{
  "group": "Code: tools",
  "taskIds": [
    "T4"
  ],
  "inputs": [
    "caseId: trusted durable case ID",
    "destinationRef: verified account notification channel",
    "noticeKey: caseId/eventId/channel stable key",
    "statusRef: immutable scoped status text and nextUpdateAt"
  ],
  "outputs": [
    "noticeResult: SENT|FAILED|TIMEOUT|UNKNOWN",
    "noticeId: delivery record ID or null"
  ],
  "whyCode": "Enforce repeatable scope, exact arithmetic, state and durable evidence without probabilistic authority.",
  "approvalRule": "No model authority. Credit requires fresh policy or exact supervisor approval; notices require current scoped case and verified destination."
}
```


Sources:

- context / user-brief: Keep customers informed, avoid duplicate refunds and use only the right customer's active service connection.

### C7 · Service-ledger credit writer

POST credit to exact original charge. Fetch immutable command and verify bytes/approval binding; currency INR, amountMinor integer >0, remaining charge bound, active service, same tenant/customer, current versions, actor authority, expiry and cancellation. Atomic unique semantic key tenant/customer/connection/incident-set/cycle/credit-type blocks cross-case duplicate; operationId deduplicates retries. Concurrent overlapping-interval complaints lock billing-cycle adjustment budget and correlate semantic matches with human before any second operation. POSTED requires durable postingId, amount/currency/originalChargeId and versions matching command. REJECTED has reason and no effect; 5s timeout/unknown require lookup. No generic retry.

Reasoning: Keeps authority explicit and failures owned.

Data:

```json
{
  "group": "Code: tools",
  "taskIds": [
    "T3.1"
  ],
  "inputs": [
    "commandRef: trusted immutable validated command ID",
    "authorityRef: trusted fresh policy authorization or signed supervisor decision",
    "operationId: trusted unique business operation ID"
  ],
  "outputs": [
    "writeResult: POSTED|REJECTED|TIMEOUT|UNKNOWN",
    "postingId: immutable ledger ID or null",
    "verifiedRecordId:string! on a proven record outcome; explicit projection of existing case/posting record ID, absent on failed or uncertain outcomes"
  ],
  "whyCode": "Enforce repeatable scope, exact arithmetic, state and durable evidence without probabilistic authority.",
  "approvalRule": "No model authority. Credit requires fresh policy or exact supervisor approval; notices require current scoped case and verified destination."
}
```


Sources:

- context / user-brief: Keep customers informed, avoid duplicate refunds and use only the right customer's active service connection.

### C8 · Read-only reconciliation

Lookup uses service credential scoped to original tenant and operation, survives user logout. Deduplicate callbacks by eventId+operationId and reject mismatched proof. Poll at 1m,5m,30m,2h; then unresolved with duty manager and no automatic future write. ABSENT_FINAL must prove operation cannot later commit before one resubmission under original key and fresh checks. Session expiry does not revoke lookup; revocation blocks any new action. Cancellation after COMMITTED records posted/cancellation requested; reversal requires separately authorized new case outside first-release scope.

Reasoning: Keeps authority explicit and failures owned.

Data:

```json
{
  "group": "Code: tools",
  "taskIds": [
    "T3.1",
    "T4"
  ],
  "inputs": [
    "operationRef: credit operationId or noticeKey and original scope",
    "attempt: durable lookup counter"
  ],
  "outputs": [
    "lookup: COMMITTED|ABSENT_FINAL|PENDING|UNAVAILABLE|CONFLICT",
    "proof: authoritative matching posting/delivery record or null",
    "verifiedRecordId:string! on a proven record outcome; explicit projection of existing case/posting record ID, absent on failed or uncertain outcomes"
  ],
  "whyCode": "Enforce repeatable scope, exact arithmetic, state and durable evidence without probabilistic authority.",
  "approvalRule": "No model authority. Credit requires fresh policy or exact supervisor approval; notices require current scoped case and verified destination."
}
```


Sources:

- context / user-brief: Keep customers informed, avoid duplicate refunds and use only the right customer's active service connection.

## Workflow rules

### W7 · Send waiting update

{"state": "C6.noticeResult; workflow stores resume=WAIT and notice event key before send. FAILED records delivery issue, in-app status and duty manager. Notice send does not reset wait deadline.", "transitions": [{"to": "W6", "when": "noticeResult == SENT or noticeResult == FAILED", "mode": "exclusive; first matching predicate wins"}, {"to": "W10", "when": "noticeResult == TIMEOUT", "mode": "exclusive; first matching predicate wins"}, {"to": "W10", "when": "noticeResult == UNKNOWN", "mode": "exclusive; first matching predicate wins"}], "failureDisposition": "Persist owned case; no unproved success or blind second action.", "timeout": "Node-specific deadlines in component; server UTC elapsed timers.", "retryPolicy": "Only bounded read retries; no write retry without final absence proof.", "terminalDisposition": ""}

Reasoning: Keeps authority explicit and failures owned.

Data:

```json
{
  "componentId": "C6",
  "taskIds": [
    "T4"
  ],
  "next": [
    "W6",
    "W10"
  ],
  "decision": true,
  "example": "CASE1 follows only recorded component result; guard variables below are authoritative."
}
```


Sources:

- context / user-brief: Keep customers informed, avoid duplicate refunds and use only the right customer's active service connection.

### W9 · Post credit

{"state": "C7.writeResult authoritative. Persist operation and resume=CREDIT before submission. POSTED includes matching durable postingId. REJECTED clears only conclusively absent operation, preserves human reason. Unknown locks changed intent.", "transitions": [{"to": "W12", "when": "writeResult == POSTED", "mode": "exclusive; first matching predicate wins"}, {"to": "W6", "when": "writeResult == REJECTED", "mode": "exclusive; first matching predicate wins"}, {"to": "W10", "when": "writeResult == TIMEOUT", "mode": "exclusive; first matching predicate wins"}, {"to": "W10", "when": "writeResult == UNKNOWN", "mode": "exclusive; first matching predicate wins"}], "failureDisposition": "Persist owned case; no unproved success or blind second action.", "timeout": "Node-specific deadlines in component; server UTC elapsed timers.", "retryPolicy": "Only bounded read retries; no write retry without final absence proof.", "terminalDisposition": ""}

Reasoning: Keeps authority explicit and failures owned.

Data:

```json
{
  "componentId": "C7",
  "taskIds": [
    "T3.1"
  ],
  "next": [
    "W12",
    "W6",
    "W10"
  ],
  "decision": true,
  "example": "CASE1 follows only recorded component result; guard variables below are authoritative."
}
```


Sources:

- context / user-brief: Keep customers informed, avoid duplicate refunds and use only the right customer's active service connection.

### W10 · Check uncertain action

{"state": "lookup:C8 output after bounded polling. resume:enum CREDIT|WAIT|FINAL, retryCount:int 0..1, cancelled:bool, authorityFresh:bool are persisted server state and fresh C4 checks. noRetryAllowed is complement of three permitted ABSENT_FINAL retry predicates. Increment retryCount before resubmission, same original key, never while unknown. PENDING/UNAVAILABLE/CONFLICT at poll bound record UNKNOWN_OWNED duty manager and operation lock. On COMMITTED credit readback mark CREDITED; on committed final notice preserve prior disposition. Cancellation during unknown prevents resubmit but not lookup. Duplicate callbacks only update once.", "transitions": [{"to": "W9", "when": "lookup == ABSENT_FINAL and resume == CREDIT and retryCount == 0 and not cancelled and authorityFresh", "mode": "exclusive; first matching predicate wins"}, {"to": "W7", "when": "lookup == ABSENT_FINAL and resume == WAIT and retryCount == 0", "mode": "exclusive; first matching predicate wins"}, {"to": "W12", "when": "lookup == ABSENT_FINAL and resume == FINAL and retryCount == 0", "mode": "exclusive; first matching predicate wins"}, {"to": "W6", "when": "lookup == COMMITTED and resume == WAIT", "mode": "exclusive; first matching predicate wins"}, {"to": "W14", "when": "lookup == COMMITTED and resume != WAIT", "mode": "exclusive; first matching predicate wins"}, {"to": "W14", "when": "lookup == ABSENT_FINAL and noRetryAllowed", "mode": "exclusive; first matching predicate wins"}, {"to": "W14", "when": "lookup == PENDING or lookup == UNAVAILABLE or lookup == CONFLICT", "mode": "exclusive; first matching predicate wins"}], "failureDisposition": "Persist owned case; no unproved success or blind second action.", "timeout": "Node-specific deadlines in component; server UTC elapsed timers.", "retryPolicy": "Only bounded read retries; no write retry without final absence proof.", "terminalDisposition": ""}

Reasoning: Keeps authority explicit and failures owned.

Data:

```json
{
  "componentId": "C8",
  "taskIds": [
    "T3.1",
    "T4"
  ],
  "next": [
    "W9",
    "W7",
    "W12",
    "W6",
    "W14"
  ],
  "decision": true,
  "example": "CASE1 follows only recorded component result; guard variables below are authoritative."
}
```


Sources:

- context / user-brief: Keep customers informed, avoid duplicate refunds and use only the right customer's active service connection.

### W12 · Send final or overdue update

{"state": "C6.noticeResult with resume=FINAL. C9 fixed status template uses POSTED proof for CREDITED; supervisor approval alone says pending. NO_CREDIT/CANCELLED/HUMAN_OWNED have durable disposition IDs. Failed notice cannot erase posted credit.", "transitions": [{"to": "W14", "when": "noticeResult == SENT or noticeResult == FAILED", "mode": "exclusive; first matching predicate wins"}, {"to": "W10", "when": "noticeResult == TIMEOUT", "mode": "exclusive; first matching predicate wins"}, {"to": "W10", "when": "noticeResult == UNKNOWN", "mode": "exclusive; first matching predicate wins"}], "failureDisposition": "Persist owned case; no unproved success or blind second action.", "timeout": "Node-specific deadlines in component; server UTC elapsed timers.", "retryPolicy": "Only bounded read retries; no write retry without final absence proof.", "terminalDisposition": ""}

Reasoning: Keeps authority explicit and failures owned.

Data:

```json
{
  "componentId": "C6",
  "taskIds": [
    "T4"
  ],
  "next": [
    "W14",
    "W10"
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
- EV2: Cross-customer service rejected
- EV3: Policy changed after decision
- EV4: Two operations same outage serialize
- EV5: Conflicting outage cannot authorize text instruction
- EV6: Unknown commit after logout and cancellation
- EV7: No proof means no success
- EV8: 48-hour queue retains owner and visible status
- EV9: Missing rule blocks calculation
- EV10: Wrong notification destination rejected
- EV11: Verified waiting notice delivered
- EV12: Large calculated credit goes to human
- EV13: Valid supervisor-bound credit
- EV14: Revocation wins after approval
- EV15: Notice timeout readback prevents duplicate send
- EV16: Unknown stays locked at polling bound
- EV17: Cancellation before submit suppresses credit
- EV18: Inactive connection cannot receive credit
- EV19: Poor speed investigated but not auto-credited
- EV20: Invented citation triggers template fallback
- EV21: Stratified end-to-end evidence review
- EV22: Operational safety monitors
- EV23: Release suite and approval evidence
## Acceptance criteria

- Implement exact selected contracts and every linked assertion; no new authority.
- Verified external dependencies H1-H4,H6 remain launch gates.
