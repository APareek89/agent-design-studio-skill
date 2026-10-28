# Bind and investigate

> PASS | DESIGN ONLY. self-review; round 3.

Depends on earlier milestones where their outputs are inputs below. Cross-milestone shared types are read by ID from ../design.json, not copied.

## Selected contracts

### C1 · Identity and scoped intake

Bind IDs from gateway and account registry, never from text. Refuse any mismatched/inactive selection before private reads. Case persisted transactionally with reason and owner; provisional cases contain no private billing data. GET account timeout 5s, one read retry, then NEED_INFO.

Reasoning: Keeps authority explicit and failures owned.

Data:

```json
{
  "group": "Code: validation",
  "taskIds": [
    "T1"
  ],
  "inputs": [
    "session: authenticated gateway token or absent",
    "selection: connection reference or absent",
    "complaint: untrusted text"
  ],
  "outputs": [
    "scope: tenantId/customerId/connectionId/accountVersion or null",
    "intake: caseId/status(VALID|NEED_INFO|UNAUTHORIZED|CANCELLED)"
  ],
  "whyCode": "Enforce repeatable scope, exact arithmetic, state and durable evidence without probabilistic authority.",
  "approvalRule": "No model authority. Credit requires fresh policy or exact supervisor approval; notices require current scoped case and verified destination."
}
```


Sources:

- context / user-brief: Keep customers informed, avoid duplicate refunds and use only the right customer's active service connection.

### C2 · Scoped evidence reader

Read only exact tenant/customer/active connection. Typed evidence includes observedAt, resourceVersion, allowed fields, source IDs. Timeout 5s per source, one read retry; missing, stale (>5 minutes for active state), conflicting or unavailable fields route to supervisor. Interval union clips to billing-cycle UTC boundaries; never double-count overlapping outages.

Reasoning: Keeps authority explicit and failures owned.

Data:

```json
{
  "group": "Code: tools",
  "taskIds": [
    "T2"
  ],
  "inputs": [
    "scope: C1.scope required",
    "caseId: durable intake ID"
  ],
  "outputs": [
    "evidence: signed policy/version; billing recurring charge and cycle; outage intervals and source IDs; freshness",
    "readStatus: OK|MISSING|CONFLICT|UNAVAILABLE"
  ],
  "whyCode": "Enforce repeatable scope, exact arithmetic, state and durable evidence without probabilistic authority.",
  "approvalRule": "No model authority. Credit requires fresh policy or exact supervisor approval; notices require current scoped case and verified destination."
}
```


Sources:

- context / user-brief: Keep customers informed, avoid duplicate refunds and use only the right customer's active service connection.

### C3 · Evidence-grounded explanation

One call, deadline 12s. May explain service/billing evidence, cannot supply amount, dates or IDs for writes. Code verifies citations against admitted source fields; invalid/unavailable output uses fixed template and human route. Customer and retrieved text are untrusted; no tool execution and no hidden HTML/document layer is admitted.

Reasoning: Keeps authority explicit and failures owned.

Data:

```json
{
  "group": "Agents (LLM)",
  "taskIds": [
    "T2"
  ],
  "inputs": [
    "evidence: minimized C2 evidence and allowed source IDs",
    "complaint: plain text treated as data, max 4000 chars"
  ],
  "outputs": [
    "explanation: plain text",
    "citations: source ID and exact quoted field list",
    "disposition: EXPLAIN|ABSTAIN"
  ],
  "whyCode": "",
  "approvalRule": "No model authority. Credit requires fresh policy or exact supervisor approval; notices require current scoped case and verified destination."
}
```


Sources:

- context / user-brief: Keep customers informed, avoid duplicate refunds and use only the right customer's active service connection.

## Workflow rules

### W1 · Check active service

{"state": "C1.intake.status enum and C1.scope are gateway/registry outputs; persist provisional reason for missing/unauthorized, no private reads. Cancelled initial requests create a cancellation disposition.", "transitions": [{"to": "W2", "when": "intake.status == VALID", "mode": "exclusive; first matching predicate wins"}, {"to": "W14", "when": "intake.status != VALID", "mode": "exclusive; first matching predicate wins"}], "failureDisposition": "Persist owned case; no unproved success or blind second action.", "timeout": "Node-specific deadlines in component; server UTC elapsed timers.", "retryPolicy": "Only bounded read retries; no write retry without final absence proof.", "terminalDisposition": ""}

Reasoning: Keeps authority explicit and failures owned.

Data:

```json
{
  "componentId": "C1",
  "taskIds": [
    "T1"
  ],
  "next": [
    "W2",
    "W14"
  ],
  "decision": true,
  "example": "CASE1 follows only recorded component result; guard variables below are authoritative."
}
```


Sources:

- context / user-brief: Keep customers informed, avoid duplicate refunds and use only the right customer's active service connection.

### W2 · Read complaint evidence

{"state": "C2.readStatus and evidence from authoritative sources; non-OK assigns support investigation with provisional case.", "transitions": [{"to": "W3", "when": "readStatus == OK", "mode": "exclusive; first matching predicate wins"}, {"to": "W6", "when": "readStatus != OK", "mode": "exclusive; first matching predicate wins"}], "failureDisposition": "Persist owned case; no unproved success or blind second action.", "timeout": "Node-specific deadlines in component; server UTC elapsed timers.", "retryPolicy": "Only bounded read retries; no write retry without final absence proof.", "terminalDisposition": ""}

Reasoning: Keeps authority explicit and failures owned.

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
  "example": "CASE1 follows only recorded component result; guard variables below are authoritative."
}
```


Sources:

- context / user-brief: Keep customers informed, avoid duplicate refunds and use only the right customer's active service connection.

### W3 · Explain findings

{"state": "validatedModel:boolean produced by C9 citation/schema checker over C3 outputs; timeout, invalid schema, unknown citation or abstain sets false; fixed explanation template remains available. One invocation, no retry.", "transitions": [{"to": "W4", "when": "validatedModel == true", "mode": "exclusive; first matching predicate wins"}, {"to": "W6", "when": "validatedModel == false", "mode": "exclusive; first matching predicate wins"}], "failureDisposition": "Persist owned case; no unproved success or blind second action.", "timeout": "Node-specific deadlines in component; server UTC elapsed timers.", "retryPolicy": "Only bounded read retries; no write retry without final absence proof.", "terminalDisposition": ""}

Reasoning: Keeps authority explicit and failures owned.

Data:

```json
{
  "componentId": "C3",
  "taskIds": [
    "T2"
  ],
  "next": [
    "W4",
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
- EV2: Cross-customer service rejected
- EV5: Conflicting outage cannot authorize text instruction
- EV18: Inactive connection cannot receive credit
- EV19: Poor speed investigated but not auto-credited
- EV20: Invented citation triggers template fallback
- EV21: Stratified end-to-end evidence review
- EV22: Operational safety monitors
- EV23: Release suite and approval evidence
## Acceptance criteria

- Implement exact selected contracts and every linked assertion; no new authority.
- Verified external dependencies H1-H4,H6 remain launch gates.
