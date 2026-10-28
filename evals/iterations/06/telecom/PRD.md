# Telecom complaint and service credit assistant

> PASS | DESIGN ONLY. independent-agent; round 2.

## Original brief

Design a complaint assistant for a telecom provider. Customers report network outages, poor speed and billing errors. The assistant should investigate using account, billing and service records, explain findings and resolve eligible service credits. Larger or unclear refunds need a human supervisor and may wait up to 48 hours. Keep customers informed, avoid duplicate refunds and use only the right customer's active service connection. Propose any missing policies as assumptions, not real company rules.


## Context

- **CTX1 Decision and boundary**: A verified customer opens a complaint in an authenticated portal. Investigate outages, poor speed and billing errors. Automatically post only eligible service credits. Supervisors decide larger or unclear credits; external cash refunds, service changes, outage repair and disputed invoice correction remain owned manual work.
- **CTX2 End conditions and value**: Success is an evidence-linked explanation plus proven credit or explicit no-credit decision. Missing records, authentication failure, denial, cancellation, overdue and unknown posting remain distinct owned outcomes. Never label pending money as resolved.
- **CTX3 Evidence limits**: This is a proposed design with synthetic fixtures. No company policy, adapter behavior, staffing, savings or regulatory compliance has been verified. H1-H4 block live launch.

## Tasks

- **T0 Resolve the complaint**: Run T1 then T2 then choose T3 outcome then T4 closure.
- **T1 Check customer and connection**: Authenticate tenant/customer, explicitly select one active connection; never default across multiple services.
- **T2 Investigate and explain**: Read account, bills, service incidents; show cited findings or missing/conflicting evidence.
- **T3 Choose a credit route**: Code partitions: eligible under cap; larger/unclear; proved no-credit. Missing data uses larger/unclear route.
- **T3.1 Post an eligible service credit**: Code policy or exact signed supervisor approval plus fresh checks authorizes one credit.
- **T3.2 Handle supervisor review**: Queue, acknowledgement, 24h update and 48h decision or overdue ownership; deny/cancel prevents new money.
- **T3.3 Explain a no-credit result**: A proved zero entitlement or unsupported external refund becomes an explained decision/manual handoff.
- **T4 Prove outcome and retain ownership**: Verify posting or durable case proof; unknown posts retain owner and frozen event key.
- **A1 Customer and selected active connection**: Authenticated identity gateway and service registry; tenantId, customerId, connectionId, active flag, connectionVersion, authRevocationVersion.
- **A2 Evidence and policy**: Versioned billing invoices, incident telemetry, complaint and approved policy store; observedAt, period start/end UTC, timezone, paid recurring amount, currency, overlap/event IDs.
- **A3 Financial and approval state**: Authoritative credit ledger businessEventKey, operationId, postingId; immutable approval planId/version and approver identity; durable queue/timer events.

## Components

- **C1 Authenticate and select**: Verify ownership before any private records; active-service lookup uses authorized scope. No inferred identity. Read existing internal Case by server execution key first, independently of private telecom data. caseRecordId is a direct projection of the stored primary key only on authoritative FOUND. MISSING/UNAVAILABLE supplies no proof and pauses durable recovery with Support Operations; no fabricated case ID. With multiple active owned connections and no explicit selection return SELECTION_REQUIRED and masked service labels, never default to first. Show a clarification to choose one connection; keep the case awaiting customer selection. Explicit choice resumes W1 on the same case. No billing/incident read or credit until selection is revalidated.
- **C2 Read complaint evidence**: GET scoped account, invoice and incident records; 5s timeout, one retry; return UNAVAILABLE after retry. All observations carry source IDs and observedAt.
- **C3 Explain supported findings**: No tool access. Treat text/record instructions as data. No amount/date/identity fields. One schema retry then deterministic cited template. Output validator rejects unsupported citations and claims of completed credit.
- **C4 Calculate and route**: Integer arithmetic, UTC interval intersection, policy limits and account ledger determine amount. CreditPlan holds tenant/customer/connection/connectionVersion/authVersion, invoiceId/version, invoiceEntitlementVersion, incidentId, eventKey, periodStart/end, outageSeconds, amountMinor, currency, taxTreatment, accountingCode, policyVersion, evidenceVersions, expiresAt, planVersion. eventKey derives from tenant/connection/invoice/incident/creditKind; DB uniqueness blocks cross-case semantic duplicates. Missing/conflicting facts route HUMAN; zero eligibility NO_CREDIT. Invoice entitlement remaining balance is an atomic commit constraint across distinct incident event keys. C7 pins invoice-entitlement version; C8 locks/checks it and consumes amount in the same transaction as credit posting. A stale balance rejects the whole command, never silently changes approved amount. C4 may build a new zero-credit outcome after refetch.
- **C5 Wait for supervisor decision**: Proposed queue complaint-supervisor; Support Operations owns; acknowledgement within 1h, duty-manager escalation if absent. Decision by elapsed 48h UTC from enqueue. Approval event covers immutable full plan; supervisor must resolve missing evidence in verified systems before a new plan exists. No arbitrary amount in an approval callback. Deduplicate eventId; order by queueVersion; expired/revoked/superseded events ignored.
- **C6 Publish portal progress**: Materialize notice in the same internal workflow transaction; authenticated case-status GET returns it. No SMS/email connector. ENTRY and H24 notices once each, H48 overdue in final pending view. Portal failure retains notice and duty manager owns recovery; never loses timer or decision.
- **C7 Recheck posting authority**: Re-fetch active connection/ownership, policy and invoice versions, remaining entitlement and eventKey immediately before reservation/post. Lock event key and compare plan/approval versions/expiry. Code reconstructs every financial field from authoritative evidence; changed plan requires a new approval. API must recheck versions atomically at commit or H2 fails. Invoice entitlement remaining balance is an atomic commit constraint across distinct incident event keys. C7 pins invoice-entitlement version; C8 locks/checks it and consumes amount in the same transaction as credit posting. A stale balance rejects the whole command, never silently changes approved amount. C4 may build a new zero-credit outcome after refetch. CreditPlan.invoiceEntitlementVersion:uint is required and bound by policy or exact supervisor approval; backend checks it atomically against invoice entitlement row.
- **C8 Post one service credit**: POST service-credit resource with exact trusted plan, operationId and eventKey. 5s timeout; no internal retry. Backend atomic unique event key and preconditions required. POSTED means durable ledger receipt, not HTTP 200 alone. All rejects imply zero new posting; ambiguous responses use UNKNOWN_COMMIT. Project postingId directly only after a nonempty authoritative committed record is verified. TIMEOUT, UNKNOWN_COMMIT, UNRESOLVED, rejection and malformed success never carry postingId. Normalize malformed POSTED to UNKNOWN_COMMIT before workflow routing. Invoice entitlement remaining balance is an atomic commit constraint across distinct incident event keys. C7 pins invoice-entitlement version; C8 locks/checks it and consumes amount in the same transaction as credit posting. A stale balance rejects the whole command, never silently changes approved amount. C4 may build a new zero-credit outcome after refetch. CreditPlan.invoiceEntitlementVersion:uint is required and bound by policy or exact supervisor approval; backend checks it atomically against invoice entitlement row.
- **C9 Reconcile uncertain posting**: Read authoritative operation ledger by operationId and eventKey under durable service identity. Query at 5s, 30s and 120s max; COMMITTED verifies receipt, DEFINITIVELY_ABSENT requires final provider guarantee and can re-enter C7 once with same key/operation. Otherwise freeze event key as pending reconciliation for Billing Operations; hourly read-only checks for 24h then duty-manager ownership. Never expire reservation into another writer. Project postingId directly only after a nonempty authoritative committed record is verified. TIMEOUT, UNKNOWN_COMMIT, UNRESOLVED, rejection and malformed success never carry postingId. Normalize malformed POSTED to UNKNOWN_COMMIT before workflow routing.
- **C10 Verify outcome proof**: Deterministically reject missing/empty postingId and any uncommitted result. Read authoritative receipt and match tenant/customer/connection/eventKey/operation/planVersion/amount/currency to the exact authorized plan and persisted Case. PROVEN_CREDIT only if committed receipt and direct postingId agree. No timeout supplies proof; mismatch keeps money pending with Billing Operations.
- **C11 Verify existing case proof**: Reject missing/empty caseRecordId. Read authoritative internal Case row under server execution key and verify its primary key equals C1.caseRecordId, owner/status exist, and authenticated views match customer scope. Missing/unavailable record pauses durable recovery; never claim a case is closed or money posted. PROVEN_CASE can show a no-credit outcome or owned pending state, never CREDIT_CONFIRMED.

## Workflow

- **W1 Check active connection**: {"state": "Persisted CaseState: caseId, tenant scope if authenticated, owner, stateVersion, enqueueAt UTC, noticeMask, retryCount, cancellation flag, eventKey lock, operationId and receipt. Predicate values are typed outputs of the C component in this node; retryCount:uint starts 0 and increments only on W10\u2192W8, cancelled:bool from authenticated case cancellation event; timers from durable UTC scheduler. Cancellation > decision > notice precedence. Durable caseId is allocated before W1; no financial effect.  C1 caseLookup MISSING/UNAVAILABLE pauses the durable case runner for owned storage recovery; it has no executable edge to a completion or business writer. Billing/service reads require explicit active selection. SELECTION_REQUIRED shows masked active-service choices in the owned case view and awaits customer resumption at W1.", "transitions": [{"to": "W2", "when": "C1.caseLookup == FOUND and C1.status == OK", "mode": "exclusive"}, {"to": "W12", "when": "C1.caseLookup == FOUND and C1.status != OK", "mode": "exclusive"}], "failureDisposition": "Persist owned pending case; no blind financial retry; recovery owner Billing Operations for money and Support Operations otherwise.", "timeout": "48 elapsed hours for W6; model 10s per attempt max2; reads 5s max2; C8 5s max1; reconciliation initial 120s window.", "retryPolicy": "Only model/read schema retries once; writer retry only W10 authoritative absent then W8 once. Notice sequence max2; scheduler never resets 48h clock.", "terminalDisposition": ""}
- **W2 Read service and billing records**: {"state": "Persisted CaseState: caseId, tenant scope if authenticated, owner, stateVersion, enqueueAt UTC, noticeMask, retryCount, cancellation flag, eventKey lock, operationId and receipt. Predicate values are typed outputs of the C component in this node; retryCount:uint starts 0 and increments only on W10\u2192W8, cancelled:bool from authenticated case cancellation event; timers from durable UTC scheduler. Cancellation > decision > notice precedence. Durable caseId is allocated before W1; no financial effect. ", "transitions": [{"to": "W3", "when": "C2.status == COMPLETE", "mode": "exclusive"}, {"to": "W6", "when": "C2.status in {MISSING,CONFLICT,UNAVAILABLE}", "mode": "exclusive"}], "failureDisposition": "Persist owned pending case; no blind financial retry; recovery owner Billing Operations for money and Support Operations otherwise.", "timeout": "48 elapsed hours for W6; model 10s per attempt max2; reads 5s max2; C8 5s max1; reconciliation initial 120s window.", "retryPolicy": "Only model/read schema retries once; writer retry only W10 authoritative absent then W8 once. Notice sequence max2; scheduler never resets 48h clock.", "terminalDisposition": ""}
- **W3 Draft a cited explanation**: {"state": "Persisted CaseState: caseId, tenant scope if authenticated, owner, stateVersion, enqueueAt UTC, noticeMask, retryCount, cancellation flag, eventKey lock, operationId and receipt. Predicate values are typed outputs of the C component in this node; retryCount:uint starts 0 and increments only on W10\u2192W8, cancelled:bool from authenticated case cancellation event; timers from durable UTC scheduler. Cancellation > decision > notice precedence. Durable caseId is allocated before W1; no financial effect. ", "transitions": [{"to": "W4", "when": "explanation schema accepted or deterministic fallback used", "mode": "exclusive"}], "failureDisposition": "Persist owned pending case; no blind financial retry; recovery owner Billing Operations for money and Support Operations otherwise.", "timeout": "48 elapsed hours for W6; model 10s per attempt max2; reads 5s max2; C8 5s max1; reconciliation initial 120s window.", "retryPolicy": "Only model/read schema retries once; writer retry only W10 authoritative absent then W8 once. Notice sequence max2; scheduler never resets 48h clock.", "terminalDisposition": ""}
- **W4 Choose the policy route**: {"state": "Persisted CaseState: caseId, tenant scope if authenticated, owner, stateVersion, enqueueAt UTC, noticeMask, retryCount, cancellation flag, eventKey lock, operationId and receipt. Predicate values are typed outputs of the C component in this node; retryCount:uint starts 0 and increments only on W10\u2192W8, cancelled:bool from authenticated case cancellation event; timers from durable UTC scheduler. Cancellation > decision > notice precedence. Durable caseId is allocated before W1; no financial effect. ", "transitions": [{"to": "W8", "when": "C4.route == AUTO", "mode": "exclusive"}, {"to": "W6", "when": "C4.route == HUMAN", "mode": "exclusive"}, {"to": "W12", "when": "C4.route == NO_CREDIT", "mode": "exclusive"}], "failureDisposition": "Persist owned pending case; no blind financial retry; recovery owner Billing Operations for money and Support Operations otherwise.", "timeout": "48 elapsed hours for W6; model 10s per attempt max2; reads 5s max2; C8 5s max1; reconciliation initial 120s window.", "retryPolicy": "Only model/read schema retries once; writer retry only W10 authoritative absent then W8 once. Notice sequence max2; scheduler never resets 48h clock.", "terminalDisposition": ""}
- **W6 Wait up to 48 hours**: {"state": "Persisted CaseState: caseId, tenant scope if authenticated, owner, stateVersion, enqueueAt UTC, noticeMask, retryCount, cancellation flag, eventKey lock, operationId and receipt. Predicate values are typed outputs of the C component in this node; retryCount:uint starts 0 and increments only on W10\u2192W8, cancelled:bool from authenticated case cancellation event; timers from durable UTC scheduler. Cancellation > decision > notice precedence. Durable caseId is allocated before W1; no financial effect. While PENDING with noticeDue NONE, scheduler waits without an active self-edge; ENTRY/H24 fire once; at enqueueAt+48h OVERDUE wins. Acknowledge deadline is enqueueAt+1h. After 48h retain supervisor ownership; late approval cannot auto-post.", "transitions": [{"to": "W7", "when": "C5.decision == PENDING and C5.noticeDue in {ENTRY,H24}", "mode": "exclusive"}, {"to": "W8", "when": "C5.decision == APPROVED", "mode": "exclusive"}, {"to": "W12", "when": "C5.decision in {DENIED,CANCELLED}", "mode": "exclusive"}, {"to": "W12", "when": "C5.decision == OVERDUE", "mode": "exclusive"}], "failureDisposition": "Persist owned pending case; no blind financial retry; recovery owner Billing Operations for money and Support Operations otherwise.", "timeout": "48 elapsed hours for W6; model 10s per attempt max2; reads 5s max2; C8 5s max1; reconciliation initial 120s window.", "retryPolicy": "Only model/read schema retries once; writer retry only W10 authoritative absent then W8 once. Notice sequence max2; scheduler never resets 48h clock.", "terminalDisposition": ""}
- **W7 Show wait progress**: {"state": "Persisted CaseState: caseId, tenant scope if authenticated, owner, stateVersion, enqueueAt UTC, noticeMask, retryCount, cancellation flag, eventKey lock, operationId and receipt. Predicate values are typed outputs of the C component in this node; retryCount:uint starts 0 and increments only on W10\u2192W8, cancelled:bool from authenticated case cancellation event; timers from durable UTC scheduler. Cancellation > decision > notice precedence. Durable caseId is allocated before W1; no financial effect. ", "transitions": [{"to": "W6", "when": "C6.status in {AVAILABLE,PORTAL_UNAVAILABLE} and notice sequence persisted", "mode": "exclusive"}], "failureDisposition": "Persist owned pending case; no blind financial retry; recovery owner Billing Operations for money and Support Operations otherwise.", "timeout": "48 elapsed hours for W6; model 10s per attempt max2; reads 5s max2; C8 5s max1; reconciliation initial 120s window.", "retryPolicy": "Only model/read schema retries once; writer retry only W10 authoritative absent then W8 once. Notice sequence max2; scheduler never resets 48h clock.", "terminalDisposition": ""}
- **W8 Recheck amount and permission**: {"state": "Persisted CaseState: caseId, tenant scope if authenticated, owner, stateVersion, enqueueAt UTC, noticeMask, retryCount, cancellation flag, eventKey lock, operationId and receipt. Predicate values are typed outputs of the C component in this node; retryCount:uint starts 0 and increments only on W10\u2192W8, cancelled:bool from authenticated case cancellation event; timers from durable UTC scheduler. Cancellation > decision > notice precedence. Durable caseId is allocated before W1; no financial effect. ", "transitions": [{"to": "W9", "when": "C7.status == VALID", "mode": "exclusive"}, {"to": "W12", "when": "C7.status != VALID", "mode": "exclusive"}], "failureDisposition": "Persist owned pending case; no blind financial retry; recovery owner Billing Operations for money and Support Operations otherwise.", "timeout": "48 elapsed hours for W6; model 10s per attempt max2; reads 5s max2; C8 5s max1; reconciliation initial 120s window.", "retryPolicy": "Only model/read schema retries once; writer retry only W10 authoritative absent then W8 once. Notice sequence max2; scheduler never resets 48h clock.", "terminalDisposition": ""}
- **W9 Post the service credit**: {"state": "Persisted CaseState: caseId, tenant scope if authenticated, owner, stateVersion, enqueueAt UTC, noticeMask, retryCount, cancellation flag, eventKey lock, operationId and receipt. Predicate values are typed outputs of the C component in this node; retryCount:uint starts 0 and increments only on W10\u2192W8, cancelled:bool from authenticated case cancellation event; timers from durable UTC scheduler. Cancellation > decision > notice precedence. Durable caseId is allocated before W1; no financial effect. ", "transitions": [{"to": "W11", "when": "C8.result == POSTED", "mode": "exclusive"}, {"to": "W12", "when": "C8.result == REJECTED", "mode": "exclusive"}, {"to": "W10", "when": "C8.result == TIMEOUT", "mode": "exclusive"}, {"to": "W10", "when": "C8.result == UNKNOWN_COMMIT", "mode": "exclusive"}], "failureDisposition": "Persist owned pending case; no blind financial retry; recovery owner Billing Operations for money and Support Operations otherwise.", "timeout": "48 elapsed hours for W6; model 10s per attempt max2; reads 5s max2; C8 5s max1; reconciliation initial 120s window.", "retryPolicy": "Only model/read schema retries once; writer retry only W10 authoritative absent then W8 once. Notice sequence max2; scheduler never resets 48h clock.", "terminalDisposition": ""}
- **W10 Check an uncertain posting**: {"state": "Persisted CaseState: caseId, tenant scope if authenticated, owner, stateVersion, enqueueAt UTC, noticeMask, retryCount, cancellation flag, eventKey lock, operationId and receipt. Predicate values are typed outputs of the C component in this node; retryCount:uint starts 0 and increments only on W10\u2192W8, cancelled:bool from authenticated case cancellation event; timers from durable UTC scheduler. Cancellation > decision > notice precedence. Durable caseId is allocated before W1; no financial effect. ", "transitions": [{"to": "W11", "when": "C9.result == COMMITTED", "mode": "exclusive"}, {"to": "W8", "when": "C9.result == DEFINITIVELY_ABSENT and retryCount < 1 and not cancelled", "mode": "exclusive"}, {"to": "W12", "when": "C9.result == UNRESOLVED or (C9.result == DEFINITIVELY_ABSENT and (retryCount >= 1 or cancelled))", "mode": "exclusive"}], "failureDisposition": "Persist owned pending case; no blind financial retry; recovery owner Billing Operations for money and Support Operations otherwise.", "timeout": "48 elapsed hours for W6; model 10s per attempt max2; reads 5s max2; C8 5s max1; reconciliation initial 120s window.", "retryPolicy": "Only model/read schema retries once; writer retry only W10 authoritative absent then W8 once. Notice sequence max2; scheduler never resets 48h clock.", "terminalDisposition": ""}
- **W11 Verify credit proof**: {"state": "Persisted CaseState: caseId, tenant scope if authenticated, owner, stateVersion, enqueueAt UTC, noticeMask, retryCount, cancellation flag, eventKey lock, operationId and receipt. Predicate values are typed outputs of the C component in this node; retryCount:uint starts 0 and increments only on W10\u2192W8, cancelled:bool from authenticated case cancellation event; timers from durable UTC scheduler. Cancellation > decision > notice precedence. Durable caseId is allocated before W1; no financial effect.  postingId selects C8 on POSTED or C9 on COMMITTED; all other results have no projection and fail proof. C10 must verify nonempty committed receipt before PROVEN_CREDIT.", "transitions": [{"to": "W13", "when": "C10.status == PROVEN_CREDIT", "mode": "exclusive"}, {"to": "W12", "when": "C10.status != PROVEN_CREDIT", "mode": "exclusive"}], "failureDisposition": "Persist owned pending case; no blind financial retry; recovery owner Billing Operations for money and Support Operations otherwise.", "timeout": "48 elapsed hours for W6; model 10s per attempt max2; reads 5s max2; C8 5s max1; reconciliation initial 120s window.", "retryPolicy": "Only model/read schema retries once; writer retry only W10 authoritative absent then W8 once. Notice sequence max2; scheduler never resets 48h clock.", "terminalDisposition": "", "bindings": {"postingId": [{"sourceComponentId": "C8", "sourceField": "postingId"}, {"sourceComponentId": "C9", "sourceField": "postingId"}]}}
- **W12 Keep case proof and owner**: {"state": "Persisted CaseState: caseId, tenant scope if authenticated, owner, stateVersion, enqueueAt UTC, noticeMask, retryCount, cancellation flag, eventKey lock, operationId and receipt. Predicate values are typed outputs of the C component in this node; retryCount:uint starts 0 and increments only on W10\u2192W8, cancelled:bool from authenticated case cancellation event; timers from durable UTC scheduler. Cancellation > decision > notice precedence. Durable caseId is allocated before W1; no financial effect. Preserve reason AUTH_FAILED/SELECTION_REQUIRED/INACTIVE/NO_CREDIT/DENIED/CANCELLED/STALE/REVOKED/DUPLICATE/OVERDUE/UNAVAILABLE/PENDING_RECONCILIATION/MISSING_PROOF from prior event. If case persistence cannot be read, do not exit: operational alarm and durable transaction recovery; no customer completion. C11 rejects empty/missing direct C1 proof and never reaches W14 on MISSING_PROOF. Case storage recovery remains owned; financial status stays pending if no receipt exists.", "transitions": [{"to": "W14", "when": "C11.status == PROVEN_CASE", "mode": "exclusive"}], "failureDisposition": "MISSING_PROOF pauses durable runner with Support Operations storage incident; do not emit W14 or W13. Restore and re-read authoritative Case before rerunning C11.", "timeout": "48 elapsed hours for W6; model 10s per attempt max2; reads 5s max2; C8 5s max1; reconciliation initial 120s window.", "retryPolicy": "Only model/read schema retries once; writer retry only W10 authoritative absent then W8 once. Notice sequence max2; scheduler never resets 48h clock.", "terminalDisposition": "", "bindings": {"caseRecordId": {"sourceComponentId": "C1", "sourceField": "caseRecordId"}}}
- **W13 Credit confirmed**: {"state": "Persisted CaseState: caseId, tenant scope if authenticated, owner, stateVersion, enqueueAt UTC, noticeMask, retryCount, cancellation flag, eventKey lock, operationId and receipt. Predicate values are typed outputs of the C component in this node; retryCount:uint starts 0 and increments only on W10\u2192W8, cancelled:bool from authenticated case cancellation event; timers from durable UTC scheduler. Cancellation > decision > notice precedence. Durable caseId is allocated before W1; no financial effect. ", "transitions": [], "failureDisposition": "Persist owned pending case; no blind financial retry; recovery owner Billing Operations for money and Support Operations otherwise.", "timeout": "48 elapsed hours for W6; model 10s per attempt max2; reads 5s max2; C8 5s max1; reconciliation initial 120s window.", "retryPolicy": "Only model/read schema retries once; writer retry only W10 authoritative absent then W8 once. Notice sequence max2; scheduler never resets 48h clock.", "terminalDisposition": "Proven posted credit with postingId and caseId."}
- **W14 Case outcome or owned pending**: {"state": "Persisted CaseState: caseId, tenant scope if authenticated, owner, stateVersion, enqueueAt UTC, noticeMask, retryCount, cancellation flag, eventKey lock, operationId and receipt. Predicate values are typed outputs of the C component in this node; retryCount:uint starts 0 and increments only on W10\u2192W8, cancelled:bool from authenticated case cancellation event; timers from durable UTC scheduler. Cancellation > decision > notice precedence. Durable caseId is allocated before W1; no financial effect. View includes caseId, owner and truthful next action. OVERDUE shows missed deadline immediately. PENDING_RECONCILIATION is not closed and retains frozen event key and read-only reconciliation owner. Portal resumes from persisted case after reconnect.", "transitions": [], "failureDisposition": "Persist owned pending case; no blind financial retry; recovery owner Billing Operations for money and Support Operations otherwise.", "timeout": "48 elapsed hours for W6; model 10s per attempt max2; reads 5s max2; C8 5s max1; reconciliation initial 120s window.", "retryPolicy": "Only model/read schema retries once; writer retry only W10 authoritative absent then W8 once. Notice sequence max2; scheduler never resets 48h clock.", "terminalDisposition": "Durable non-credit outcome or owned pending case with reason; unresolved money never called complete."}

## Framework

### F1 · A durable code workflow

Use one durable code state machine with a bounded explanation model. Code owns route/amount/clock. Planner adds authority risk; request handler cannot own 48h waits. Compare database-backed workers and workflow engine on durable timers, event ordering, retry visibility and operational burden; start database worker plus transactional outbox; choose a workflow engine if replay/recovery support is easier for team.

Reasoning: Bound responsibility to a testable contract.

Assumptions:

- H2

- H4

Data:

```json
{
  "category": "fit",
  "taskIds": [
    "T1",
    "T2",
    "T3.1",
    "T3.2",
    "T4"
  ],
  "choice": "Use one durable code state machine with a bounded explanation model.",
  "alternatives": [
    "Free-running multi-agent planner; synchronous request handler."
  ],
  "tradeoffs": "Code owns route/amount/clock. Planner adds authority risk; request handler cannot own 48h waits. Compare database-backed workers and workflow engine on durable timers, event ordering, retry visibility and operational burden; start database worker plus transactional outbox; choose a workflow engine if replay/recovery support is easier for team.",
  "permission": "none",
  "blastRadius": "One tenant/customer/active connection and original invoice/incident per command; system outage disables automatic credits.",
  "approvalRule": "H1-H4 verified before live data or money; policy or exact supervisor plan at C7/C8.",
  "leastPrivilege": "Scoped reads, credit-only write, separate durable reconciliation identity; portal ownership enforced on every GET.",
  "aws": "Unverified managed candidates in F4; compare timer durability and audit.",
  "gcp": "Unverified managed candidates in F4; same criteria.",
  "azure": "Unverified managed candidates in F4; same criteria.",
  "openSource": "PostgreSQL worker/outbox and encrypted object store; test crash recovery and operations."
}
```


Sources:

- hypothesis / H2: Account, service and billing adapters must offer authenticated tenant/subject reads, active connection version checks, scoped credit posting with a unique business-event key and definitive operation readback. Financial API must also atomically compare and consume invoice entitlement versions across different incident keys.

- hypothesis / H4: Proposed retention is 30 days for redacted model traces and 365 days for financial audit; deployment region, deletion exceptions and customer permissions need privacy review.

### F2 · State and evidence ownership

Relational case store for scope/versions/queue/event keys; immutable approved plans and append-only audit. Billing ledger remains financial truth. Retrieval may help explanation later, but cannot decide entitlement. Inbox events unique by provider eventId; DB compare-and-swap by caseVersion. Outbox and timers resume on worker restart. Local state updates are internal bookkeeping, never telecom account mutations. Portal GET exposes durable workflow notices without email/SMS side effects.

Reasoning: Bound responsibility to a testable contract.

Assumptions:

- H2

- H4

Data:

```json
{
  "category": "architecture",
  "taskIds": [
    "T2",
    "T3.1",
    "T3.2",
    "T4"
  ],
  "choice": "Relational case store for scope/versions/queue/event keys; immutable approved plans and append-only audit. Billing ledger remains financial truth.",
  "alternatives": [
    "Vector store as authority; model conversation as state."
  ],
  "tradeoffs": "Retrieval may help explanation later, but cannot decide entitlement. Inbox events unique by provider eventId; DB compare-and-swap by caseVersion. Outbox and timers resume on worker restart. Local state updates are internal bookkeeping, never telecom account mutations. Portal GET exposes durable workflow notices without email/SMS side effects.",
  "permission": "none",
  "blastRadius": "One tenant/customer/active connection and original invoice/incident per command; system outage disables automatic credits.",
  "approvalRule": "H1-H4 verified before live data or money; policy or exact supervisor plan at C7/C8.",
  "leastPrivilege": "Scoped reads, credit-only write, separate durable reconciliation identity; portal ownership enforced on every GET.",
  "aws": "Unverified managed candidates in F4; compare timer durability and audit.",
  "gcp": "Unverified managed candidates in F4; same criteria.",
  "azure": "Unverified managed candidates in F4; same criteria.",
  "openSource": "PostgreSQL worker/outbox and encrypted object store; test crash recovery and operations."
}
```


Sources:

- hypothesis / H2: Account, service and billing adapters must offer authenticated tenant/subject reads, active connection version checks, scoped credit posting with a unique business-event key and definitive operation readback. Financial API must also atomically compare and consume invoice entitlement versions across different incident keys.

- hypothesis / H4: Proposed retention is 30 days for redacted model traces and 365 days for financial audit; deployment region, deletion exceptions and customer permissions need privacy review.

### F3 · Separate read and credit identities

Gateway checks tenant/customer and active selected connection before reads; credit adapter only posts a scoped service-credit command. Small blast radius; readback service identity may outlive portal session. Every financial writer enforces fresh plan and event key; human approval cannot bypass source evidence or revoked authority. Secrets via deployment secret store, rotation and no model access.

Reasoning: Bound responsibility to a testable contract.

Assumptions:

- H2

- H4

Data:

```json
{
  "category": "permission",
  "taskIds": [
    "T1",
    "T3.1",
    "T4"
  ],
  "choice": "Gateway checks tenant/customer and active selected connection before reads; credit adapter only posts a scoped service-credit command.",
  "alternatives": [
    "One broad billing admin credential."
  ],
  "tradeoffs": "Small blast radius; readback service identity may outlive portal session. Every financial writer enforces fresh plan and event key; human approval cannot bypass source evidence or revoked authority. Secrets via deployment secret store, rotation and no model access.",
  "permission": "write",
  "blastRadius": "One tenant/customer/active connection and original invoice/incident per command; system outage disables automatic credits.",
  "approvalRule": "H1-H4 verified before live data or money; policy or exact supervisor plan at C7/C8.",
  "leastPrivilege": "Scoped reads, credit-only write, separate durable reconciliation identity; portal ownership enforced on every GET.",
  "aws": "Unverified managed candidates in F4; compare timer durability and audit.",
  "gcp": "Unverified managed candidates in F4; same criteria.",
  "azure": "Unverified managed candidates in F4; same criteria.",
  "openSource": "PostgreSQL worker/outbox and encrypted object store; test crash recovery and operations."
}
```


Sources:

- hypothesis / H2: Account, service and billing adapters must offer authenticated tenant/subject reads, active connection version checks, scoped credit posting with a unique business-event key and definitive operation readback. Financial API must also atomically compare and consume invoice entitlement versions across different incident keys.

- hypothesis / H4: Proposed retention is 30 days for redacted model traces and 365 days for financial audit; deployment region, deletion exceptions and customer permissions need privacy review.

### F4 · Data deployment candidates

Choose managed relational DB, encrypted object audit and a secrets service in approved region; provider decision remains H4 spike. AWS: RDS/object storage/secrets candidates; GCP: Cloud SQL/object storage/secret manager candidates; Azure: managed PostgreSQL/blob/key vault candidates; open source: PostgreSQL/S3-compatible storage/Vault candidates. Compare retention, residency, access audit, restore and operator load on identical requirements. These are candidates; no current capability, pricing or compliance claim. Minimize model data to evidence extracts with pseudonymous IDs; never payment details.

Reasoning: Bound responsibility to a testable contract.

Assumptions:

- H2

- H4

Data:

```json
{
  "category": "data",
  "taskIds": [
    "T1",
    "T2",
    "T4"
  ],
  "choice": "Choose managed relational DB, encrypted object audit and a secrets service in approved region; provider decision remains H4 spike.",
  "alternatives": [
    "Cross-region unreviewed replication; embeddings over raw billing records."
  ],
  "tradeoffs": "AWS: RDS/object storage/secrets candidates; GCP: Cloud SQL/object storage/secret manager candidates; Azure: managed PostgreSQL/blob/key vault candidates; open source: PostgreSQL/S3-compatible storage/Vault candidates. Compare retention, residency, access audit, restore and operator load on identical requirements. These are candidates; no current capability, pricing or compliance claim. Minimize model data to evidence extracts with pseudonymous IDs; never payment details.",
  "permission": "read",
  "blastRadius": "One tenant/customer/active connection and original invoice/incident per command; system outage disables automatic credits.",
  "approvalRule": "H1-H4 verified before live data or money; policy or exact supervisor plan at C7/C8.",
  "leastPrivilege": "Scoped reads, credit-only write, separate durable reconciliation identity; portal ownership enforced on every GET.",
  "aws": "Unverified managed candidates in F4; compare timer durability and audit.",
  "gcp": "Unverified managed candidates in F4; same criteria.",
  "azure": "Unverified managed candidates in F4; same criteria.",
  "openSource": "PostgreSQL worker/outbox and encrypted object store; test crash recovery and operations."
}
```


Sources:

- hypothesis / H2: Account, service and billing adapters must offer authenticated tenant/subject reads, active connection version checks, scoped credit posting with a unique business-event key and definitive operation readback. Financial API must also atomically compare and consume invoice entitlement versions across different incident keys.

- hypothesis / H4: Proposed retention is 30 days for redacted model traces and 365 days for financial audit; deployment region, deletion exceptions and customer permissions need privacy review.


## Models

- **M1 A small explanation model**: Proposed small model drafts evidence-linked explanations only; no financial, date or identity authority. One invocation in W3, at most two attempts; deterministic fallback on invalid/unavailable output. H5 is illustrative budget, not measured usage.

## Fmea

- **FM1 Wrong or inactive connection**: Hypothetical S/O/D: severity 1 negligible to10 catastrophic; occurrence1 rare to10 frequent; detection1 caught before harm to10 rarely detected. RPN=120; scores prioritize review, not probability.
- **FM2 Stale policy or invoice**: Hypothetical S/O/D: severity 1 negligible to10 catastrophic; occurrence1 rare to10 frequent; detection1 caught before harm to10 rarely detected. RPN=180; scores prioritize review, not probability.
- **FM3 Duplicate or concurrent credit**: Hypothetical S/O/D: severity 1 negligible to10 catastrophic; occurrence1 rare to10 frequent; detection1 caught before harm to10 rarely detected. RPN=225; scores prioritize review, not probability.
- **FM4 Uncertain posting retried**: Hypothetical S/O/D: severity 1 negligible to10 catastrophic; occurrence1 rare to10 frequent; detection1 caught before harm to10 rarely detected. RPN=216; scores prioritize review, not probability.
- **FM5 Model follows injected records**: Hypothetical S/O/D: severity 1 negligible to10 catastrophic; occurrence1 rare to10 frequent; detection1 caught before harm to10 rarely detected. RPN=128; scores prioritize review, not probability.
- **FM6 False credit completion**: Hypothetical S/O/D: severity 1 negligible to10 catastrophic; occurrence1 rare to10 frequent; detection1 caught before harm to10 rarely detected. RPN=160; scores prioritize review, not probability.
- **FM7 Supervisor or notice clock lost**: Hypothetical S/O/D: severity 1 negligible to10 catastrophic; occurrence1 rare to10 frequent; detection1 caught before harm to10 rarely detected. RPN=200; scores prioritize review, not probability.
- **FM8 Contradictory or missing evidence**: Hypothetical S/O/D: severity 1 negligible to10 catastrophic; occurrence1 rare to10 frequent; detection1 caught before harm to10 rarely detected. RPN=175; scores prioritize review, not probability.
- **FM9 Cancellation or denied approval bypassed**: Hypothetical S/O/D: severity 1 negligible to10 catastrophic; occurrence1 rare to10 frequent; detection1 caught before harm to10 rarely detected. RPN=180; scores prioritize review, not probability.

## Evals

- **EV1 Eligible credit positive**: Self-contained synthetic fixture; ordered mocks are expected adapter conditions, not executed evidence.
- **EV2 Supervisor larger-credit positive**: Self-contained synthetic fixture; ordered mocks are expected adapter conditions, not executed evidence.
- **EV3 Wrong customer blocks reads**: Self-contained synthetic fixture; ordered mocks are expected adapter conditions, not executed evidence.
- **EV4 Inactive service rejected**: Self-contained synthetic fixture; ordered mocks are expected adapter conditions, not executed evidence.
- **EV5 Changed policy invalidates plan**: Self-contained synthetic fixture; ordered mocks are expected adapter conditions, not executed evidence.
- **EV6 Approval covers whole plan**: Self-contained synthetic fixture; ordered mocks are expected adapter conditions, not executed evidence.
- **EV7 Revoked authority prevents credit**: Self-contained synthetic fixture; ordered mocks are expected adapter conditions, not executed evidence.
- **EV8 Two cases cannot duplicate one incident**: Self-contained synthetic fixture; ordered mocks are expected adapter conditions, not executed evidence.
- **EV9 Timeout committed and duplicate callback**: Self-contained synthetic fixture; ordered mocks are expected adapter conditions, not executed evidence.
- **EV10 Definitive absence permits one guarded retry**: Self-contained synthetic fixture; ordered mocks are expected adapter conditions, not executed evidence.
- **EV11 Unknown commit stays frozen**: Self-contained synthetic fixture; ordered mocks are expected adapter conditions, not executed evidence.
- **EV12 Injection cannot control money**: Self-contained synthetic fixture; ordered mocks are expected adapter conditions, not executed evidence.
- **EV13 Success response without record is not completion**: Self-contained synthetic fixture; ordered mocks are expected adapter conditions, not executed evidence.
- **EV14 Wait notices and overdue ownership**: Self-contained synthetic fixture; ordered mocks are expected adapter conditions, not executed evidence.
- **EV15 Portal outage retains customer notice**: Self-contained synthetic fixture; ordered mocks are expected adapter conditions, not executed evidence.
- **EV16 Cancellation wins before post**: Self-contained synthetic fixture; ordered mocks are expected adapter conditions, not executed evidence.
- **EV17 Conflicting billing or speed evidence abstains**: Self-contained synthetic fixture; ordered mocks are expected adapter conditions, not executed evidence.
- **EV18 Remaining charge caps credit**: Self-contained synthetic fixture; ordered mocks are expected adapter conditions, not executed evidence.
- **EV19 Evidence supports no service credit**: Self-contained synthetic fixture; ordered mocks are expected adapter conditions, not executed evidence.
- **EV20 Denied larger credit**: Self-contained synthetic fixture; ordered mocks are expected adapter conditions, not executed evidence.
- **EV21 Offline evidence and adapter suite**: Future execution specification; not observed results.
- **EV22 Online safety and queue monitoring**: Future execution specification; not observed results.
- **EV23 Release complete suite**: Future execution specification; not observed results.
- **EV24 Two incidents cannot exceed one invoice cap**: Self-contained synthetic fixture for a proposed business policy; future harness execution required.
- **EV25 Clarify among multiple active services**: Self-contained synthetic fixture for a proposed business policy; future harness execution required.
- **EV26 Tampered approval amount is isolated**: Self-contained synthetic fixture for a proposed business policy; future harness execution required.

## Rollout

### R1 · Measure durable complaint resolution

Evidence citation precision supports explanation trust; route agreement reduces avoidable supervisor load; timer/notice lag protects customer follow-through. Cost and safety metrics are guardrails, not assumed causal gains.

Reasoning: Bound responsibility to a testable contract.

Assumptions:

- H1

- H2

- H3

- H4

- H5

Data:

```json
{
  "category": "kpi",
  "businessKpi": "Seven-day reopen rate = complaints reopened within7d / complaints receiving a decision, by decision week. Track median and p95 elapsed hours to proven credit or owned decision. Financial correctness = wrong/duplicate/unsupported credit count and value per posted credit; safety counts are never averaged away. Collect two-week manual baseline before setting effect targets.",
  "aiMetrics": [
    "EV21 citation precision/route agreement",
    "EV22 unsafe effects, queue and notice lag; model cost per case"
  ],
  "phase": "All phases",
  "gate": "Evidence citation precision supports explanation trust; route agreement reduces avoidable supervisor load; timer/notice lag protects customer follow-through. Cost and safety metrics are guardrails, not assumed causal gains.",
  "owner": "Product analytics owner",
  "experiment": "Initial aim: non-inferior reopen rate with shorter resolution; quantify after baseline."
}
```


Sources:

- hypothesis / H1: Proposed pilot policy P1: verified outage credits equal floor(monthly recurring service charge in minor units × verified outage seconds / billing-period seconds), capped at the remaining recurring charge. Auto cap is 1000 minor units INR per incident; poor speed without a verified service breach and billing errors require supervisor review.

- hypothesis / H2: Account, service and billing adapters must offer authenticated tenant/subject reads, active connection version checks, scoped credit posting with a unique business-event key and definitive operation readback. Financial API must also atomically compare and consume invoice entitlement versions across different incident keys.

- hypothesis / H3: Proposed supervisor queue is staffed continuously, acknowledges cases within 1 elapsed hour, decides within 48 elapsed hours, and a duty manager owns overdue cases. Portal updates appear on entry and at 24 hours; overdue notice appears at 48 hours.

- hypothesis / H4: Proposed retention is 30 days for redacted model traces and 365 days for financial audit; deployment region, deletion exceptions and customer permissions need privacy review.

- hypothesis / H5: Illustrative traffic is 10000 cases/month; one explanation call per case, maximum two attempts. Assume 10% retry rate and 2000 input/300 output tokens at $1/$4 per million tokens.

### R2 · Shadow without customer effects

Entry: synthetic EV23 passes and lawful scoped read approvals. Exit: two weeks representative labelled traces covering outage/speed/billing and active/multi-connection strata; EV21 thresholds with adjudicated disagreements; no scoped data breach.

Reasoning: Bound responsibility to a testable contract.

Assumptions:

- H1

- H2

- H3

- H4

- H5

Data:

```json
{
  "category": "phase",
  "businessKpi": "R1 outcome baseline only",
  "aiMetrics": [
    "EV21 citation precision/route agreement",
    "EV22 unsafe effects, queue and notice lag; model cost per case"
  ],
  "phase": "Shadow: proposed two weeks after H4 data approval; no customer explanation or credit adapter permission.",
  "gate": "Entry: synthetic EV23 passes and lawful scoped read approvals. Exit: two weeks representative labelled traces covering outage/speed/billing and active/multi-connection strata; EV21 thresholds with adjudicated disagreements; no scoped data breach.",
  "owner": "Support quality owner",
  "experiment": "Stop on privacy breach; remove shadow access, retain necessary incident evidence."
}
```


Sources:

- hypothesis / H1: Proposed pilot policy P1: verified outage credits equal floor(monthly recurring service charge in minor units × verified outage seconds / billing-period seconds), capped at the remaining recurring charge. Auto cap is 1000 minor units INR per incident; poor speed without a verified service breach and billing errors require supervisor review.

- hypothesis / H2: Account, service and billing adapters must offer authenticated tenant/subject reads, active connection version checks, scoped credit posting with a unique business-event key and definitive operation readback. Financial API must also atomically compare and consume invoice entitlement versions across different incident keys.

- hypothesis / H3: Proposed supervisor queue is staffed continuously, acknowledges cases within 1 elapsed hour, decides within 48 elapsed hours, and a duty manager owns overdue cases. Portal updates appear on entry and at 24 hours; overdue notice appears at 48 hours.

- hypothesis / H4: Proposed retention is 30 days for redacted model traces and 365 days for financial audit; deployment region, deletion exceptions and customer permissions need privacy review.

- hypothesis / H5: Illustrative traffic is 10000 cases/month; one explanation call per case, maximum two attempts. Assume 10% retry rate and 2000 input/300 output tokens at $1/$4 per million tokens.

### R3 · Assist staff with reviewed plans

Entry: Shadow exit plus staff queue training and H1/H3 approvals. Exit: independently labelled plans meet EV21; H2 sandbox proves commit checks, uniqueness and readback; EV22 alarms exercised. No pilot effect required for entry.

Reasoning: Bound responsibility to a testable contract.

Assumptions:

- H1

- H2

- H3

- H4

- H5

Data:

```json
{
  "category": "phase",
  "businessKpi": "R1 evidence-backed decision time",
  "aiMetrics": [
    "EV21 citation precision/route agreement",
    "EV22 unsafe effects, queue and notice lag; model cost per case"
  ],
  "phase": "Assist: proposed two weeks; staff reviews every explanation and manually handles all financial commands.",
  "gate": "Entry: Shadow exit plus staff queue training and H1/H3 approvals. Exit: independently labelled plans meet EV21; H2 sandbox proves commit checks, uniqueness and readback; EV22 alarms exercised. No pilot effect required for entry.",
  "owner": "Support operations owner",
  "experiment": "Record disagreement reasons and baseline variance for power calculation. Staff remains responsible."
}
```


Sources:

- hypothesis / H1: Proposed pilot policy P1: verified outage credits equal floor(monthly recurring service charge in minor units × verified outage seconds / billing-period seconds), capped at the remaining recurring charge. Auto cap is 1000 minor units INR per incident; poor speed without a verified service breach and billing errors require supervisor review.

- hypothesis / H2: Account, service and billing adapters must offer authenticated tenant/subject reads, active connection version checks, scoped credit posting with a unique business-event key and definitive operation readback. Financial API must also atomically compare and consume invoice entitlement versions across different incident keys.

- hypothesis / H3: Proposed supervisor queue is staffed continuously, acknowledges cases within 1 elapsed hour, decides within 48 elapsed hours, and a duty manager owns overdue cases. Portal updates appear on entry and at 24 hours; overdue notice appears at 48 hours.

- hypothesis / H4: Proposed retention is 30 days for redacted model traces and 365 days for financial audit; deployment region, deletion exceptions and customer permissions need privacy review.

- hypothesis / H5: Illustrative traffic is 10000 cases/month; one explanation call per case, maximum two attempts. Assume 10% retry rate and 2000 input/300 output tokens at $1/$4 per million tokens.

### R4 · Bounded automatic-credit pilot

Entry: Assist exit, H1-H4 signed and Billing owner enables scoped adapter. Exit: powered R6 observation complete; zero unsafe financial effects, EV21 quality holds in each stratum, no unowned overdue/unknown case. Product and Billing owners decide expansion.

Reasoning: Bound responsibility to a testable contract.

Assumptions:

- H1

- H2

- H3

- H4

- H5

Data:

```json
{
  "category": "phase",
  "businessKpi": "R1 financial correctness and reopen rate",
  "aiMetrics": [
    "EV21 citation precision/route agreement",
    "EV22 unsafe effects, queue and notice lag; model cost per case"
  ],
  "phase": "Pilot: verified outages only, INR under approved H1 cap; other complaints continue supervisor review. Proposed minimum four weeks plus7d follow-up.",
  "gate": "Entry: Assist exit, H1-H4 signed and Billing owner enables scoped adapter. Exit: powered R6 observation complete; zero unsafe financial effects, EV21 quality holds in each stratum, no unowned overdue/unknown case. Product and Billing owners decide expansion.",
  "owner": "Billing operations owner",
  "experiment": "Safety event instantly disables new automatic writes; preserve queue/readback. No automatic reversal; investigate existing receipts."
}
```


Sources:

- hypothesis / H1: Proposed pilot policy P1: verified outage credits equal floor(monthly recurring service charge in minor units × verified outage seconds / billing-period seconds), capped at the remaining recurring charge. Auto cap is 1000 minor units INR per incident; poor speed without a verified service breach and billing errors require supervisor review.

- hypothesis / H2: Account, service and billing adapters must offer authenticated tenant/subject reads, active connection version checks, scoped credit posting with a unique business-event key and definitive operation readback. Financial API must also atomically compare and consume invoice entitlement versions across different incident keys.

- hypothesis / H3: Proposed supervisor queue is staffed continuously, acknowledges cases within 1 elapsed hour, decides within 48 elapsed hours, and a duty manager owns overdue cases. Portal updates appear on entry and at 24 hours; overdue notice appears at 48 hours.

- hypothesis / H4: Proposed retention is 30 days for redacted model traces and 365 days for financial audit; deployment region, deletion exceptions and customer permissions need privacy review.

- hypothesis / H5: Illustrative traffic is 10000 cases/month; one explanation call per case, maximum two attempts. Assume 10% retry rate and 2000 input/300 output tokens at $1/$4 per million tokens.

### R5 · Expand only with evidence

Entry: Pilot exit and owner decision. Weekly audit and EV23 on each policy/adapter change. Roll back new automatic traffic on any wrong-subject, duplicate or unproven completion; existing uncertain operations retain keys and reconciliation identity.

Reasoning: Bound responsibility to a testable contract.

Assumptions:

- H1

- H2

- H3

- H4

- H5

Data:

```json
{
  "category": "phase",
  "businessKpi": "R1 repeat contacts and decision time",
  "aiMetrics": [
    "EV21 citation precision/route agreement",
    "EV22 unsafe effects, queue and notice lag; model cost per case"
  ],
  "phase": "Scale: expand outage traffic in steps agreed by owners; speed/billing credits remain supervisor-only until a new verified policy/design review.",
  "gate": "Entry: Pilot exit and owner decision. Weekly audit and EV23 on each policy/adapter change. Roll back new automatic traffic on any wrong-subject, duplicate or unproven completion; existing uncertain operations retain keys and reconciliation identity.",
  "owner": "Product owner with Billing and Security veto",
  "experiment": "Capacity load and queue SLA verified before increasing traffic; no arbitrary traffic assumption presented as safe."
}
```


Sources:

- hypothesis / H1: Proposed pilot policy P1: verified outage credits equal floor(monthly recurring service charge in minor units × verified outage seconds / billing-period seconds), capped at the remaining recurring charge. Auto cap is 1000 minor units INR per incident; poor speed without a verified service breach and billing errors require supervisor review.

- hypothesis / H2: Account, service and billing adapters must offer authenticated tenant/subject reads, active connection version checks, scoped credit posting with a unique business-event key and definitive operation readback. Financial API must also atomically compare and consume invoice entitlement versions across different incident keys.

- hypothesis / H3: Proposed supervisor queue is staffed continuously, acknowledges cases within 1 elapsed hour, decides within 48 elapsed hours, and a duty manager owns overdue cases. Portal updates appear on entry and at 24 hours; overdue notice appears at 48 hours.

- hypothesis / H4: Proposed retention is 30 days for redacted model traces and 365 days for financial audit; deployment region, deletion exceptions and customer permissions need privacy review.

- hypothesis / H5: Illustrative traffic is 10000 cases/month; one explanation call per case, maximum two attempts. Assume 10% retry rate and 2000 input/300 output tokens at $1/$4 per million tokens.

### R6 · Run a controlled complaint experiment

Randomize authenticated customer account, sticky assignment, stratified by complaint type, language and connection count. Same household account never crosses arms; staff tool clearly labels control and cannot transfer cases. Manual process control vs bounded assistant treatment, same eligibility and supervisors. Observe at least four weekly cycles and7d follow-up, extending for planned sample. Compute two-proportion non-inferiority sample from baseline p, pre-agreed margin, alpha .05 and power .80; adjust repeated accounts by design effect1+(m-1)ICC; estimate ICC during baseline. For time outcome use baseline variance and continuous-outcome power separately. Fix margin/sample before examining treatment outcomes; safety stops immediate regardless of power.

Reasoning: Bound responsibility to a testable contract.

Assumptions:

- H1

- H2

- H3

- H4

- H5

Data:

```json
{
  "category": "experiment",
  "businessKpi": "Primary: seven-day reopen binary outcome; secondary elapsed decision time",
  "aiMetrics": [
    "EV21 citation precision/route agreement",
    "EV22 unsafe effects, queue and notice lag; model cost per case"
  ],
  "phase": "Pilot evaluation",
  "gate": "Randomize authenticated customer account, sticky assignment, stratified by complaint type, language and connection count. Same household account never crosses arms; staff tool clearly labels control and cannot transfer cases. Manual process control vs bounded assistant treatment, same eligibility and supervisors. Observe at least four weekly cycles and7d follow-up, extending for planned sample. Compute two-proportion non-inferiority sample from baseline p, pre-agreed margin, alpha .05 and power .80; adjust repeated accounts by design effect1+(m-1)ICC; estimate ICC during baseline. For time outcome use baseline variance and continuous-outcome power separately. Fix margin/sample before examining treatment outcomes; safety stops immediate regardless of power.",
  "owner": "Product analytics owner; Billing owns safety stops",
  "experiment": "No sample size, effect or savings invented. Pre-register analysis, attrition and missing-data handling; report per-stratum uncertainty."
}
```


Sources:

- hypothesis / H1: Proposed pilot policy P1: verified outage credits equal floor(monthly recurring service charge in minor units × verified outage seconds / billing-period seconds), capped at the remaining recurring charge. Auto cap is 1000 minor units INR per incident; poor speed without a verified service breach and billing errors require supervisor review.

- hypothesis / H2: Account, service and billing adapters must offer authenticated tenant/subject reads, active connection version checks, scoped credit posting with a unique business-event key and definitive operation readback. Financial API must also atomically compare and consume invoice entitlement versions across different incident keys.

- hypothesis / H3: Proposed supervisor queue is staffed continuously, acknowledges cases within 1 elapsed hour, decides within 48 elapsed hours, and a duty manager owns overdue cases. Portal updates appear on entry and at 24 hours; overdue notice appears at 48 hours.

- hypothesis / H4: Proposed retention is 30 days for redacted model traces and 365 days for financial audit; deployment region, deletion exceptions and customer permissions need privacy review.

- hypothesis / H5: Illustrative traffic is 10000 cases/month; one explanation call per case, maximum two attempts. Assume 10% retry rate and 2000 input/300 output tokens at $1/$4 per million tokens.

### R7 · Own every pending case

Support owns supervisor waits and1h acknowledgement/48h decision; duty manager owns overdue. Billing owns uncertain posting, hourly read-only recovery and ledger reconciliation. Security owns scope/revocation incidents; model owner owns unsupported explanations. Product can expand only with all required gate owners.

Reasoning: Bound responsibility to a testable contract.

Assumptions:

- H1

- H2

- H3

- H4

- H5

Data:

```json
{
  "category": "owner",
  "businessKpi": "No unowned pending cases",
  "aiMetrics": [
    "EV21 citation precision/route agreement",
    "EV22 unsafe effects, queue and notice lag; model cost per case"
  ],
  "phase": "All phases",
  "gate": "Support owns supervisor waits and1h acknowledgement/48h decision; duty manager owns overdue. Billing owns uncertain posting, hourly read-only recovery and ledger reconciliation. Security owns scope/revocation incidents; model owner owns unsupported explanations. Product can expand only with all required gate owners.",
  "owner": "Support and Billing duty managers",
  "experiment": "Proposed owners and staffing are H3 verification dependencies, not stakeholder approval."
}
```


Sources:

- hypothesis / H1: Proposed pilot policy P1: verified outage credits equal floor(monthly recurring service charge in minor units × verified outage seconds / billing-period seconds), capped at the remaining recurring charge. Auto cap is 1000 minor units INR per incident; poor speed without a verified service breach and billing errors require supervisor review.

- hypothesis / H2: Account, service and billing adapters must offer authenticated tenant/subject reads, active connection version checks, scoped credit posting with a unique business-event key and definitive operation readback. Financial API must also atomically compare and consume invoice entitlement versions across different incident keys.

- hypothesis / H3: Proposed supervisor queue is staffed continuously, acknowledges cases within 1 elapsed hour, decides within 48 elapsed hours, and a duty manager owns overdue cases. Portal updates appear on entry and at 24 hours; overdue notice appears at 48 hours.

- hypothesis / H4: Proposed retention is 30 days for redacted model traces and 365 days for financial audit; deployment region, deletion exceptions and customer permissions need privacy review.

- hypothesis / H5: Illustrative traffic is 10000 cases/month; one explanation call per case, maximum two attempts. Assume 10% retry rate and 2000 input/300 output tokens at $1/$4 per million tokens.


## Export

### X1 · Implement the bounded workflow

A design and future test specification, not built telecom software.

Reasoning: Bound responsibility to a testable contract.

Data:

```json
{
  "acceptanceCriteria": [
    "T1 rejects wrong/inactive scope before C2 reads; EV3/EV4 pass.",
    "C4/C7/C8 preserve all plan fields, atomic eventKey uniqueness and policy/authority versions; EV1-EV8 and EV18 pass.",
    "W6/W7 preserve1h acknowledgement, ENTRY/H24/48h updates across restart; EV14-EV16 pass.",
    "W9 timeout never retries before W10 definitive absence; EV9-EV11 pass; unresolved event keys stay frozen.",
    "W13 requires proven postingId and exact receipt; EV13 passes; no-case storage failure cannot claim completion.",
    "EV23 executes every EV1-EV20 and EV24-EV26; H1-H4 evidence verified before live launch.",
    "Record guards use required direct string IDs, actual workflow input bindings and authoritative conditional producer fields; no timeout proof. EV24-EV26 pass."
  ],
  "buildInstructions": "Implement milestones01-03 only. Persist Case, CreditPlan, Approval, Operation, Inbox, Notice and Audit tables with versioned transitions. C1/C2/C7/C8/C9 adapters must be verified, not invented existing APIs. Contract fields and enums are in design.json; fixtures maintained in eval-set.json. Add transactional outbox and durable UTC timers; internal case/notice state is one workflow transaction, separate from external financial effect. Inject crashes between reserve/post/readback and callback dedup. Keep original event key locked during unknown commits even beyond24h and portal-session expiry. Map actual provider errors to C8 enum; malformed success becomes UNKNOWN_COMMIT. Deploy read-only Shadow then Assist; enable Pilot only through R4 gate. All deployment, real business actions and messages require separate authorization. No PDF in this authoring subtask. After actual PDF delivery, ask exactly once: “Would you also like a visual HTML version in the same ten-stage structure as the app?” Generate HTML only after opt-in. C10 receives direct C8/C9 committed postingId projections; C11 receives direct C1 authoritative caseRecordId. Never fabricate these fields or add model outputs. EV24 tests separate-incident invoice entitlement locking; EV25 explicit service clarification; EV26 signed amount tampering."
}
```


Sources:

- context / user-brief: Design a complaint assistant for a telecom provider. Customers report network outages, poor speed and billing errors. The assistant should investigate using account, billing and service records, explain findings and resolve eligible service credits. Larger or unclear refunds need a human supervisor and may wait up to 48 hours. Keep customers informed, avoid duplicate refunds and use only the right customer's active service connection. Propose any missing policies as assumptions, not real company rules.


Full exact data and source evidence: [design.json](design.json). Launch facts and owners: [assumptions.md](assumptions.md).
