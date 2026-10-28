# Local outcome recorder

> PASS | DESIGN ONLY. self-review; round 3.

Depends on earlier milestones where their outputs are inputs below. Cross-milestone shared types are read by ID from ../design.json, not copied.

## Selected contracts

### C6 · Local outcome recorder

Append a unique per-invocation local JSON status under ROOT/status (exclusive create + fsync), storing report date, run_key when known, terminal/reason, proof, proposed owner, ack_due_utc and manual next action. COMPLETE exits 0 only with C4/C5 proof; BLOCKED exits 2, CANCELLED exits 130. If status write fails emit structured stderr and status_proof=STDERR_ONLY; this does not convert a proved committed report to failure. Remove owned lock at normal exit; cleanup failure is visible stderr/status warning. Hard crash may leave stale lock: operator confirms no running process and read-only checks final manifest before manual lock removal. Operations checks local statuses by 10:00 UTC, acknowledges failure in a separate local operating log by 12:00 UTC, then manually escalates to lead if overdue. No automatic messaging and no indefinite waiting loop.

Reasoning: A file/exit-code handoff handles exceptions without adding a conversational or remote interface.

Assumptions:

- H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H7: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

Data:

```json
{
  "group": "Code: human triggers",
  "taskIds": [
    "T5"
  ],
  "inputs": [
    "terminal:required enum COMPLETE|BLOCKED|CANCELLED",
    "reason:required enum READY|ALREADY_COMPLETE|INPUT_INVALID|INPUT_IO|OUTPUT_IO|BUSY|CONFLICT|PUBLICATION_UNKNOWN|TIMEOUT|CANCELLED",
    "proof:required on COMPLETE, otherwise absent; lock_acquired:required bool",
    "owner_role:required proposed Operations report owner; acknowledgement_due:required next 12:00 UTC following this run"
  ],
  "outputs": [
    "state:enum COMPLETE|BLOCKED|CANCELLED; exit_code:int enum 0|2|130; status_path:optional absolute path",
    "status_proof:enum DURABLE|STDERR_ONLY; lock_status:enum RELEASED|NOT_HELD|CLEANUP_FAILED"
  ],
  "whyCode": "A file/exit-code handoff handles exceptions without adding a conversational or remote interface.",
  "approvalRule": "Operator-configured local filesystem permission only; no runtime approval conversation. Recheck local path/capability before reads/writes. No external action is authorized by this design."
}
```


Sources:

- context / user-brief: Design a small daily report that joins two CSV files by order ID. One has promised-delivery timestamps and the other actual-delivery timestamps, both ISO UTC. Flag delivered orders more than 24 hours late and export a CSV for the operations team. No emails, remote updates, forecasting or conversational interface.

- hypothesis / H1: The proposed CSV contract is UTF-8 with optional BOM, comma delimiter and one header; promised columns are order_id,promised_delivery_utc and actual columns are order_id,actual_delivery_utc. Extra columns are ignored. IDs are case-sensitive ASCII [A-Za-z0-9][A-Za-z0-9_-]{0,63}, unique within each file; empty or padded IDs are errors.

- hypothesis / H4: Accepted timestamps use YYYY-MM-DDTHH:MM:SS[.ffffff]Z or +00:00, with 1-6 fractional digits, valid Gregorian dates and seconds 00-59. Empty actual means undelivered; non-UTC offsets, missing promised values, leap seconds and greater precision fail validation.

- hypothesis / H5: Proposed operational budget is at most 100,000 rows and 50 MiB per file, 120 seconds per run, and a once-daily invocation at 08:00 UTC after exports are ready. Operations reviews local status by 10:00 UTC and acknowledges failures by 12:00 UTC; after that the operations lead manually escalates.

- hypothesis / H6: Run on one trusted local host/account with two allowlisted input roots, a dedicated output root and same-filesystem staging. Only the job may mutate its output root; no symlinks are permitted in resolved input/output paths. An operator grants these local capabilities in configuration.

- hypothesis / H7: Keep committed CSVs, manifests and local failure records for 30 days. Do not copy raw input files; persist hashes, counts and error row numbers without row contents. Delete expired files locally only through a separate operator-maintained procedure.

- hypothesis / H8: A date with an existing valid completed report is immutable: identical input/config returns ALREADY_COMPLETE; changed input/config returns CONFLICT. Corrections require the owner to archive the old date directory outside this job and rerun; no replacement action is implemented.

## Workflow rules

### W9 · COMPLETE

{"state":"COMPLETE","transitions":[],"failureDisposition":"All outcomes are enumerated below; unhandled internal exceptions go to W11 as BLOCKED/OUTPUT_IO without a success claim.","timeout":"C1-C4 share C1.deadline (120s); C5 has one additional 5s read-only reconciliation budget; C6 attempts local status once then stderr.","retryPolicy":"Zero except W6\u2192W4 after ABSENT, maximum one retry, bounded by deadline and cancellation.","terminalDisposition":"COMPLETE with required proof; C6 status write failure yields STDERR_ONLY and a warning; never invents a report proof.","guardBindings":"C1.outcome enum READY|BLOCKED|BUSY|CANCELLED; C2.outcome VALID|INVALID|CANCELLED; C3.outcome BUILT|CANCELLED; C4.outcome COMMITTED|ALREADY_COMPLETE|NOT_COMMITTED|UNKNOWN|CONFLICT|CANCELLED; C5.outcome COMMITTED|ABSENT|CONFLICT|UNKNOWN. C1 creates retry_count:int=0; orchestrator increments on W6\u2192W4. cancel_requested:boolean comes only from SIGINT/SIGTERM; deadline_expired:boolean compares monotonic clock with C1.deadline. Exact outcome switches below are exhaustive and exclusive; no guard depends on model text. The reason is READY for new/reconciled commit or ALREADY_COMPLETE for identical rerun."}

Reasoning: Explicit outcome switches and bounded readback preserve local report integrity.

Assumptions:

- H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

Data:

```json
{
  "componentId": "C6",
  "taskIds": [
    "T5"
  ],
  "next": [],
  "decision": false,
  "example": "C4/C5 proof is persisted; exit 0 with final manifest path."
}
```


Sources:

- context / user-brief: Design a small daily report that joins two CSV files by order ID. One has promised-delivery timestamps and the other actual-delivery timestamps, both ISO UTC. Flag delivered orders more than 24 hours late and export a CSV for the operations team. No emails, remote updates, forecasting or conversational interface.

- hypothesis / H5: Proposed operational budget is at most 100,000 rows and 50 MiB per file, 120 seconds per run, and a once-daily invocation at 08:00 UTC after exports are ready. Operations reviews local status by 10:00 UTC and acknowledges failures by 12:00 UTC; after that the operations lead manually escalates.

- hypothesis / H6: Run on one trusted local host/account with two allowlisted input roots, a dedicated output root and same-filesystem staging. Only the job may mutate its output root; no symlinks are permitted in resolved input/output paths. An operator grants these local capabilities in configuration.

- hypothesis / H8: A date with an existing valid completed report is immutable: identical input/config returns ALREADY_COMPLETE; changed input/config returns CONFLICT. Corrections require the owner to archive the old date directory outside this job and rerun; no replacement action is implemented.

### W10 · CANCELLED

{"state":"CANCELLED","transitions":[],"failureDisposition":"All outcomes are enumerated below; unhandled internal exceptions go to W11 as BLOCKED/OUTPUT_IO without a success claim.","timeout":"C1-C4 share C1.deadline (120s); C5 has one additional 5s read-only reconciliation budget; C6 attempts local status once then stderr.","retryPolicy":"Zero except W6\u2192W4 after ABSENT, maximum one retry, bounded by deadline and cancellation.","terminalDisposition":"CANCELLED; final absent has been proved if publication was attempted; owned lock released where possible.","guardBindings":"C1.outcome enum READY|BLOCKED|BUSY|CANCELLED; C2.outcome VALID|INVALID|CANCELLED; C3.outcome BUILT|CANCELLED; C4.outcome COMMITTED|ALREADY_COMPLETE|NOT_COMMITTED|UNKNOWN|CONFLICT|CANCELLED; C5.outcome COMMITTED|ABSENT|CONFLICT|UNKNOWN. C1 creates retry_count:int=0; orchestrator increments on W6\u2192W4. cancel_requested:boolean comes only from SIGINT/SIGTERM; deadline_expired:boolean compares monotonic clock with C1.deadline. Exact outcome switches below are exhaustive and exclusive; no guard depends on model text. Before publication, no final report created by this attempt. Post-start cancellation routes via W6. Signal-free timeout routes W11/TIMEOUT."}

Reasoning: Explicit outcome switches and bounded readback preserve local report integrity.

Assumptions:

- H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

Data:

```json
{
  "componentId": "C6",
  "taskIds": [
    "T5"
  ],
  "next": [],
  "decision": false,
  "example": "SIGINT before rename yields no final report, a local status and exit 130."
}
```


Sources:

- context / user-brief: Design a small daily report that joins two CSV files by order ID. One has promised-delivery timestamps and the other actual-delivery timestamps, both ISO UTC. Flag delivered orders more than 24 hours late and export a CSV for the operations team. No emails, remote updates, forecasting or conversational interface.

- hypothesis / H5: Proposed operational budget is at most 100,000 rows and 50 MiB per file, 120 seconds per run, and a once-daily invocation at 08:00 UTC after exports are ready. Operations reviews local status by 10:00 UTC and acknowledges failures by 12:00 UTC; after that the operations lead manually escalates.

- hypothesis / H6: Run on one trusted local host/account with two allowlisted input roots, a dedicated output root and same-filesystem staging. Only the job may mutate its output root; no symlinks are permitted in resolved input/output paths. An operator grants these local capabilities in configuration.

- hypothesis / H8: A date with an existing valid completed report is immutable: identical input/config returns ALREADY_COMPLETE; changed input/config returns CONFLICT. Corrections require the owner to archive the old date directory outside this job and rerun; no replacement action is implemented.

### W11 · BLOCKED

{"state":"BLOCKED","transitions":[],"failureDisposition":"All outcomes are enumerated below; unhandled internal exceptions go to W11 as BLOCKED/OUTPUT_IO without a success claim.","timeout":"C1-C4 share C1.deadline (120s); C5 has one additional 5s read-only reconciliation budget; C6 attempts local status once then stderr.","retryPolicy":"Zero except W6\u2192W4 after ABSENT, maximum one retry, bounded by deadline and cancellation.","terminalDisposition":"BLOCKED with reason and proposed owner; exit 2. Publication ambiguity retains run identity for manual read-only inspection and forbids another blind write.","guardBindings":"C1.outcome enum READY|BLOCKED|BUSY|CANCELLED; C2.outcome VALID|INVALID|CANCELLED; C3.outcome BUILT|CANCELLED; C4.outcome COMMITTED|ALREADY_COMPLETE|NOT_COMMITTED|UNKNOWN|CONFLICT|CANCELLED; C5.outcome COMMITTED|ABSENT|CONFLICT|UNKNOWN. C1 creates retry_count:int=0; orchestrator increments on W6\u2192W4. cancel_requested:boolean comes only from SIGINT/SIGTERM; deadline_expired:boolean compares monotonic clock with C1.deadline. Exact outcome switches below are exhaustive and exclusive; no guard depends on model text. Reason mapping: C1 PATH_DENIED/OUTPUT_IO\u2192OUTPUT_IO, INPUT_IO/FILE_TOO_LARGE/INVALID_DATE\u2192INPUT_IO, BUSY\u2192BUSY; C2 INVALID\u2192INPUT_INVALID; deadline\u2192TIMEOUT; C4 NOT_COMMITTED\u2192OUTPUT_IO, CONFLICT\u2192CONFLICT; C5 CONFLICT\u2192CONFLICT, UNKNOWN\u2192PUBLICATION_UNKNOWN, exhausted ABSENT\u2192OUTPUT_IO. Local status is the handoff, not a remote queue."}

Reasoning: Explicit outcome switches and bounded readback preserve local report integrity.

Assumptions:

- H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

Data:

```json
{
  "componentId": "C6",
  "taskIds": [
    "T5"
  ],
  "next": [],
  "decision": false,
  "example": "Malformed timestamp yields INPUT_INVALID status, no CSV and exit 2."
}
```


Sources:

- context / user-brief: Design a small daily report that joins two CSV files by order ID. One has promised-delivery timestamps and the other actual-delivery timestamps, both ISO UTC. Flag delivered orders more than 24 hours late and export a CSV for the operations team. No emails, remote updates, forecasting or conversational interface.

- hypothesis / H5: Proposed operational budget is at most 100,000 rows and 50 MiB per file, 120 seconds per run, and a once-daily invocation at 08:00 UTC after exports are ready. Operations reviews local status by 10:00 UTC and acknowledges failures by 12:00 UTC; after that the operations lead manually escalates.

- hypothesis / H6: Run on one trusted local host/account with two allowlisted input roots, a dedicated output root and same-filesystem staging. Only the job may mutate its output root; no symlinks are permitted in resolved input/output paths. An operator grants these local capabilities in configuration.

- hypothesis / H8: A date with an existing valid completed report is immutable: identical input/config returns ALREADY_COMPLETE; changed input/config returns CONFLICT. Corrections require the owner to archive the old date directory outside this job and rerun; no replacement action is implemented.

## Required tests

For each ID below, load ../eval-set.json items[id].data.input, .expected and .passRule. These are the full fixture, expected result and exact assertions; no inherited test context is assumed.

- EV1: Positive one-row late delivery
- EV28: Local status failure remains visible
- EV29: Extra data is minimized from outputs and logs
- EV30: Offline parser, invariants and end-to-end suite
- EV31: Daily local report and failure monitor
- EV32: Release gate and deployment filesystem proof
## Acceptance criteria

- Implement the declared contract and all named assertions; do not execute live actions without user authority.
