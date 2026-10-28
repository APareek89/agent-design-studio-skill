# Read-only publication reconciler

> PASS | DESIGN ONLY. self-review; round 3.

Depends on earlier milestones where their outputs are inputs below. Cross-milestone shared types are read by ID from ../design.json, not copied.

## Selected contracts

### C5 · Read-only publication reconciler

Read final manifest and CSV under held lock. COMPLETE + expected run_key + actual CSV SHA256 match => COMMITTED. No final directory => ABSENT; readable nonmatching/incomplete final => CONFLICT; read failure or reconciliation deadline => UNKNOWN. One reconciliation attempt, no write. ABSENT may authorize one C4 retry only if retry_count==0 and cancellation/deadline have not fired; increment before retry. Any unresolved ambiguity blocks owned outcome; an expired caller or stale lock never authorizes another publication. Matching proof also requires every expected manifest field from CTX4 (date/schema/config/input hashes and counts), not only status/run_key/output hash; mismatch yields CONFLICT. Read-only C5 never repairs or deletes a final directory.

Reasoning: Read-only evidence distinguishes a committed report from a safe retry and from unresolved ambiguity.

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
  "group": "Code: validation",
  "taskIds": [
    "T4"
  ],
  "inputs": [
    "candidate_final_dir:required absolute path; expected_run_key:required hex64; expected_report_sha256:required hex64",
    "read_capability:required within configured output root; retry_count:int 0..1; reconcile deadline:monotonic time now+5s"
  ],
  "outputs": [
    "outcome:enum COMMITTED|ABSENT|CONFLICT|UNKNOWN; reason:enum NONE|FINAL_ABSENT|FINAL_MISMATCH|READBACK_IO|TIMEOUT",
    "proof when COMMITTED:required same proof shape as C4; observed_final_state:required enum MATCH|ABSENT|MISMATCH|UNREADABLE"
  ],
  "whyCode": "Read-only evidence distinguishes a committed report from a safe retry and from unresolved ambiguity.",
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

### W6 · RECONCILE

{"state":"RECONCILE","transitions":[{"to":"W9","when":"C5.outcome == COMMITTED","mode":"exclusive"},{"to":"W4","when":"C5.outcome == ABSENT and retry_count == 0 and not cancel_requested and not deadline_expired; increment retry_count before invoking C4","mode":"exclusive"},{"to":"W10","when":"C5.outcome == ABSENT and cancel_requested","mode":"exclusive"},{"to":"W11","when":"C5.outcome in [CONFLICT,UNKNOWN] or (C5.outcome == ABSENT and not cancel_requested and (retry_count == 1 or deadline_expired))","mode":"exclusive"}],"failureDisposition":"All outcomes are enumerated below; unhandled internal exceptions go to W11 as BLOCKED/OUTPUT_IO without a success claim.","timeout":"C1-C4 share C1.deadline (120s); C5 has one additional 5s read-only reconciliation budget; C6 attempts local status once then stderr.","retryPolicy":"Zero except W6\u2192W4 after ABSENT, maximum one retry, bounded by deadline and cancellation.","terminalDisposition":"","guardBindings":"C1.outcome enum READY|BLOCKED|BUSY|CANCELLED; C2.outcome VALID|INVALID|CANCELLED; C3.outcome BUILT|CANCELLED; C4.outcome COMMITTED|ALREADY_COMPLETE|NOT_COMMITTED|UNKNOWN|CONFLICT|CANCELLED; C5.outcome COMMITTED|ABSENT|CONFLICT|UNKNOWN. C1 creates retry_count:int=0; orchestrator increments on W6\u2192W4. cancel_requested:boolean comes only from SIGINT/SIGTERM; deadline_expired:boolean compares monotonic clock with C1.deadline. Exact outcome switches below are exhaustive and exclusive; no guard depends on model text. Cancellation after publication begins is deferred until final state known: COMMITTED still wins; ABSENT+CANCEL gives CANCELLED; UNKNOWN remains BLOCKED/PUBLICATION_UNKNOWN."}

Reasoning: Explicit outcome switches and bounded readback preserve local report integrity.

Assumptions:

- H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

Data:

```json
{
  "componentId": "C5",
  "taskIds": [
    "T4"
  ],
  "next": [
    "W9",
    "W4",
    "W10",
    "W11"
  ],
  "decision": true,
  "example": "Post-rename timeout plus matching final hash → W9; absent final permits one bounded retry."
}
```


Sources:

- context / user-brief: Design a small daily report that joins two CSV files by order ID. One has promised-delivery timestamps and the other actual-delivery timestamps, both ISO UTC. Flag delivered orders more than 24 hours late and export a CSV for the operations team. No emails, remote updates, forecasting or conversational interface.

- hypothesis / H5: Proposed operational budget is at most 100,000 rows and 50 MiB per file, 120 seconds per run, and a once-daily invocation at 08:00 UTC after exports are ready. Operations reviews local status by 10:00 UTC and acknowledges failures by 12:00 UTC; after that the operations lead manually escalates.

- hypothesis / H6: Run on one trusted local host/account with two allowlisted input roots, a dedicated output root and same-filesystem staging. Only the job may mutate its output root; no symlinks are permitted in resolved input/output paths. An operator grants these local capabilities in configuration.

- hypothesis / H8: A date with an existing valid completed report is immutable: identical input/config returns ALREADY_COMPLETE; changed input/config returns CONFLICT. Corrections require the owner to archive the old date directory outside this job and rerun; no replacement action is implemented.

## Required tests

For each ID below, load ../eval-set.json items[id].data.input, .expected and .passRule. These are the full fixture, expected result and exact assertions; no inherited test context is assumed.

- EV13: Known pre-publication disk-full
- EV14: Unknown commit reconciles without duplicate publish
- EV15: Proven absent permits one retry
- EV16: Unresolved publication is blocked
- EV20: Revoked local write permission fails safely
- EV22: Input size exceeds configured bound
- EV23: Retry budget cannot loop
- EV26: Cancellation before publication
- EV27: Cancellation after commit start defers to proof
- EV30: Offline parser, invariants and end-to-end suite
- EV31: Daily local report and failure monitor
- EV32: Release gate and deployment filesystem proof
## Acceptance criteria

- Implement the declared contract and all named assertions; do not execute live actions without user authority.
