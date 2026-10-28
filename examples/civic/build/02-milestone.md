# Authoritative context read adapter part 1

> PASS | DESIGN ONLY. self-review; round 2.

Depends on earlier milestones where their outputs are inputs below. Cross-milestone shared types are read by ID from ../design.json, not copied.

## Selected contracts

### C2 · Authoritative context read adapter

Proposed GET context(cityId,caseId,assetId?,address?,reportRevision) returns asset evidence, same-city candidate tickets and policy/crew snapshots. Exact asset + bounded same-street search; at most 20 candidates, no cross-city retrieval. No ticket result is valid only after successful search. Read-attempt 5s, one retry with same keys. Ambiguous geocode remains ambiguous; address text never authorizes a city/asset. Adapter API availability is unverified.

Reasoning: Chosen to make the stated workflow explicit and bounded.

Assumptions:

- H2: A city-scoped ticket ledger, GIS asset registry and versioned crew routing table can provide read APIs; create-ticket and attach-report commands require a verified adapter.

- H7: Proposed routing uses a versioned GIS boundary, asset ownership, fault category and crew capability/on-duty table; unresolved boundary, unavailable crew or conflicting asset evidence goes to supervisor.

- H10: Proposed operational limits: each read attempt 5 seconds, one read retry; LLM attempt 10 seconds with one retry; ticket write timeout 5 seconds with zero automatic write retry; reconciliation reads at 5, 30 and 120 seconds, then owned unknown hold with 15-minute read-only watchdog. Proposed additional limits: snapshot age at plan creation 60 seconds, plan/approval expiry 5 elapsed minutes, routine nonhuman response p95 30 seconds, and unknown-held >1 hour escalates service manager. These limits require verification, not established policy.

Data:

```json
{
  "group": "Code: tools",
  "taskIds": [
    "T2"
  ],
  "inputs": [
    "intake:C1.intake; required",
    "claims:{cityId:string,serviceScope:context.read}; required"
  ],
  "outputs": [
    "readResult:OK|UNAVAILABLE|NOT_FOUND|CONFLICT|AUTH_DENIED|INVALID; required after bounded retry",
    "snapshot?:{cityId:string,asset:{id,owner,geometryVersion,locationEvidence}?,tickets:[{id,assetId,status,version}],routing:{policyId,version,crewVersion,rules,crews},observedAt:UTC}; required on OK",
    "conflictReason?:ASSET_ADDRESS_MISMATCH|MULTIPLE_ASSETS; if CONFLICT",
    "reason:string enum=NONE|CONTEXT_UNAVAILABLE|ASSET_NOT_FOUND|ASSET_ADDRESS_MISMATCH|MULTIPLE_ASSETS|AUTH_DENIED|INVALID_CONTEXT; required"
  ],
  "whyCode": "Retrieval, tenant filtering, timeout and version attribution must be deterministic.",
  "approvalRule": "City-scoped read-only service credential; no telemetry/equipment credentials."
}
```


Sources:

- hypothesis / H2: A city-scoped ticket ledger, GIS asset registry and versioned crew routing table can provide read APIs; create-ticket and attach-report commands require a verified adapter.

- hypothesis / H7: Proposed routing uses a versioned GIS boundary, asset ownership, fault category and crew capability/on-duty table; unresolved boundary, unavailable crew or conflicting asset evidence goes to supervisor.

- hypothesis / H10: Proposed operational limits: each read attempt 5 seconds, one read retry; LLM attempt 10 seconds with one retry; ticket write timeout 5 seconds with zero automatic write retry; reconciliation reads at 5, 30 and 120 seconds, then owned unknown hold with 15-minute read-only watchdog. Proposed additional limits: snapshot age at plan creation 60 seconds, plan/approval expiry 5 elapsed minutes, routine nonhuman response p95 30 seconds, and unknown-held >1 hour escalates service manager. These limits require verification, not established policy.

## Workflow rules

### W2 · Read context snapshot

{"state":"READ_CONTEXT","guardBindings":{"readResult":"C2.readResult enum after retry"},"transitions":[{"to":"W3","when":"readResult == OK","mode":"exclusive"},{"to":"W8","when":"readResult in [UNAVAILABLE,NOT_FOUND,CONFLICT,AUTH_DENIED,INVALID]","mode":"exclusive"}],"failureDisposition":"Read failure never treated as empty ticket list.","timeout":"5s/attempt","retryPolicy":"1 read retry; at most 10s total then owned manual","terminalDisposition":""}

Reasoning: Chosen to make the stated workflow explicit and bounded.

Assumptions:

- H3: Each ticket write requires a currently authorized operator approval; tenant is city ID, and operation, resource, report revision, immutable payload digest and policy version are bound to approval.

- H4: Potential exposed wires, fallen poles, sparks or fire enter a staffed urgent manual queue immediately; proposed acknowledgement 2 elapsed minutes and supervisor escalation at 2 minutes; routine exceptions acknowledge within 30 staffed minutes and escalate at 30.

- H10: Proposed operational limits: each read attempt 5 seconds, one read retry; LLM attempt 10 seconds with one retry; ticket write timeout 5 seconds with zero automatic write retry; reconciliation reads at 5, 30 and 120 seconds, then owned unknown hold with 15-minute read-only watchdog. Proposed additional limits: snapshot age at plan creation 60 seconds, plan/approval expiry 5 elapsed minutes, routine nonhuman response p95 30 seconds, and unknown-held >1 hour escalates service manager. These limits require verification, not established policy.

Data:

```json
{
  "componentId": "C2",
  "taskIds": [
    "T2"
  ],
  "next": [
    "W3",
    "W8"
  ],
  "decision": true,
  "example": "Search unavailable -> W8 reason CONTEXT_UNAVAILABLE."
}
```


Sources:

- hypothesis / H3: Each ticket write requires a currently authorized operator approval; tenant is city ID, and operation, resource, report revision, immutable payload digest and policy version are bound to approval.

- hypothesis / H4: Potential exposed wires, fallen poles, sparks or fire enter a staffed urgent manual queue immediately; proposed acknowledgement 2 elapsed minutes and supervisor escalation at 2 minutes; routine exceptions acknowledge within 30 staffed minutes and escalate at 30.

- hypothesis / H10: Proposed operational limits: each read attempt 5 seconds, one read retry; LLM attempt 10 seconds with one retry; ticket write timeout 5 seconds with zero automatic write retry; reconciliation reads at 5, 30 and 120 seconds, then owned unknown hold with 15-minute read-only watchdog. Proposed additional limits: snapshot age at plan creation 60 seconds, plan/approval expiry 5 elapsed minutes, routine nonhuman response p95 30 seconds, and unknown-held >1 hour escalates service manager. These limits require verification, not established policy.

## Required tests

For each ID below, load ../eval-set.json items[id].data.input, .expected and .passRule. These are the full fixture, expected result and exact assertions; no inherited test context is assumed.

- EV1: Valid CREATE positive control
- EV3: Writer rejects resource city mismatch
- EV4: Contradictory location retained as human case
- EV5: Concurrent same-report CREATE cannot duplicate
- EV6: Valid operator-selected LINK positive control
- EV9: Concurrent ticket edit rejects stale LINK
- EV17: Context outage persists owned report without guessing
- EV18: Privacy redaction and proposed retention controls
- EV20: Full release and live invariant gates
- EV22: Online safety, queue, drift and cost observation
- EV25: Closed candidate cannot receive new report
- EV26: Invalid model output exhausted into owned fallback
## Acceptance criteria

- Implement these exact branch rules and all named eval assertions. No equipment controls.
