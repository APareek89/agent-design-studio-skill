# Prove and close

> NEEDS-WORK | DESIGN ONLY. independent-agent; round 1.

Depends on earlier milestones where their outputs are inputs below. Cross-milestone shared types are read by ID from ../design.json, not copied.

## Selected contracts

### C9 · Record proof and close

Credit completion requires readback matching all command fields; all other dispositions require persisted case reason/owner/version. Unknown is not completed refund and retains operation lock. Missing/mismatched proof becomes owned unresolved status; no success assertion. Code templates verify LLM explanation citations and all amounts before display. Explicit proof projection: CREDITED requires a matching ledger posting from C7/C8; C1 case IDs can never prove a credit. Other states require a fresh scoped durable case record with reason, owner and version. Missing/empty/wrong-source ID yields MISSING, never VERIFIED.

Reasoning: Keeps authority explicit and failures owned.

Data:

```json
{
  "group": "Code: validation",
  "taskIds": [
    "T3.3",
    "T4"
  ],
  "inputs": [
    "caseId: durable scoped case ID",
    "outcome: CREDITED|NO_CREDIT|CANCELLED|HUMAN_OWNED|UNKNOWN_OWNED",
    "proof: matching posting ID if CREDITED; durable case disposition/version/owner for others",
    "verifiedRecordId:string! on a proven outcome; required nonempty trusted record projection, otherwise reject proof"
  ],
  "outputs": [
    "guard: VERIFIED|MISSING|MISMATCH",
    "closure: scoped status with record ID and next update owner",
    "validatedModel: boolean from explanation schema and exact source-field citation verification"
  ],
  "whyCode": "Enforce repeatable scope, exact arithmetic, state and durable evidence without probabilistic authority.",
  "approvalRule": "No model authority. Credit requires fresh policy or exact supervisor approval; notices require current scoped case and verified destination."
}
```


Sources:

- context / user-brief: Keep customers informed, avoid duplicate refunds and use only the right customer's active service connection.

## Workflow rules

### W14 · Verify durable proof

{"state": "guard:C9 output; requires posting readback matches command for CREDITED, scoped durable case record for every other outcome. Unknown state explicitly retained; never mapped to no-credit or refund success.", "transitions": [{"to": "W15", "when": "guard == VERIFIED", "mode": "exclusive; first matching predicate wins"}, {"to": "W16", "when": "guard == MISSING or guard == MISMATCH", "mode": "exclusive; first matching predicate wins"}], "failureDisposition": "Persist owned case; no unproved success or blind second action.", "timeout": "Node-specific deadlines in component; server UTC elapsed timers.", "retryPolicy": "Only bounded read retries; no write retry without final absence proof.", "terminalDisposition": "", "bindings": {"verifiedRecordId": [{"sourceComponentId": "C1", "sourceField": "verifiedRecordId"}, {"sourceComponentId": "C7", "sourceField": "verifiedRecordId"}, {"sourceComponentId": "C8", "sourceField": "verifiedRecordId"}]}, "recordProofPolicy": "CREDITED requires a matching ledger posting from C7/C8; C1 case IDs can never prove a credit. Other states require a fresh scoped durable case record with reason, owner and version. Missing/empty/wrong-source ID yields MISSING, never VERIFIED."}

Reasoning: Keeps authority explicit and failures owned.

Data:

```json
{
  "componentId": "C9",
  "taskIds": [
    "T3.3",
    "T4"
  ],
  "next": [
    "W15",
    "W16"
  ],
  "decision": true,
  "example": "CASE1 follows only recorded component result; guard variables below are authoritative."
}
```


Sources:

- context / user-brief: Keep customers informed, avoid duplicate refunds and use only the right customer's active service connection.

### W15 · Show proved status

{"state": "C9.closure verified by W14. Customer gets case reference, reason, proof and next update time for owned unresolved cases.", "transitions": [], "failureDisposition": "Persist owned case; no unproved success or blind second action.", "timeout": "Node-specific deadlines in component; server UTC elapsed timers.", "retryPolicy": "Only bounded read retries; no write retry without final absence proof.", "terminalDisposition": "Durable disposition: CREDITED, NO_CREDIT, CANCELLED, HUMAN_OWNED or UNKNOWN_OWNED. Only CREDITED claims a service credit posted."}

Reasoning: Keeps authority explicit and failures owned.

Data:

```json
{
  "componentId": "C9",
  "taskIds": [
    "T4"
  ],
  "next": [],
  "decision": false,
  "example": "CASE1 follows only recorded component result; guard variables below are authoritative."
}
```


Sources:

- context / user-brief: Keep customers informed, avoid duplicate refunds and use only the right customer's active service connection.

### W16 · Keep proof failure owned

{"state": "Missing/mismatched proof creates restricted duty-manager incident with original operation lock; in-app message says result not yet confirmed.", "transitions": [], "failureDisposition": "Persist owned case; no unproved success or blind second action.", "timeout": "Node-specific deadlines in component; server UTC elapsed timers.", "retryPolicy": "Only bounded read retries; no write retry without final absence proof.", "terminalDisposition": "UNKNOWN_OWNED: no claim of resolution; operations owns readback and customer update within 2h. No autonomous re-entry or write."}

Reasoning: Keeps authority explicit and failures owned.

Data:

```json
{
  "componentId": "C9",
  "taskIds": [
    "T4"
  ],
  "next": [],
  "decision": false,
  "example": "CASE1 follows only recorded component result; guard variables below are authoritative."
}
```


Sources:

- context / user-brief: Keep customers informed, avoid duplicate refunds and use only the right customer's active service connection.

## Required tests

For each ID below, load ../eval-set.json items[id].data.input, .expected and .passRule. These are the full fixture, expected result and exact assertions; no inherited test context is assumed.

- EV1: Valid outage arithmetic and proof
- EV6: Unknown commit after logout and cancellation
- EV7: No proof means no success
- EV17: Cancellation before submit suppresses credit
- EV20: Invented citation triggers template fallback
- EV21: Stratified end-to-end evidence review
- EV22: Operational safety monitors
- EV23: Release suite and approval evidence
## Acceptance criteria

- Implement exact selected contracts and every linked assertion; no new authority.
- Verified external dependencies H1-H4,H6 remain launch gates.
