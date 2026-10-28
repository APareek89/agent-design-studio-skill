# Conditional ticket writer part 1

> PASS | DESIGN ONLY. self-review; round 2.

Depends on earlier milestones where their outputs are inputs below. Cross-milestone shared types are read by ID from ../design.json, not copied.

## Selected contracts

### C6 · Conditional ticket writer

Proposed POST /city/{cityId}/ticket-actions accepts {operationId,businessKey,planId,planVersion,approvalId}; fetches immutable plan, recomputes digest and validates full payload and live operator authority, current case/revision, city/resource, policyVersion, crewVersion, crew eligibility and ticket version/status (LINK). businessKey=cityId:intakeId:reportRevision, unique across CREATE and LINK, so same report cannot be applied twice. Atomically reserve businessKey and operationId in authoritative ledger before mutation; conditional write/unique constraint closes race. CREATE duplicate same asset/time is not alone denial: operator must resolve existing open tickets from fresh search; C6 rejects NEW_CANDIDATE if snapshot changed. Commit proof is operationId, ticketId, linkId if LINK, resulting ticketVersion, payloadDigest and durable ledger sequence. 5s timeout; never blind write retry. Local dispatch journal marks MAY_HAVE_SENT before network call. Credential is ticket create/attach only; equipment destinations blocked by network and allowlist. BUSINESS_KEY_EXISTS returns the existing operation pointer and its immutable winning intent; wrapper journals that operation as MAY_HAVE_SENT for readback. A mismatched losing plan is not claimed as applied. Recovered original receipt is labelled EXISTING_ACTION_RECOVERED and supervisor owns any conflicting desired change.

Reasoning: Chosen to make the stated workflow explicit and bounded.

Assumptions:

- H2: A city-scoped ticket ledger, GIS asset registry and versioned crew routing table can provide read APIs; create-ticket and attach-report commands require a verified adapter.

- H3: Each ticket write requires a currently authorized operator approval; tenant is city ID, and operation, resource, report revision, immutable payload digest and policy version are bound to approval.

- H5: Suggested duplicates require operator selection of an existing ticket on the same asset; fuzzy similarity never merges or suppresses reports. Existing ticket links do not change crew assignment or close work.

- H10: Proposed operational limits: each read attempt 5 seconds, one read retry; LLM attempt 10 seconds with one retry; ticket write timeout 5 seconds with zero automatic write retry; reconciliation reads at 5, 30 and 120 seconds, then owned unknown hold with 15-minute read-only watchdog. Proposed additional limits: snapshot age at plan creation 60 seconds, plan/approval expiry 5 elapsed minutes, routine nonhuman response p95 30 seconds, and unknown-held >1 hour escalates service manager. These limits require verification, not established policy.

Data:

```json
{
  "group": "Code: tools",
  "taskIds": [
    "T6"
  ],
  "inputs": [
    "request:{operationId:string,businessKey:string,planId:string,planVersion:int,approvalId:string}; required",
    "plan/approval:immutable records fetched by ID; required; whole canonical payload binding",
    "live:{actorAuthorized:boolean,caseVersion:int,reportRevision:int,policyVersion:string,crewVersion:string,ticketVersion?:int,ticketStatus?:enum}; API-produced, LINK conditionals required"
  ],
  "outputs": [
    "writeResult:COMMITTED|NOT_SENT|AUTH_DENIED|STALE|WRONG_CITY|INVALID|CONFLICT|UNKNOWN; required",
    "reason?:AUTH_REVOKED|DIGEST_MISMATCH|STALE_POLICY|STALE_CASE|STALE_TICKET|NO_CREW|NEW_CANDIDATE|BUSINESS_KEY_EXISTS|INVALID_PAYLOAD|TIMEOUT|WRONG_CITY; required except COMMITTED",
    "receipt?:{operationId,ticketId,linkId?:string,ticketVersion:int,payloadDigest,ledgerSequence:int}; required COMMITTED; linkId required LINK",
    "journal:{operationId,businessKey,state:NOT_SENT|MAY_HAVE_SENT|COMMITTED|NOT_COMMITTED,ownerRole,caseVersion}; durable before/after attempt",
    "priorOperation?:{operationId,businessKey,cityId,planId,payloadDigest}; required on BUSINESS_KEY_EXISTS; authoritative winning operation pointer, never caller-supplied"
  ],
  "whyCode": "All authorization, versions, uniqueness, commit proof and errors must be enforced at the authoritative action API; UI checks are insufficient.",
  "approvalRule": "No ticket write before verified adapter supports these guarantees (H2/H3). API checks authority afresh at commit, including revocation after approval."
}
```


Sources:

- hypothesis / H2: A city-scoped ticket ledger, GIS asset registry and versioned crew routing table can provide read APIs; create-ticket and attach-report commands require a verified adapter.

- hypothesis / H3: Each ticket write requires a currently authorized operator approval; tenant is city ID, and operation, resource, report revision, immutable payload digest and policy version are bound to approval.

- hypothesis / H5: Suggested duplicates require operator selection of an existing ticket on the same asset; fuzzy similarity never merges or suppresses reports. Existing ticket links do not change crew assignment or close work.

- hypothesis / H10: Proposed operational limits: each read attempt 5 seconds, one read retry; LLM attempt 10 seconds with one retry; ticket write timeout 5 seconds with zero automatic write retry; reconciliation reads at 5, 30 and 120 seconds, then owned unknown hold with 15-minute read-only watchdog. Proposed additional limits: snapshot age at plan creation 60 seconds, plan/approval expiry 5 elapsed minutes, routine nonhuman response p95 30 seconds, and unknown-held >1 hour escalates service manager. These limits require verification, not established policy.

## Workflow rules

### W6 · Apply conditional ticket action

{"state":"WRITE","guardBindings":{"writeResult":"C6.writeResult; any timeout or unparseable response after MAY_HAVE_SENT maps UNKNOWN, including post-cancel","reason":"C6.reason typed enum; BUSINESS_KEY_EXISTS includes authoritative priorOperation pointer"},"transitions":[{"to":"W9","when":"writeResult == COMMITTED","mode":"exclusive"},{"to":"W7","when":"writeResult == UNKNOWN OR (writeResult == CONFLICT AND reason == BUSINESS_KEY_EXISTS)","mode":"exclusive"},{"to":"W8","when":"writeResult in [NOT_SENT,AUTH_DENIED,STALE,WRONG_CITY,INVALID] OR (writeResult == CONFLICT AND reason != BUSINESS_KEY_EXISTS)","mode":"exclusive"}],"failureDisposition":"No retry of ticket action after uncertain send. Failed known outcomes keep explicit reason; known business-key existing receipt must be recovered via W7, not overwritten.","timeout":"5s","retryPolicy":"0 write retries; same operation replay only allowed by API idempotency proof, implementation defaults to readback","terminalDisposition":""}

Reasoning: Chosen to make the stated workflow explicit and bounded.

Assumptions:

- H3: Each ticket write requires a currently authorized operator approval; tenant is city ID, and operation, resource, report revision, immutable payload digest and policy version are bound to approval.

- H4: Potential exposed wires, fallen poles, sparks or fire enter a staffed urgent manual queue immediately; proposed acknowledgement 2 elapsed minutes and supervisor escalation at 2 minutes; routine exceptions acknowledge within 30 staffed minutes and escalate at 30.

- H10: Proposed operational limits: each read attempt 5 seconds, one read retry; LLM attempt 10 seconds with one retry; ticket write timeout 5 seconds with zero automatic write retry; reconciliation reads at 5, 30 and 120 seconds, then owned unknown hold with 15-minute read-only watchdog. Proposed additional limits: snapshot age at plan creation 60 seconds, plan/approval expiry 5 elapsed minutes, routine nonhuman response p95 30 seconds, and unknown-held >1 hour escalates service manager. These limits require verification, not established policy.

Data:

```json
{
  "componentId": "C6",
  "taskIds": [
    "T6"
  ],
  "next": [
    "W9",
    "W7",
    "W8"
  ],
  "decision": true,
  "example": "Timeout after MAY_HAVE_SENT -> W7."
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
- EV5: Concurrent same-report CREATE cannot duplicate
- EV6: Valid operator-selected LINK positive control
- EV7: Revoked actor denied at commit
- EV8: Changed routing policy invalidates approval
- EV9: Concurrent ticket edit rejects stale LINK
- EV10: Payload tampering fails digest binding
- EV11: Injection cannot invoke equipment or fabricate target
- EV12: Lost commit recovered after session expiry and duplicate callback
- EV13: Unknown effect remains locked during cancellation/change
- EV16: LINK rejects forbidden CREATE fields even with valid digest
- EV20: Full release and live invariant gates
- EV22: Online safety, queue, drift and cost observation
- EV25: Closed candidate cannot receive new report
- EV27: Direct equipment command blocked before transport
## Acceptance criteria

- Implement these exact branch rules and all named eval assertions. No equipment controls.
