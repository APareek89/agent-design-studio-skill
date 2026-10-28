# Streetlight repair intake and operator-assisted routing

> PASS | DESIGN ONLY. self-review; round 2.

## Original brief

I need a system for a small city team to handle streetlight repair requests: classify reports, find existing tickets and route to the right maintenance crew. Five operators handle about 200 reports a day. It must not remotely control equipment.

## Context

- **CTX1 Decision and first release**: Recommend the category, existing-ticket candidates and responsible crew for each operator-entered report. An operator confirms CREATE or LINK before a ticket-ledger write. Completion is a durable ticket/link receipt or a visible owned exception; a recommendation alone is never dispatched work. Reject autonomous dispatch/remote diagnosis as unnecessary authority at this scale.
- **CTX2 Actors, trigger and capacity**: Five operators handle about 200 reports a day, from the user brief. Trigger is an authenticated operator submitting a text report. Proposed roles: duty supervisor owns urgent and ambiguous cases; maintenance lead owns route policy; IT lead owns adapters and recovery. 40 reports/operator/day is only an equal-allocation arithmetic average; shift length and peak arrival rate are unknown. Baseline captures these before capacity claims.
- **CTX3 Inputs, outcomes and exclusions**: Inputs: city/session claims, intake ID/revision/text, optional asset ID/address, authoritative asset/ticket/crew snapshots. Outputs: category, evidence, candidates, proposed crew, operator decision, durable ticket/link or owned queue case. No equipment connectivity, switching, reset, dimming, telemetry commands, work completion claims, citizen messaging, autonomous ticket closure, procurement or crew scheduling optimization. Cancellation cancels a pending proposal only; existing committed tickets are handed to a human for separately authorized handling.
- **CTX4 Human dispositions and service windows**: Urgent reports are surfaced immediately even if information is missing. C8 durably owns every exception with supervisor, reason, status and next due time; C5 records ACK/APPROVE/REJECT/CANCEL/OVERDUE. Urgent acknowledgement uses elapsed clock, routine timers use the published staffed calendar. No confirmed out-of-hours procedure means no real launch; no promise that software substitutes for emergency response.
- **CTX5 Value and measurement**: R1 defines handling minutes/report and correct first-route fraction; lower search/edit time is the intended benefit. R2 guards urgent detection and safe ticket writes. Unknown baseline must be collected. No repair-time or public-safety improvement claim follows from a triage recommendation; repair outcomes can be a secondary descriptive signal.
- **CTX6 Authority and integration boundary**: Proposed adapters remain launch dependencies. No actual city policy, API or provider has been verified. Before adapter authority is proven, implementation may persist internal proposed cases and read approved synthetic/sandbox data only. Remote equipment APIs are absent from schemas, credentials, network allowlist and model tools.

## Tasks

- **T0 Resolve a streetlight report**: Run intake, retrieve, recommend, validate, obtain decision and persist in that order when eligible; exception/cancel ends the spine through T8. Reconciliation T7 replaces retry when a T6 commit is unknown.
- **T1 Validate and register intake**: Authenticate city/operator, deduplicate exact intake delivery, validate command/revision, minimize data and apply deterministic urgent indicators before any dependency call.
- **T2 Read asset, candidate tickets and routing policy**: Read same-city GIS asset evidence, current/open/recent tickets and crew policy; correlate exact asset and geography with evidence.
- **T3 Classify and explain**: One LLM extracts fault enum and cited spans, urgency signal, candidate rationale and abstention. It cannot create IDs, set permissions or choose executable tools.
- **T4 Construct safe routing proposal**: Code maps asset/category to a current eligible crew, validates candidates, forms an immutable CREATE or operator-selected LINK plan.
- **T5 Obtain operator decision**: Show report, evidence, candidate status and route. Capture payload-bound approval or cancel/reject; supervisor handles unknowns and overdue.
- **T6 Persist approved ticket action**: Create ticket or attach intake to existing ticket using action API checks, city/report uniqueness and durable receipt. No equipment access.
- **T7 Reconcile unknown write**: Read operation and report-uniqueness index; recover durable committed receipt, definite not-committed proof or retain owned unknown hold.
- **T8 Own exceptions, cancellation and completion**: Persist durable status, owner, due time and audit. Cancel only uncommitted proposal; while unknown freeze changed intent and record cancel pending reconciliation.
- **A1 City and current actor authority**: Verified city identity service/session and live policy evaluator; never report text
- **A2 Report facts and asset evidence**: Immutable local intake revision, optional operator asset ID, authoritative GIS geometry/version; caller location is evidence only
- **A3 Ticket and operation state**: Authoritative city ticket ledger, ticket versions, report uniqueness index and operation idempotency readback
- **A4 Routing policy and crew eligibility**: Maintenance-lead published policy/version, on-duty table/version, city calendar and current authorization
- **A5 Approval, payload and recovery ownership**: Immutable plan store + canonical digest, signed decision record, operation journal, queue/timer ledger

## Components

- **C1 Intake and scope gate**: Local commands SUBMIT {intakeId,revision,text,assetId?,address?} and CANCEL_PROPOSAL {caseId,expectedCaseVersion}; command replaces entire payload. City/actor come from verified identity. Reject unknown keys, >12000 text chars and non-text formats to owned queue. Missing location is allowed provisionally. Same city/intakeId/revision is exactly-once local ingest. Conflicting revision enters owned conflict. Redact contacts before model; untrusted text is data. Preserve original in restricted local store. Fast hazard patterns raise urgency and cannot be downgraded. receivedAt is trusted server ingestion time preserved on replay, never caller time.
- **C2 Authoritative context read adapter**: Proposed GET context(cityId,caseId,assetId?,address?,reportRevision) returns asset evidence, same-city candidate tickets and policy/crew snapshots. Exact asset + bounded same-street search; at most 20 candidates, no cross-city retrieval. No ticket result is valid only after successful search. Read-attempt 5s, one retry with same keys. Ambiguous geocode remains ambiguous; address text never authorizes a city/asset. Adapter API availability is unverified.
- **C3 Bounded text triage judgement**: Classify fault from text and supplied evidence, flag hazard and explain same-asset candidate relevance. No browsing or tool invocation. Report text and ticket descriptions are untrusted content and cannot change system rules. Return schema, citations and abstain; ignore instructions embedded in content. Conflicting evidence or absent usable location is not solved by guess. One retry for transport/invalid shape on identical snapshot; then manual.
- **C4 Route resolver and immutable plan validator**: Code checks model evidence quotes against input and candidate IDs against snapshot. Any hazard from C1 or C3 wins precedence; no automatic down-ranking. Missing/contradictory location, abstain, other/unknown category, unavailable crew, stale snapshots or semantic duplicates require owned operator review. With exact asset and routine category map policy rules to one eligible crew. Present CREATE draft and candidate LINK choices; when operator selects LINK construct a new immutable plan. CREATE creates one new ticket; LINK appends a report reference only to an open same-asset ticket, preserves existing assignment. Closed tickets and different faults need supervisor deciding CREATE under current policy. No fuzzy merging. Payload uses canonical UTF-8 JSON, sorted object keys, compact separators, integers/strings, no floats, SHA-256 digest.
- **C5 Operator decision queue**: Persist proposal in city routine review queue; assigned operator ACK deadline 30 staffed minutes then supervisor takes ownership. Hazard is separate urgent manual queue; no approval path auto-dispatches hazard. Events ACK, APPROVE, REJECT, CANCEL, OVERDUE are signed by identity service and server timed. APPROVE binds exact immutable plan/digest plus actor, city, action, resource (asset for CREATE, ticket for LINK), report revision, policy/crew versions, expiresAt and decisionId. Show all action-critical fields and provenance. Any edit produces a new plan/approval. Reject/cancel retains intake audit; no citizen message. A timer job survives caller closure. Routine acknowledgement due time starts at durable queueCreatedAt; plan expiry uses trusted createdAt. Acknowledgement neither authorizes a write nor resets plan expiry.
- **C6 Conditional ticket writer**: Proposed POST /city/{cityId}/ticket-actions accepts {operationId,businessKey,planId,planVersion,approvalId}; fetches immutable plan, recomputes digest and validates full payload and live operator authority, current case/revision, city/resource, policyVersion, crewVersion, crew eligibility and ticket version/status (LINK). businessKey=cityId:intakeId:reportRevision, unique across CREATE and LINK, so same report cannot be applied twice. Atomically reserve businessKey and operationId in authoritative ledger before mutation; conditional write/unique constraint closes race. CREATE duplicate same asset/time is not alone denial: operator must resolve existing open tickets from fresh search; C6 rejects NEW_CANDIDATE if snapshot changed. Commit proof is operationId, ticketId, linkId if LINK, resulting ticketVersion, payloadDigest and durable ledger sequence. 5s timeout; never blind write retry. Local dispatch journal marks MAY_HAVE_SENT before network call. Credential is ticket create/attach only; equipment destinations blocked by network and allowlist. BUSINESS_KEY_EXISTS returns the existing operation pointer and its immutable winning intent; wrapper journals that operation as MAY_HAVE_SENT for readback. A mismatched losing plan is not claimed as applied. Recovered original receipt is labelled EXISTING_ACTION_RECOVERED and supervisor owns any conflicting desired change.
- **C7 Read-only commit reconciler**: Proposed GET operation(cityId,operationId,businessKey) with service reconciliation identity independent of caller session. Read at 5/30/120s; durable callback and watchdog use same operation/city/digest, deduplicate callback eventId. Returns COMMITTED with receipt, NOT_COMMITTED only with authoritative final noncommit + released uniqueness reservation, UNKNOWN, or AUTH_DENIED. Not-found alone is UNKNOWN until ledger proves final noncommit. 15-minute watchdog retries read-only after unknown hold and alerts IT; no elapsed timeout means permission to write again. Changed intent/cancel is recorded but frozen while unknown. On receipt, cancel becomes follow-up-required; ticket cancellation/correction is outside scope and separately authorized manually. For BUSINESS_KEY_EXISTS recover the authoritative winning operation/plan/digest, not the losing proposal; any different intended action remains unapplied with supervisor follow-up.
- **C8 Case journal, owner timers and status projection**: Durable local transaction saves terminal status plus reason, ownerRole, ackDueAt/nextReadAt, operation linkage, receipt and audit. Statuses: COMPLETED, CANCELLED_PROPOSAL, OWNED_MANUAL, UNKNOWN_HELD. COMPLETED requires actual C6/C7 receipt and means ticket action recorded, never equipment repaired. Urgent and ordinary queue entries notify only internal configured console; out-of-hours delivery contract must be verified before launch. Owner ACK does not close case. Timer persists after operator logout, overdue changes owner to duty supervisor, then at another 2 urgent elapsed/30 routine staffed minutes escalate service manager console. Reconciliation outage also escalates IT operations. Manual outcomes are recorded resolution events; cannot fabricate ticket receipt. Unknown holds freeze fresh writes for same businessKey; watchdog creates W7 read-only reconciliation instance, never restarts W1. Before-send cancellation wins if CAS before journal MAY_HAVE_SENT; after that freeze and reconcile. Input reason mapping is exact upstream C1/C2/C3/C4/C5/C6 reason string; C7 NOT_COMMITTED maps WRITE_NOT_COMMITTED, UNKNOWN maps COMMIT_UNKNOWN, AUTH_DENIED maps RECOVERY_AUTH_DENIED, INVALID_CALLBACK maps INVALID_CALLBACK. W9/W10 explicitly dispatch failed finalization; their terminal projection nodes are idempotent no-op reads of already saved status. Urgent ackDueAt is intake.receivedAt + 2 elapsed minutes even when model/retrieval took time; routine due is queueCreatedAt + 30 staffed minutes using the frozen calendar version. Retention worker runs daily with data-owner-approved versioned H6 policy; removes restricted raw data at day 30 and recommendation snapshots at day 90, minimizes audit until day 365, emits deletion receipts. Unresolved operation IDs, immutable action payload/digest, approvals and receipt proof are not automatically purged while UNKNOWN_HELD; retention exception is visible to data owner for review. This evidence contains no reporter contact; real backup/legal-hold deletion behavior remains H6 verification dependency.

## Workflow

- **W1 Register or cancel intake**: {"state":"ENTRY","guardBindings":{"entryResult":"C1.entryResult enum; priority CANCEL_PROPOSAL evaluated against journal state before other branches"},"transitions":[{"to":"W2","when":"entryResult == ELIGIBLE","mode":"exclusive"},{"to":"W10","when":"entryResult == CANCELLED","mode":"exclusive"},{"to":"W11","when":"entryResult == UNKNOWN_LOCKED","mode":"exclusive"},{"to":"W8","when":"entryResult in [URGENT,INVALID,UNAUTHORIZED,UNSUPPORTED,CONFLICT]","mode":"exclusive"}],"failureDisposition":"Local save failure: return intake unavailable, no accepted-case claim; restricted incident ledger owned by IT.","timeout":"local 2s budget; failure shown to operator","retryPolicy":"0; exact delivery replay returns same case","terminalDisposition":""}
- **W2 Read context snapshot**: {"state":"READ_CONTEXT","guardBindings":{"readResult":"C2.readResult enum after retry"},"transitions":[{"to":"W3","when":"readResult == OK","mode":"exclusive"},{"to":"W8","when":"readResult in [UNAVAILABLE,NOT_FOUND,CONFLICT,AUTH_DENIED,INVALID]","mode":"exclusive"}],"failureDisposition":"Read failure never treated as empty ticket list.","timeout":"5s/attempt","retryPolicy":"1 read retry; at most 10s total then owned manual","terminalDisposition":""}
- **W3 Bounded classification**: {"state":"CLASSIFY","guardBindings":{"modelResult":"C3.wrapper modelResult after at most 2 attempts"},"transitions":[{"to":"W4","when":"modelResult == VALID","mode":"exclusive"},{"to":"W8","when":"modelResult in [INVALID,UNAVAILABLE]","mode":"exclusive"}],"failureDisposition":"Invalid schema or unknown IDs cannot reach writer.","timeout":"10s/attempt","retryPolicy":"1 identical-input retry for invalid format/transient; no recursive calls","terminalDisposition":""}
- **W4 Build safe immutable plan**: {"state":"PLAN","guardBindings":{"planResult":"C4.planResult enum; URGENT precedence before other validations"},"transitions":[{"to":"W5","when":"planResult == READY","mode":"exclusive"},{"to":"W8","when":"planResult in [URGENT,NEEDS_LOCATION,AMBIGUOUS,UNSUPPORTED,NO_CREW,STALE,INVALID]","mode":"exclusive"}],"failureDisposition":"Missing location and candidate conflict persist visible owned queue.","timeout":"local 2s","retryPolicy":"0; revised operator selection creates new plan and restarts W4 only after fresh W2 snapshot","terminalDisposition":""}
- **W5 Await payload-bound human decision**: {"state":"WAIT_APPROVAL","guardBindings":{"decisionResult":"C5.decisionResult; WAITING resumes same durable wait until event/deadline"},"transitions":[{"to":"W6","when":"decisionResult == APPROVED","mode":"exclusive"},{"to":"W10","when":"decisionResult == CANCELLED","mode":"exclusive"},{"to":"W8","when":"decisionResult in [REJECTED,OVERDUE,AUTH_DENIED,STALE]","mode":"exclusive"}],"failureDisposition":"WAITING is persisted suspension, not a transition. ACK extends no approval expiry.","timeout":"30 staffed minutes ACK deadline; plan expiry 5 elapsed minutes independently enforced","retryPolicy":"0 automatic approval; OVERDUE yields W8","terminalDisposition":""}
- **W6 Apply conditional ticket action**: {"state":"WRITE","guardBindings":{"writeResult":"C6.writeResult; any timeout or unparseable response after MAY_HAVE_SENT maps UNKNOWN, including post-cancel","reason":"C6.reason typed enum; BUSINESS_KEY_EXISTS includes authoritative priorOperation pointer"},"transitions":[{"to":"W9","when":"writeResult == COMMITTED","mode":"exclusive"},{"to":"W7","when":"writeResult == UNKNOWN OR (writeResult == CONFLICT AND reason == BUSINESS_KEY_EXISTS)","mode":"exclusive"},{"to":"W8","when":"writeResult in [NOT_SENT,AUTH_DENIED,STALE,WRONG_CITY,INVALID] OR (writeResult == CONFLICT AND reason != BUSINESS_KEY_EXISTS)","mode":"exclusive"}],"failureDisposition":"No retry of ticket action after uncertain send. Failed known outcomes keep explicit reason; known business-key existing receipt must be recovered via W7, not overwritten.","timeout":"5s","retryPolicy":"0 write retries; same operation replay only allowed by API idempotency proof, implementation defaults to readback","terminalDisposition":""}
- **W7 Reconcile uncertain commit**: {"state":"RECONCILE","guardBindings":{"reconcileResult":"C7 enum after bounded read schedule; callback invalidity cannot substitute for final authoritative committed proof"},"transitions":[{"to":"W9","when":"reconcileResult == COMMITTED","mode":"exclusive"},{"to":"W8","when":"reconcileResult == NOT_COMMITTED","mode":"exclusive"},{"to":"W11","when":"reconcileResult in [UNKNOWN,AUTH_DENIED,INVALID_CALLBACK]","mode":"exclusive"}],"failureDisposition":"Invalid callback has no effect; continue scheduled authoritative reads, then UNKNOWN_HELD. NOT_COMMITTED requires final proof and a new separately approved attempt, never an automatic action.","timeout":"reads at 5,30,120 seconds from write timeout","retryPolicy":"3 reads per instance; watchdog only read-only W7 resume every 15m while unresolved","terminalDisposition":""}
- **W8 Persist owned manual disposition**: {"state":"OWNED_MANUAL","guardBindings":{"reason":"upstream enum/reason mapped to case.reason:string","urgency":"C1.deterministicHazard OR C3.urgency POTENTIAL_HAZARD; missing upstream => routine except deterministic hazard"},"transitions":[],"failureDisposition":"If local queue save fails, do not claim handoff; block new intake and display IT incident + operator manual fallback.","timeout":"2s local persistence","retryPolicy":"0 effect retry beyond transactional event-id dedup","terminalDisposition":"Durable OWNED_MANUAL with owner, reason, calendar-bound due time, visible queue and escalation; manual resubmission requires new revision/plan/approval after any operation lock clears."}
- **W9 Record ticket receipt completion**: {"state":"FINALIZE_RECEIPT","guardBindings":{"persistResult":"C8.persistResult after receipt/city/digest checks and local transaction","terminal.status":"C8.terminal.status only when TERMINAL_SAVED","receipt":"C6/C7 durable matching receipt; required; no absence means completion","cancelRequested":"C8 journal boolean at finalization; if committed sets FOLLOWUP_REQUIRED without reversal"},"transitions":[{"to":"W12","when":"persistResult == TERMINAL_SAVED AND terminal.status == COMPLETED","mode":"exclusive"},{"to":"W11","when":"persistResult in [RECEIPT_MISSING,CANCEL_RACE]","mode":"exclusive"},{"to":"W8","when":"persistResult == SAVE_FAILED","mode":"exclusive"}],"failureDisposition":"Missing/mismatched receipt -> W11 owned unknown; local save failure -> W8 owned incident fallback. No completion emitted before persisted receipt.","timeout":"2s local persistence","retryPolicy":"transaction event-id dedup only; durable operation receipt can be recovered on restart","terminalDisposition":""}
- **W10 Record proposal cancellation**: {"state":"FINALIZE_CANCEL","guardBindings":{"persistResult":"C8 cancellation CAS result; TERMINAL_SAVED only before any MAY_HAVE_SENT","terminal.status":"C8.terminal.status only when saved"},"transitions":[{"to":"W13","when":"persistResult == TERMINAL_SAVED AND terminal.status == CANCELLED_PROPOSAL","mode":"exclusive"},{"to":"W11","when":"persistResult == CANCEL_RACE","mode":"exclusive"},{"to":"W8","when":"persistResult in [SAVE_FAILED,RECEIPT_MISSING]","mode":"exclusive"}],"failureDisposition":"Lost cancellation CAS -> W11; local save failure -> W8 incident fallback. No external-cancellation claim.","timeout":"2s local persistence","retryPolicy":"transaction dedup only","terminalDisposition":""}
- **W11 Hold unknown effect with owner**: {"state":"UNKNOWN_HELD","guardBindings":{"operationId":"C6.journal persisted before send","nextReadAt":"C8 trustedClock + H10 interval; C7 service credential is independent of operator session"},"transitions":[],"failureDisposition":"Recovery authority unavailable => IT owner alert and same write lock remains.","timeout":"2s local persistence","retryPolicy":"15-minute durable watchdog creates only W7 read instance; no second write; no expiry on unknown lock","terminalDisposition":"UNKNOWN_HELD durable supervisor/IT ownership, operationId, nextReadAt and immutable intent; cancellation stored as pending and changed intent frozen."}
- **W12 Project durable ticket receipt**: {"state":"COMPLETED","guardBindings":{"terminal":"C8 already persisted terminal by eventId and case version"},"transitions":[],"failureDisposition":"Projection read unavailable: show pending status and IT incident, never fabricate completion/cancellation. Durable underlying status recoverable by case read.","timeout":"2s local read","retryPolicy":"one local read retry; no ticket mutation","terminalDisposition":"COMPLETED only for matching persisted ticket/link receipt; if cancelRequested true display FOLLOWUP_REQUIRED and supervisor owner, never mark equipment repaired."}
- **W13 Project durable proposal cancellation**: {"state":"CANCELLED_PROPOSAL","guardBindings":{"terminal":"C8 already persisted terminal by eventId and case version"},"transitions":[],"failureDisposition":"Projection read unavailable: show pending status and IT incident, never fabricate completion/cancellation. Durable underlying status recoverable by case read.","timeout":"2s local read","retryPolicy":"one local read retry; no ticket mutation","terminalDisposition":"CANCELLED_PROPOSAL only after saved no-send CAS; original intake audit retained."}

## Framework

### F1 · Pattern and boundary

Choose a durable code workflow with one bounded classification LLM and operator confirmation. Five operators/200 daily reports justify reliability and search assistance before more autonomy.

Reasoning: Chosen to make the stated workflow explicit and bounded.

Assumptions:

- H2: A city-scoped ticket ledger, GIS asset registry and versioned crew routing table can provide read APIs; create-ticket and attach-report commands require a verified adapter.

- H3: Each ticket write requires a currently authorized operator approval; tenant is city ID, and operation, resource, report revision, immutable payload digest and policy version are bound to approval.

Data:

```json
{
  "category": "fit",
  "taskIds": [
    "T0"
  ],
  "choice": "Choose a durable code workflow with one bounded classification LLM and operator confirmation. Five operators/200 daily reports justify reliability and search assistance before more autonomy.",
  "alternatives": [
    "Rejected autonomous multi-agent dispatch: unnecessary authority, harder replay and more calls.",
    "Code-only rules remain fallback and comparison: reliable known categories but less useful for varied text."
  ],
  "tradeoffs": "One model call handles judgement; code owns policy and effects. Replace LLM with code-only if held-out routing gains do not justify cost/latency.",
  "permission": "none",
  "blastRadius": "One city and one report-revision business key per write; no device or infrastructure control.",
  "approvalRule": "All ticket actions require C5 approval and fresh C6 API checks; no design approval grants operational authority.",
  "leastPrivilege": "Separate context-read, ticket-create/attach and operation-read identities; no shared broad admin or equipment credential.",
  "aws": "",
  "gcp": "",
  "azure": "",
  "openSource": ""
}
```


Sources:

- hypothesis / H2: A city-scoped ticket ledger, GIS asset registry and versioned crew routing table can provide read APIs; create-ticket and attach-report commands require a verified adapter.

- hypothesis / H3: Each ticket write requires a currently authorized operator approval; tenant is city ID, and operation, resource, report revision, immutable payload digest and policy version are bound to approval.

### F2 · State and ownership

Choose transactional relational case/plan/approval/outbox journal with persisted timer jobs, W1–W11 and CAS versions. Authoritative city ticket system owns actual tickets; local store owns proposals, approvals and pending/recovery status.

Reasoning: Chosen to make the stated workflow explicit and bounded.

Assumptions:

- H2: A city-scoped ticket ledger, GIS asset registry and versioned crew routing table can provide read APIs; create-ticket and attach-report commands require a verified adapter.

- H3: Each ticket write requires a currently authorized operator approval; tenant is city ID, and operation, resource, report revision, immutable payload digest and policy version are bound to approval.

Data:

```json
{
  "category": "architecture",
  "taskIds": [
    "T0"
  ],
  "choice": "Choose transactional relational case/plan/approval/outbox journal with persisted timer jobs, W1–W11 and CAS versions. Authoritative city ticket system owns actual tickets; local store owns proposals, approvals and pending/recovery status.",
  "alternatives": [
    "Rejected in-memory chat chain: loses human waits and unknown-commit ownership."
  ],
  "tradeoffs": "Simple deploy footprint but requires robust timer worker, backups, recovery drills and adapter proof. Search snapshots are never authoritative for commit.",
  "permission": "none",
  "blastRadius": "One city and one report-revision business key per write; no device or infrastructure control.",
  "approvalRule": "All ticket actions require C5 approval and fresh C6 API checks; no design approval grants operational authority.",
  "leastPrivilege": "Separate context-read, ticket-create/attach and operation-read identities; no shared broad admin or equipment credential.",
  "aws": "",
  "gcp": "",
  "azure": "",
  "openSource": ""
}
```


Sources:

- hypothesis / H2: A city-scoped ticket ledger, GIS asset registry and versioned crew routing table can provide read APIs; create-ticket and attach-report commands require a verified adapter.

- hypothesis / H3: Each ticket write requires a currently authorized operator approval; tenant is city ID, and operation, resource, report revision, immutable payload digest and policy version are bound to approval.

### F3 · Orchestration comparison

Choose a small code state machine + relational job queue initially. Criteria are durable human wait, retry visibility, replay, operating burden and city team maintainability.

Reasoning: Chosen to make the stated workflow explicit and bounded.

Assumptions:

- H2: A city-scoped ticket ledger, GIS asset registry and versioned crew routing table can provide read APIs; create-ticket and attach-report commands require a verified adapter.

- H3: Each ticket write requires a currently authorized operator approval; tenant is city ID, and operation, resource, report revision, immutable payload digest and policy version are bound to approval.

Data:

```json
{
  "category": "orchestration",
  "taskIds": [
    "T0"
  ],
  "choice": "Choose a small code state machine + relational job queue initially. Criteria are durable human wait, retry visibility, replay, operating burden and city team maintainability.",
  "alternatives": [
    "Candidate durable workflow engine: investigate managed or open-source workflow engine if timer/recovery load outgrows SQL queue; verify actual product capabilities.",
    "Candidate graph-agent library: useful for model experiments but does not remove need for durable transaction/approval ledger."
  ],
  "tradeoffs": "Code queue: fewer moving parts, recovery logic owned by IT. Workflow engine: evaluate durable timers/replay on same fixtures and operating burden in spike. Graph library: evaluate same durability needs before selection; no current vendor capability claim. No framework/provider chosen by brand.",
  "permission": "none",
  "blastRadius": "One city and one report-revision business key per write; no device or infrastructure control.",
  "approvalRule": "All ticket actions require C5 approval and fresh C6 API checks; no design approval grants operational authority.",
  "leastPrivilege": "Separate context-read, ticket-create/attach and operation-read identities; no shared broad admin or equipment credential.",
  "aws": "",
  "gcp": "",
  "azure": "",
  "openSource": ""
}
```


Sources:

- hypothesis / H2: A city-scoped ticket ledger, GIS asset registry and versioned crew routing table can provide read APIs; create-ticket and attach-report commands require a verified adapter.

- hypothesis / H3: Each ticket write requires a currently authorized operator approval; tenant is city ID, and operation, resource, report revision, immutable payload digest and policy version are bound to approval.

### F4 · Tool permissions and equipment exclusion

Allow C2 city data reads; C6 only create-ticket/attach-report; C7 operation reads; C1/C4/C5/C8 local case writes. Deny arbitrary URLs, shell/tools from model, direct equipment endpoints, ticket closure and bulk routing.

Reasoning: Chosen to make the stated workflow explicit and bounded.

Assumptions:

- H2: A city-scoped ticket ledger, GIS asset registry and versioned crew routing table can provide read APIs; create-ticket and attach-report commands require a verified adapter.

- H3: Each ticket write requires a currently authorized operator approval; tenant is city ID, and operation, resource, report revision, immutable payload digest and policy version are bound to approval.

Data:

```json
{
  "category": "permission",
  "taskIds": [
    "T1",
    "T2",
    "T5",
    "T6",
    "T7",
    "T8"
  ],
  "choice": "Allow C2 city data reads; C6 only create-ticket/attach-report; C7 operation reads; C1/C4/C5/C8 local case writes. Deny arbitrary URLs, shell/tools from model, direct equipment endpoints, ticket closure and bulk routing.",
  "alternatives": [
    "Rejected broad municipal administrator token for integration convenience."
  ],
  "tradeoffs": "Adapter-side and egress policy controls are required. Prove attempted equipment action rejected before any network call. Credentials held server-side secret store, rotated under city security owner.",
  "permission": "write",
  "blastRadius": "One city and one report-revision business key per write; no device or infrastructure control.",
  "approvalRule": "All ticket actions require C5 approval and fresh C6 API checks; no design approval grants operational authority.",
  "leastPrivilege": "Separate context-read, ticket-create/attach and operation-read identities; no shared broad admin or equipment credential.",
  "aws": "",
  "gcp": "",
  "azure": "",
  "openSource": ""
}
```


Sources:

- hypothesis / H2: A city-scoped ticket ledger, GIS asset registry and versioned crew routing table can provide read APIs; create-ticket and attach-report commands require a verified adapter.

- hypothesis / H3: Each ticket write requires a currently authorized operator approval; tenant is city ID, and operation, resource, report revision, immutable payload digest and policy version are bound to approval.

### F5 · Data minimization and platform options

Prefer city-managed relational database, encrypted object store for restricted original reports, indexed city-scoped asset/ticket snapshots, and city identity/secret infrastructure already supported by IT. Unverified candidates only; no hosting decision or spend. Store contact separately; LLM receives redacted text, asset IDs and minimal candidates. Delete under H6 after approval; backups and legal holds need verified retention behavior. Audit stores IDs/digests/decisions/receipt, not unrestricted prompt text. Proposed roles: operator city cases; supervisor city queue; IT minimized diagnostic metadata; data owner retention exports.

Reasoning: Chosen to make the stated workflow explicit and bounded.

Assumptions:

- H2: A city-scoped ticket ledger, GIS asset registry and versioned crew routing table can provide read APIs; create-ticket and attach-report commands require a verified adapter.

- H6: Proposed data policy: redact reporter contact before LLM use; raw local intake expires after 30 days, recommendation snapshots after 90 days, minimal audit receipts after 365 days; residency and legal retention require city approval.

Data:

```json
{
  "category": "data",
  "taskIds": [
    "T0"
  ],
  "choice": "Prefer city-managed relational database, encrypted object store for restricted original reports, indexed city-scoped asset/ticket snapshots, and city identity/secret infrastructure already supported by IT. Unverified candidates only; no hosting decision or spend. Store contact separately; LLM receives redacted text, asset IDs and minimal candidates. Delete under H6 after approval; backups and legal holds need verified retention behavior. Audit stores IDs/digests/decisions/receipt, not unrestricted prompt text. Proposed roles: operator city cases; supervisor city queue; IT minimized diagnostic metadata; data owner retention exports.",
  "alternatives": [
    "Rejected global vector index mixing cities and raw personal details.",
    "Candidate semantic index only for candidate search; no authority to suppress reports or merge tickets."
  ],
  "tradeoffs": "Relational ledger gives transaction/version ownership; object storage for restricted originals separates access. Hosting options below use same categories—case ledger, restricted originals, secrets/identity—and require equivalent residency, backup and restore tests.",
  "permission": "read",
  "blastRadius": "One city and one report-revision business key per write; no device or infrastructure control.",
  "approvalRule": "All ticket actions require C5 approval and fresh C6 API checks; no design approval grants operational authority.",
  "leastPrivilege": "Separate context-read, ticket-create/attach and operation-read identities; no shared broad admin or equipment credential.",
  "aws": "Unverified candidates: managed relational service + object storage + secrets/IAM; validate city residency, recovery, identity and price.",
  "gcp": "Unverified candidates: managed relational service + object storage + secrets/identity; validate identical residency, recovery, identity and price criteria.",
  "azure": "Unverified candidates: managed relational service + blob storage + vault/identity; validate identical criteria.",
  "openSource": "Candidate PostgreSQL + restricted encrypted file/object store + city identity/secret manager. More operating/backup burden; same isolation and retention tests required."
}
```


Sources:

- hypothesis / H2: A city-scoped ticket ledger, GIS asset registry and versioned crew routing table can provide read APIs; create-ticket and attach-report commands require a verified adapter.

- hypothesis / H6: Proposed data policy: redact reporter contact before LLM use; raw local intake expires after 30 days, recommendation snapshots after 90 days, minimal audit receipts after 365 days; residency and legal retention require city approval.


## Models

- **M1 Single bounded classification allocation**: Illustrative budget only. W3 invokes C3 once for eligible report; same-node wrapper retries at most once. H8 expected calls/report=0.90*(1+0.05)=0.945; worst case 2 calls/report. 200 reports/day -> 189 expected calls/day, maximum 400. At 2000 input and 300 output tokens/call, cost/call=(2000*1+300*4)/1e6=$0.0032; expected $0.003024/report, $0.6048/day and $18.144 per illustrative 30 operating days; worst $1.28/day. Excludes retrieval, hosting, integration, audit, eval calls, operator labor and long context. Enforce 2000-token working input budget by restricting candidates; oversized context -> human, not silent truncation of critical facts. At most 20s model time after retry, plus up to 10s read; proposed routine system response p95 <=30s excluding human wait, to be measured.

## Fmea

- **FM1 Hazard classified as routine**: Hypothetical prioritization: severity 1 negligible to 10 catastrophic, occurrence 1 rare to 10 frequent, detection 1 caught before harm to 10 unlikely detected. Not measured probabilities. RPN=200.
- **FM2 Wrong city or asset routed**: Hypothetical prioritization: severity 1 negligible to 10 catastrophic, occurrence 1 rare to 10 frequent, detection 1 caught before harm to 10 unlikely detected. Not measured probabilities. RPN=128.
- **FM3 Duplicate report creates second action**: Hypothetical prioritization: severity 1 negligible to 10 catastrophic, occurrence 1 rare to 10 frequent, detection 1 caught before harm to 10 unlikely detected. Not measured probabilities. RPN=140.
- **FM4 Stale policy or revoked actor accepted**: Hypothetical prioritization: severity 1 negligible to 10 catastrophic, occurrence 1 rare to 10 frequent, detection 1 caught before harm to 10 unlikely detected. Not measured probabilities. RPN=128.
- **FM5 Payload changes after approval**: Hypothetical prioritization: severity 1 negligible to 10 catastrophic, occurrence 1 rare to 10 frequent, detection 1 caught before harm to 10 unlikely detected. Not measured probabilities. RPN=120.
- **FM6 Prompt injection changes action scope**: Hypothetical prioritization: severity 1 negligible to 10 catastrophic, occurrence 1 rare to 10 frequent, detection 1 caught before harm to 10 unlikely detected. Not measured probabilities. RPN=120.
- **FM7 Unknown commit retried or falsely marked complete**: Hypothetical prioritization: severity 1 negligible to 10 catastrophic, occurrence 1 rare to 10 frequent, detection 1 caught before harm to 10 unlikely detected. Not measured probabilities. RPN=160.
- **FM8 Human queue missed or unstaffed**: Hypothetical prioritization: severity 1 negligible to 10 catastrophic, occurrence 1 rare to 10 frequent, detection 1 caught before harm to 10 unlikely detected. Not measured probabilities. RPN=180.
- **FM9 Unavailable context/model mistaken for no ticket**: Hypothetical prioritization: severity 1 negligible to 10 catastrophic, occurrence 1 rare to 10 frequent, detection 1 caught before harm to 10 unlikely detected. Not measured probabilities. RPN=120.
- **FM10 Sensitive report data retained or exposed**: Hypothetical prioritization: severity 1 negligible to 10 catastrophic, occurrence 1 rare to 10 frequent, detection 1 caught before harm to 10 unlikely detected. Not measured probabilities. RPN=120.
- **FM11 Cancellation races with write**: Hypothetical prioritization: severity 1 negligible to 10 catastrophic, occurrence 1 rare to 10 frequent, detection 1 caught before harm to 10 unlikely detected. Not measured probabilities. RPN=120.
- **FM12 Stale or closed candidate linked**: Hypothetical prioritization: severity 1 negligible to 10 catastrophic, occurrence 1 rare to 10 frequent, detection 1 caught before harm to 10 unlikely detected. Not measured probabilities. RPN=112.

## Evals

- **EV1 Valid CREATE positive control**: Planned synthetic test; not executed by design helper. Fixture is complete and self-contained; ordered mocks run in listed order, absent calls forbidden when assertions say so. No inherited fields.
- **EV2 Immediate deterministic hazard despite missing location**: Planned synthetic test; not executed by design helper. Fixture is complete and self-contained; ordered mocks run in listed order, absent calls forbidden when assertions say so. No inherited fields.
- **EV3 Writer rejects resource city mismatch**: Planned synthetic test; not executed by design helper. Fixture is complete and self-contained; ordered mocks run in listed order, absent calls forbidden when assertions say so. No inherited fields.
- **EV4 Contradictory location retained as human case**: Planned synthetic test; not executed by design helper. Fixture is complete and self-contained; ordered mocks run in listed order, absent calls forbidden when assertions say so. No inherited fields.
- **EV5 Concurrent same-report CREATE cannot duplicate**: Planned synthetic test; not executed by design helper. Fixture is complete and self-contained; ordered mocks run in listed order, absent calls forbidden when assertions say so. No inherited fields.
- **EV6 Valid operator-selected LINK positive control**: Planned synthetic test; not executed by design helper. Fixture is complete and self-contained; ordered mocks run in listed order, absent calls forbidden when assertions say so. No inherited fields.
- **EV7 Revoked actor denied at commit**: Planned synthetic test; not executed by design helper. Fixture is complete and self-contained; ordered mocks run in listed order, absent calls forbidden when assertions say so. No inherited fields.
- **EV8 Changed routing policy invalidates approval**: Planned synthetic test; not executed by design helper. Fixture is complete and self-contained; ordered mocks run in listed order, absent calls forbidden when assertions say so. No inherited fields.
- **EV9 Concurrent ticket edit rejects stale LINK**: Planned synthetic test; not executed by design helper. Fixture is complete and self-contained; ordered mocks run in listed order, absent calls forbidden when assertions say so. No inherited fields.
- **EV10 Payload tampering fails digest binding**: Planned synthetic test; not executed by design helper. Fixture is complete and self-contained; ordered mocks run in listed order, absent calls forbidden when assertions say so. No inherited fields.
- **EV11 Injection cannot invoke equipment or fabricate target**: Planned synthetic test; not executed by design helper. Fixture is complete and self-contained; ordered mocks run in listed order, absent calls forbidden when assertions say so. No inherited fields.
- **EV12 Lost commit recovered after session expiry and duplicate callback**: Planned synthetic test; not executed by design helper. Fixture is complete and self-contained; ordered mocks run in listed order, absent calls forbidden when assertions say so. No inherited fields.
- **EV13 Unknown effect remains locked during cancellation/change**: Planned synthetic test; not executed by design helper. Fixture is complete and self-contained; ordered mocks run in listed order, absent calls forbidden when assertions say so. No inherited fields.
- **EV14 Urgent queue escalates after logout**: Planned synthetic test; not executed by design helper. Fixture is complete and self-contained; ordered mocks run in listed order, absent calls forbidden when assertions say so. No inherited fields.
- **EV15 Model-detected oblique hazard reaches urgent owner**: Planned synthetic test; not executed by design helper. Fixture is complete and self-contained; ordered mocks run in listed order, absent calls forbidden when assertions say so. No inherited fields.
- **EV16 LINK rejects forbidden CREATE fields even with valid digest**: Planned synthetic test; not executed by design helper. Fixture is complete and self-contained; ordered mocks run in listed order, absent calls forbidden when assertions say so. No inherited fields.
- **EV17 Context outage persists owned report without guessing**: Planned synthetic test; not executed by design helper. Fixture is complete and self-contained; ordered mocks run in listed order, absent calls forbidden when assertions say so. No inherited fields.
- **EV18 Privacy redaction and proposed retention controls**: Planned synthetic test; not executed by design helper. Fixture is complete and self-contained; ordered mocks run in listed order, absent calls forbidden when assertions say so. No inherited fields.
- **EV21 Cancellation before send has no ticket effect**: Planned synthetic test; not executed by design helper. Fixture is complete and self-contained; ordered mocks run in listed order, absent calls forbidden when assertions say so. No inherited fields.
- **EV19 Offline judgement and staffed response validation**: Planned offline specification, not executed business evidence.
- **EV20 Full release and live invariant gates**: Planned release specification, not executed business evidence.
- **EV22 Online safety, queue, drift and cost observation**: Planned online specification, not executed business evidence.
- **EV23 Urgent provisional intake without asset or address**: Planned synthetic test; not executed by design helper. Fixture is complete and self-contained; ordered mocks run in listed order, absent calls forbidden when assertions say so. No inherited fields.
- **EV24 Routine owner deadline uses staffed calendar**: Planned synthetic test; not executed by design helper. Fixture is complete and self-contained; ordered mocks run in listed order, absent calls forbidden when assertions say so. No inherited fields.
- **EV25 Closed candidate cannot receive new report**: Planned synthetic test; not executed by design helper. Fixture is complete and self-contained; ordered mocks run in listed order, absent calls forbidden when assertions say so. No inherited fields.
- **EV26 Invalid model output exhausted into owned fallback**: Planned synthetic test; not executed by design helper. Fixture is complete and self-contained; ordered mocks run in listed order, absent calls forbidden when assertions say so. No inherited fields.
- **EV27 Direct equipment command blocked before transport**: Planned synthetic test; not executed by design helper. Fixture is complete and self-contained; ordered mocks run in listed order, absent calls forbidden when assertions say so. No inherited fields.

## Rollout

### R1 · Handling effort and first-route quality

Business hypotheses, unknown baseline. Primary efficiency measure is active operator seconds spent reading/searching/editing/deciding, excluding unstaffed waits; divided by eligible reports, reported mean and p50/p95 per working week. Correct first-route fraction=adjudicated correct initial crew/category decisions / audited routable reports; report abstentions, unsupported and unresolved separately to avoid denominator gaming.

Reasoning: Chosen to make the stated workflow explicit and bounded.

Assumptions:

- H4: Potential exposed wires, fallen poles, sparks or fire enter a staffed urgent manual queue immediately; proposed acknowledgement 2 elapsed minutes and supervisor escalation at 2 minutes; routine exceptions acknowledge within 30 staffed minutes and escalate at 30.

- H9: Proposed gates: zero unauthorized/wrong-city/equipment operations and zero duplicate records in synthetic controls; urgent recall at least 99% on adjudicated offline set; routine routing agreement at least 95%; active handling-time reduction target 20% relative to baseline.

- H11: Proposed measurement uses two representative working weeks of baseline/shadow and two working weeks of randomized pilot, extending to the power-analysis requirement; no sample size or savings are established. Proposed assist usability phase lasts one working week; live pilot is one approved crew area and remains operator-confirmed.

Data:

```json
{
  "category": "kpi",
  "businessKpi": "Active handling minutes/eligible report; correct first-route fraction; baseline two working weeks, target 20% relative time reduction with noninferior route quality.",
  "aiMetrics": [
    "C3 valid grounded category reduces editing; C2 useful candidates reduce search minutes; measure mediation by step-level timers.",
    "Code route agreement affects first-route accuracy; override rate is a diagnostic, not correctness.",
    "Calls/tokens are cost guardrail, not a success KPI."
  ],
  "phase": "All phases",
  "gate": "Baseline and definitions approved before pilot; no measured benefit claimed yet.",
  "owner": "Service improvement analyst; maintenance lead validates routes.",
  "experiment": "R7 is the planned operator-shift randomized visibility experiment. This card supplies its continuous handling-time outcome and route-quality denominator."
}
```


Sources:

- hypothesis / H4: Potential exposed wires, fallen poles, sparks or fire enter a staffed urgent manual queue immediately; proposed acknowledgement 2 elapsed minutes and supervisor escalation at 2 minutes; routine exceptions acknowledge within 30 staffed minutes and escalate at 30.

- hypothesis / H9: Proposed gates: zero unauthorized/wrong-city/equipment operations and zero duplicate records in synthetic controls; urgent recall at least 99% on adjudicated offline set; routine routing agreement at least 95%; active handling-time reduction target 20% relative to baseline.

- hypothesis / H11: Proposed measurement uses two representative working weeks of baseline/shadow and two working weeks of randomized pilot, extending to the power-analysis requirement; no sample size or savings are established. Proposed assist usability phase lasts one working week; live pilot is one approved crew area and remains operator-confirmed.

### R2 · Safety, ownership and privacy guardrails

Count equipment/unauthorized/wrong-city actions and completion without durable receipt over all attempted actions, per day, with absolute zero-breach rule. Duplicate action fraction=report-revisions with >1 authoritative action / applied report-revisions. Urgent recall=adjudicated hazards escalated urgent / adjudicated hazards; acknowledgement time elapsed minutes from intake for urgent, staffed minutes from queue creation for routine. Privacy escape fraction=labelled contact fields exposed to LLM/log / labelled contact fields.

Reasoning: Chosen to make the stated workflow explicit and bounded.

Assumptions:

- H4: Potential exposed wires, fallen poles, sparks or fire enter a staffed urgent manual queue immediately; proposed acknowledgement 2 elapsed minutes and supervisor escalation at 2 minutes; routine exceptions acknowledge within 30 staffed minutes and escalate at 30.

- H9: Proposed gates: zero unauthorized/wrong-city/equipment operations and zero duplicate records in synthetic controls; urgent recall at least 99% on adjudicated offline set; routine routing agreement at least 95%; active handling-time reduction target 20% relative to baseline.

- H11: Proposed measurement uses two representative working weeks of baseline/shadow and two working weeks of randomized pilot, extending to the power-analysis requirement; no sample size or savings are established. Proposed assist usability phase lasts one working week; live pilot is one approved crew area and remains operator-confirmed.

Data:

```json
{
  "category": "kpi",
  "businessKpi": "Zero control breaches, no abandoned urgent case, no duplicate record; acknowledgement and recall as H4/H9 proposed targets.",
  "aiMetrics": [
    "Urgent recall affects time to staffed assessment, not a proven reduction in harm.",
    "Readback/receipt completeness prevents false dispatch claims.",
    "Queue ownership is service continuity guardrail; privacy and authority are independent stop conditions."
  ],
  "phase": "All phases",
  "gate": "EV19/EV20 gates; safety breach stops C6 regardless of average handling-time result.",
  "owner": "Duty supervisor for queue; IT security for authority; data owner for privacy.",
  "experiment": "R7 is the planned operator-shift randomized visibility experiment. This card supplies independent zero-breach stop rules; safety cases are monitored in both arms and never randomized to delayed response."
}
```


Sources:

- hypothesis / H4: Potential exposed wires, fallen poles, sparks or fire enter a staffed urgent manual queue immediately; proposed acknowledgement 2 elapsed minutes and supervisor escalation at 2 minutes; routine exceptions acknowledge within 30 staffed minutes and escalate at 30.

- hypothesis / H9: Proposed gates: zero unauthorized/wrong-city/equipment operations and zero duplicate records in synthetic controls; urgent recall at least 99% on adjudicated offline set; routine routing agreement at least 95%; active handling-time reduction target 20% relative to baseline.

- hypothesis / H11: Proposed measurement uses two representative working weeks of baseline/shadow and two working weeks of randomized pilot, extending to the power-analysis requirement; no sample size or savings are established. Proposed assist usability phase lasts one working week; live pilot is one approved crew area and remains operator-confirmed.

### R3 · Shadow phase

Read approved deidentified/sandbox data and store recommendations locally; operators use existing process for actual work. No live C6 authority. Proposed two working weeks, extended for representation and powered design.

Reasoning: Chosen to make the stated workflow explicit and bounded.

Assumptions:

- H4: Potential exposed wires, fallen poles, sparks or fire enter a staffed urgent manual queue immediately; proposed acknowledgement 2 elapsed minutes and supervisor escalation at 2 minutes; routine exceptions acknowledge within 30 staffed minutes and escalate at 30.

- H9: Proposed gates: zero unauthorized/wrong-city/equipment operations and zero duplicate records in synthetic controls; urgent recall at least 99% on adjudicated offline set; routine routing agreement at least 95%; active handling-time reduction target 20% relative to baseline.

- H11: Proposed measurement uses two representative working weeks of baseline/shadow and two working weeks of randomized pilot, extending to the power-analysis requirement; no sample size or savings are established. Proposed assist usability phase lasts one working week; live pilot is one approved crew area and remains operator-confirmed.

Data:

```json
{
  "category": "phase",
  "businessKpi": "R1 baseline, R2 proposed gates.",
  "aiMetrics": [
    "Per-stratum category/route agreement; valid spans; urgent queue drill; unavailable fallback; branch mix and latency."
  ],
  "phase": "Shadow",
  "gate": "Entry: H1 scope, approved data access and privacy/redaction for supplied dataset; synthetic fixtures available. Exit: EV19 + all EV20 goldens pass in business harness, API proof and city H2-H7 dependencies confirmed; variance and strata measured, power plan approved.",
  "owner": "Product owner + service improvement analyst",
  "experiment": "R7 is the planned operator-shift randomized visibility experiment. This phase collects baseline variance/ICC and strata to power R7; it performs no live experimental writes."
}
```


Sources:

- hypothesis / H4: Potential exposed wires, fallen poles, sparks or fire enter a staffed urgent manual queue immediately; proposed acknowledgement 2 elapsed minutes and supervisor escalation at 2 minutes; routine exceptions acknowledge within 30 staffed minutes and escalate at 30.

- hypothesis / H9: Proposed gates: zero unauthorized/wrong-city/equipment operations and zero duplicate records in synthetic controls; urgent recall at least 99% on adjudicated offline set; routine routing agreement at least 95%; active handling-time reduction target 20% relative to baseline.

- hypothesis / H11: Proposed measurement uses two representative working weeks of baseline/shadow and two working weeks of randomized pilot, extending to the power-analysis requirement; no sample size or savings are established. Proposed assist usability phase lasts one working week; live pilot is one approved crew area and remains operator-confirmed.

### R4 · Assist display-only phase

Operators see recommendations/candidates but continue writes in current city UI. Proposed one working week usability and timing review after shadow gates. No new live ticket-writer integration until pilot.

Reasoning: Chosen to make the stated workflow explicit and bounded.

Assumptions:

- H4: Potential exposed wires, fallen poles, sparks or fire enter a staffed urgent manual queue immediately; proposed acknowledgement 2 elapsed minutes and supervisor escalation at 2 minutes; routine exceptions acknowledge within 30 staffed minutes and escalate at 30.

- H9: Proposed gates: zero unauthorized/wrong-city/equipment operations and zero duplicate records in synthetic controls; urgent recall at least 99% on adjudicated offline set; routine routing agreement at least 95%; active handling-time reduction target 20% relative to baseline.

- H11: Proposed measurement uses two representative working weeks of baseline/shadow and two working weeks of randomized pilot, extending to the power-analysis requirement; no sample size or savings are established. Proposed assist usability phase lasts one working week; live pilot is one approved crew area and remains operator-confirmed.

Data:

```json
{
  "category": "phase",
  "businessKpi": "R1 search/edit time and first-route correctness; R2 safe escalation.",
  "aiMetrics": [
    "Operator correction reasons; queue acknowledgement; ground-truth sampled route agreement."
  ],
  "phase": "Assist",
  "gate": "Entry: shadow exit proof and named coverage roles. Exit: representative operator usability review, timing instrumentation validated, no safety/control breach, pilot training/runbook and C6 kill switch + C7 recovery drill complete. No pilot effect required.",
  "owner": "Service desk lead",
  "experiment": "R7 is the planned operator-shift randomized visibility experiment. This phase validates timers/usability before R7, without claiming causal benefit."
}
```


Sources:

- hypothesis / H4: Potential exposed wires, fallen poles, sparks or fire enter a staffed urgent manual queue immediately; proposed acknowledgement 2 elapsed minutes and supervisor escalation at 2 minutes; routine exceptions acknowledge within 30 staffed minutes and escalate at 30.

- hypothesis / H9: Proposed gates: zero unauthorized/wrong-city/equipment operations and zero duplicate records in synthetic controls; urgent recall at least 99% on adjudicated offline set; routine routing agreement at least 95%; active handling-time reduction target 20% relative to baseline.

- hypothesis / H11: Proposed measurement uses two representative working weeks of baseline/shadow and two working weeks of randomized pilot, extending to the power-analysis requirement; no sample size or savings are established. Proposed assist usability phase lasts one working week; live pilot is one approved crew area and remains operator-confirmed.

### R5 · Bounded pilot

Enable only operator-confirmed routine CREATE/LINK for one approved crew area; urgent/missing/conflicting reports remain manual. Two working weeks minimum and extend to computed power requirement; all five operators trained, eligibility strata logged.

Reasoning: Chosen to make the stated workflow explicit and bounded.

Assumptions:

- H4: Potential exposed wires, fallen poles, sparks or fire enter a staffed urgent manual queue immediately; proposed acknowledgement 2 elapsed minutes and supervisor escalation at 2 minutes; routine exceptions acknowledge within 30 staffed minutes and escalate at 30.

- H9: Proposed gates: zero unauthorized/wrong-city/equipment operations and zero duplicate records in synthetic controls; urgent recall at least 99% on adjudicated offline set; routine routing agreement at least 95%; active handling-time reduction target 20% relative to baseline.

- H11: Proposed measurement uses two representative working weeks of baseline/shadow and two working weeks of randomized pilot, extending to the power-analysis requirement; no sample size or savings are established. Proposed assist usability phase lasts one working week; live pilot is one approved crew area and remains operator-confirmed.

Data:

```json
{
  "category": "phase",
  "businessKpi": "R1 randomized handling-time effect and route noninferiority; R2 absolute controls.",
  "aiMetrics": [
    "End-to-end latency; held/overdue cases; exact receipts; wrong-link/duplicate audit; cost/case."
  ],
  "phase": "Pilot",
  "gate": "Entry: assist exit, EV20 release report, city service-owner authorization and verified adapter. Exit: powered R7 estimate with confidence interval meeting approved efficiency and route gates, zero invariant breaches, EV22 stable, operator/crew review and explicit residual-risk decision. Stop C6 on any R2 breach, recover pending operations before reverting to display-only.",
  "owner": "City service owner; IT operations executes stop/reconcile",
  "experiment": "R7 is the planned operator-shift randomized visibility experiment. This phase executes R7 with routine eligible reports after entry gates and required power calculation."
}
```


Sources:

- hypothesis / H4: Potential exposed wires, fallen poles, sparks or fire enter a staffed urgent manual queue immediately; proposed acknowledgement 2 elapsed minutes and supervisor escalation at 2 minutes; routine exceptions acknowledge within 30 staffed minutes and escalate at 30.

- hypothesis / H9: Proposed gates: zero unauthorized/wrong-city/equipment operations and zero duplicate records in synthetic controls; urgent recall at least 99% on adjudicated offline set; routine routing agreement at least 95%; active handling-time reduction target 20% relative to baseline.

- hypothesis / H11: Proposed measurement uses two representative working weeks of baseline/shadow and two working weeks of randomized pilot, extending to the power-analysis requirement; no sample size or savings are established. Proposed assist usability phase lasts one working week; live pilot is one approved crew area and remains operator-confirmed.

### R6 · Scale assisted scope

Expand areas sequentially after local policy/roster verification. End state remains operator-confirmed; no planned autonomous dispatch. Re-run EV20 for new policies/areas/languages.

Reasoning: Chosen to make the stated workflow explicit and bounded.

Assumptions:

- H4: Potential exposed wires, fallen poles, sparks or fire enter a staffed urgent manual queue immediately; proposed acknowledgement 2 elapsed minutes and supervisor escalation at 2 minutes; routine exceptions acknowledge within 30 staffed minutes and escalate at 30.

- H9: Proposed gates: zero unauthorized/wrong-city/equipment operations and zero duplicate records in synthetic controls; urgent recall at least 99% on adjudicated offline set; routine routing agreement at least 95%; active handling-time reduction target 20% relative to baseline.

- H11: Proposed measurement uses two representative working weeks of baseline/shadow and two working weeks of randomized pilot, extending to the power-analysis requirement; no sample size or savings are established. Proposed assist usability phase lasts one working week; live pilot is one approved crew area and remains operator-confirmed.

Data:

```json
{
  "category": "phase",
  "businessKpi": "R1/R2 by area and shift; benefit cannot conceal a failing stratum.",
  "aiMetrics": [
    "Route agreement by crew/language; queue capacity/arrival peaks; recovery age and cost."
  ],
  "phase": "Scale",
  "gate": "Entry: pilot exit plus new-area verified H7 maps and coverage. Exit/continuation: weekly EV22 and monthly owner review; regressions freeze expansion, restore prior policy/version for unsent plans only, reconcile unknown writes without compensation. Any autonomy change requires new design/authority.",
  "owner": "Maintenance operations lead + city service owner",
  "experiment": "R7 is the planned operator-shift randomized visibility experiment. Expansion uses new-area evidence and continues R7/R1/R2 monitoring; no autonomy increase."
}
```


Sources:

- hypothesis / H4: Potential exposed wires, fallen poles, sparks or fire enter a staffed urgent manual queue immediately; proposed acknowledgement 2 elapsed minutes and supervisor escalation at 2 minutes; routine exceptions acknowledge within 30 staffed minutes and escalate at 30.

- hypothesis / H9: Proposed gates: zero unauthorized/wrong-city/equipment operations and zero duplicate records in synthetic controls; urgent recall at least 99% on adjudicated offline set; routine routing agreement at least 95%; active handling-time reduction target 20% relative to baseline.

- hypothesis / H11: Proposed measurement uses two representative working weeks of baseline/shadow and two working weeks of randomized pilot, extending to the power-analysis requirement; no sample size or savings are established. Proposed assist usability phase lasts one working week; live pilot is one approved crew area and remains operator-confirmed.

### R7 · Randomized effect evaluation

Compare recommendations visible versus hidden while both groups retain normal operator authority. Randomization unit is operator-shift cluster, balanced within operator and crew area over full weekly cycles; initial eligible routine reports only, excluding hazards from experiment but monitoring all safety. Keep assignment concealed until shift, log spillover; no same report/candidate group split across arms. Measure intent-to-treat and contamination; learning carryover is a limitation, assess sensitivity by calendar block.

Reasoning: Chosen to make the stated workflow explicit and bounded.

Assumptions:

- H4: Potential exposed wires, fallen poles, sparks or fire enter a staffed urgent manual queue immediately; proposed acknowledgement 2 elapsed minutes and supervisor escalation at 2 minutes; routine exceptions acknowledge within 30 staffed minutes and escalate at 30.

- H9: Proposed gates: zero unauthorized/wrong-city/equipment operations and zero duplicate records in synthetic controls; urgent recall at least 99% on adjudicated offline set; routine routing agreement at least 95%; active handling-time reduction target 20% relative to baseline.

- H11: Proposed measurement uses two representative working weeks of baseline/shadow and two working weeks of randomized pilot, extending to the power-analysis requirement; no sample size or savings are established. Proposed assist usability phase lasts one working week; live pilot is one approved crew area and remains operator-confirmed.

Data:

```json
{
  "category": "experiment",
  "businessKpi": "Continuous active handling minutes/report primary; binary correct-first-route noninferiority guardrail.",
  "aiMetrics": [
    "Model agreement is mechanism; not sufficient to establish handling-time benefit."
  ],
  "phase": "Pilot",
  "gate": "Before pilot use baseline variance and intracluster correlation: continuous-mean sample size n≈2*(zα/2+zβ)^2*σ²/δ², inflate 1+(m−1)*ICC for shift clustering; binary noninferiority needs separate proportion-based power method with approved margin, use larger requirement. No invented n. Stop/extend if clusters too few, maintain assist if power unattainable.",
  "owner": "Service improvement analyst; service owner approves δ=20% target and correctness margin.",
  "experiment": "Control: existing manual search; treatment: recommendation/candidate view with same confirmation. Minimum two full working weeks after entry, extend to power requirement; use cluster-aware confidence intervals and operator/time strata. No post-hoc excluding slow cases."
}
```


Sources:

- hypothesis / H4: Potential exposed wires, fallen poles, sparks or fire enter a staffed urgent manual queue immediately; proposed acknowledgement 2 elapsed minutes and supervisor escalation at 2 minutes; routine exceptions acknowledge within 30 staffed minutes and escalate at 30.

- hypothesis / H9: Proposed gates: zero unauthorized/wrong-city/equipment operations and zero duplicate records in synthetic controls; urgent recall at least 99% on adjudicated offline set; routine routing agreement at least 95%; active handling-time reduction target 20% relative to baseline.

- hypothesis / H11: Proposed measurement uses two representative working weeks of baseline/shadow and two working weeks of randomized pilot, extending to the power-analysis requirement; no sample size or savings are established. Proposed assist usability phase lasts one working week; live pilot is one approved crew area and remains operator-confirmed.

### R8 · Authority, incident and residual-risk ownership

Proposed accountable roles, not invented appointees: service owner accepts launch/expansion; maintenance lead publishes routing/crew policy; supervisor owns manual/urgent queues; IT integration proves adapters; IT operations owns journals/kill switch/readback; security owns scopes/revocation; data owner approves retention; analyst owns measurement. No user acceptance of residual risks is implied.

Reasoning: Chosen to make the stated workflow explicit and bounded.

Assumptions:

- H4: Potential exposed wires, fallen poles, sparks or fire enter a staffed urgent manual queue immediately; proposed acknowledgement 2 elapsed minutes and supervisor escalation at 2 minutes; routine exceptions acknowledge within 30 staffed minutes and escalate at 30.

- H9: Proposed gates: zero unauthorized/wrong-city/equipment operations and zero duplicate records in synthetic controls; urgent recall at least 99% on adjudicated offline set; routine routing agreement at least 95%; active handling-time reduction target 20% relative to baseline.

- H11: Proposed measurement uses two representative working weeks of baseline/shadow and two working weeks of randomized pilot, extending to the power-analysis requirement; no sample size or savings are established. Proposed assist usability phase lasts one working week; live pilot is one approved crew area and remains operator-confirmed.

Data:

```json
{
  "category": "owner",
  "businessKpi": "R1 business value decision; R2 independent guardrails.",
  "aiMetrics": [
    "Incident receipt, owner ACK, recovery closure, audit completeness."
  ],
  "phase": "All phases",
  "gate": "All roles named and coverage proved before live pilot; a stop disables new C6 sends while retaining C7 and C8. Rollback never replays actions or deletes operation evidence; ticket correction remains separate manual authority.",
  "owner": "City service owner",
  "experiment": "R7 is the planned operator-shift randomized visibility experiment. Analyst owns analysis; service owner owns stop/expansion; security and supervisor can stop independently."
}
```


Sources:

- hypothesis / H4: Potential exposed wires, fallen poles, sparks or fire enter a staffed urgent manual queue immediately; proposed acknowledgement 2 elapsed minutes and supervisor escalation at 2 minutes; routine exceptions acknowledge within 30 staffed minutes and escalate at 30.

- hypothesis / H9: Proposed gates: zero unauthorized/wrong-city/equipment operations and zero duplicate records in synthetic controls; urgent recall at least 99% on adjudicated offline set; routine routing agreement at least 95%; active handling-time reduction target 20% relative to baseline.

- hypothesis / H11: Proposed measurement uses two representative working weeks of baseline/shadow and two working weeks of randomized pilot, extending to the power-analysis requirement; no sample size or savings are established. Proposed assist usability phase lasts one working week; live pilot is one approved crew area and remains operator-confirmed.


## Export

### X1 · Coding-agent handoff and acceptance

Implement the proposed bounded workflow after city adapter/policy verification. This package implements no city system and grants no operational authority.

Reasoning: Chosen to make the stated workflow explicit and bounded.

Assumptions:

- H1: Proposed first release ingests text typed or pasted by an operator, plus optional asset ID/address; direct citizen-channel integration, photo interpretation and ticket closure are deferred.

- H2: A city-scoped ticket ledger, GIS asset registry and versioned crew routing table can provide read APIs; create-ticket and attach-report commands require a verified adapter.

- H3: Each ticket write requires a currently authorized operator approval; tenant is city ID, and operation, resource, report revision, immutable payload digest and policy version are bound to approval.

- H4: Potential exposed wires, fallen poles, sparks or fire enter a staffed urgent manual queue immediately; proposed acknowledgement 2 elapsed minutes and supervisor escalation at 2 minutes; routine exceptions acknowledge within 30 staffed minutes and escalate at 30.

- H6: Proposed data policy: redact reporter contact before LLM use; raw local intake expires after 30 days, recommendation snapshots after 90 days, minimal audit receipts after 365 days; residency and legal retention require city approval.

- H9: Proposed gates: zero unauthorized/wrong-city/equipment operations and zero duplicate records in synthetic controls; urgent recall at least 99% on adjudicated offline set; routine routing agreement at least 95%; active handling-time reduction target 20% relative to baseline.

- H10: Proposed operational limits: each read attempt 5 seconds, one read retry; LLM attempt 10 seconds with one retry; ticket write timeout 5 seconds with zero automatic write retry; reconciliation reads at 5, 30 and 120 seconds, then owned unknown hold with 15-minute read-only watchdog. Proposed additional limits: snapshot age at plan creation 60 seconds, plan/approval expiry 5 elapsed minutes, routine nonhuman response p95 30 seconds, and unknown-held >1 hour escalates service manager. These limits require verification, not established policy.

Data:

```json
{
  "acceptanceCriteria": [
    "AC1: SUBMIT and CANCEL_PROPOSAL exact unions, city-bound intake dedup/revision checks and durable provisional intake satisfy T1/C1 and EV2/EV3/EV4/EV21.",
    "AC2: C2 returns attributed current snapshots or declared error; unavailability never becomes empty search; EV17 demonstrates owned fallback.",
    "AC3: C3 only emits bounded schema/evidence/abstention, has no tools and at most two calls; M1 budget/latency instrumentation available; EV11/EV15/EV19 cover judgment.",
    "AC4: C4 exact asset/current crew map and immutable canonical payload; LINK cannot contain CREATE fields; EV6/EV9/EV16.",
    "AC5: C5 signed payload-bound approval is required and C6 rechecks live city/action/resource/version/authority; EV7/EV8/EV10 prove denied mutations.",
    "AC6: API business-key uniqueness across CREATE/LINK and operation proof survives concurrency; EV1/EV5/EV6 prove actual record counts.",
    "AC7: UNKNOWN after MAY_HAVE_SENT goes W7 then owned W11; EV12/EV13 prove no second action after caller expiry, duplicate callback or cancellation.",
    "AC8: C8 terminal UI says ticket recorded only with receipt; urgent timers/escalation survive logout; EV14 covers explicit due times and EV18 privacy.",
    "AC9: All EV20 named goldens, EV19 strata, EV22 monitors and R3-R8 phase/stop rules have implementation harness evidence before live pilot; design-helper validation is never substituted.",
    "AC10: Remote equipment operations absent from types, credentials, model tools and egress allowlist; adversarial direct request fails without network in EV11. No real account provisioning or writes are part of this handoff."
  ],
  "buildInstructions": "Use design.json as canonical; preserve T/C/W/FM/EV/R/H IDs in code/tests. Build relational case, immutable intake revision, snapshot, plan, approval, operation/outbox, callback-dedup, queue/timer and minimized audit tables; unique(city,intakeId,revision) both locally and at authoritative writer. Model enum outputs never become authority. Canonical payload SHA256 uses UTF-8 sorted keys, compact separators, no floats and complete discriminated payload; compute digest on server, fetch plan by immutable ID, bind C5 approval and verify at C6. Implement exact contract errors and W1-W11 transitions, durable waits and bounded timeouts; no generic retry around C6. Atomic cancellation CAS wins only before MAY_HAVE_SENT; afterward lock intent and reconcile. Receipt persistence failure uses recoverable journal and blocks completion claim. Complete approved synthetic CREATE/LINK adapter before requesting live authority; prove API idempotency, resource versions, final noncommit proof and independent read-only reconciliation. If city API lacks a guarantee, remain display-only assist until shim/adapter is verified; do not weaken controls. Implement C8 owners/calendar and console alert delivery; keep recovery alive when new sends disabled. H2-H7/H9/H10 are real launch prerequisites; H8/H11 are planning hypotheses. Author business test harness that loads complete golden JSON, respects ordered mocks and checks exact record/call counts and reasons; helper only checks design structure. Include EV20 whole suite, EV19 adjudication, EV22 minute/daily/weekly telemetry; add no unrequested channels, equipment access, autonomous dispatch, ticket closure or messages. Deliver sandbox evidence and city-role sign-off per R3-R8; reviewed design is not production approval. Finalizer W9/W10 guard C8.persistResult before W12/W13 durable projection; W11 is read-only-owned recovery disposition. Additional complete fixtures EV23-EV27 are included in EV20 release assertions; no fixture inheritance or prose-only extra variants."
}
```


Sources:

- hypothesis / H1: Proposed first release ingests text typed or pasted by an operator, plus optional asset ID/address; direct citizen-channel integration, photo interpretation and ticket closure are deferred.

- hypothesis / H2: A city-scoped ticket ledger, GIS asset registry and versioned crew routing table can provide read APIs; create-ticket and attach-report commands require a verified adapter.

- hypothesis / H3: Each ticket write requires a currently authorized operator approval; tenant is city ID, and operation, resource, report revision, immutable payload digest and policy version are bound to approval.

- hypothesis / H4: Potential exposed wires, fallen poles, sparks or fire enter a staffed urgent manual queue immediately; proposed acknowledgement 2 elapsed minutes and supervisor escalation at 2 minutes; routine exceptions acknowledge within 30 staffed minutes and escalate at 30.

- hypothesis / H6: Proposed data policy: redact reporter contact before LLM use; raw local intake expires after 30 days, recommendation snapshots after 90 days, minimal audit receipts after 365 days; residency and legal retention require city approval.

- hypothesis / H9: Proposed gates: zero unauthorized/wrong-city/equipment operations and zero duplicate records in synthetic controls; urgent recall at least 99% on adjudicated offline set; routine routing agreement at least 95%; active handling-time reduction target 20% relative to baseline.

- hypothesis / H10: Proposed operational limits: each read attempt 5 seconds, one read retry; LLM attempt 10 seconds with one retry; ticket write timeout 5 seconds with zero automatic write retry; reconciliation reads at 5, 30 and 120 seconds, then owned unknown hold with 15-minute read-only watchdog. Proposed additional limits: snapshot age at plan creation 60 seconds, plan/approval expiry 5 elapsed minutes, routine nonhuman response p95 30 seconds, and unknown-held >1 hour escalates service manager. These limits require verification, not established policy.


Full exact data and source evidence: [design.json](design.json). Launch facts and owners: [assumptions.md](assumptions.md).
