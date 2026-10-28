# CSV integrity validator

> PASS | DESIGN ONLY. self-review; round 3.

Depends on earlier milestones where their outputs are inputs below. Cross-milestone shared types are read by ID from ../design.json, not copied.

## Selected contracts

### C2 · CSV integrity validator

CSV parser strict mode, utf-8-sig decode and exact header names; header order may vary and extra columns are ignored, but repeated headers/row-width mismatches fail. Reject all IDs outside H1 and duplicate IDs including identical rows. Validate all promised timestamps and nonblank actual timestamps before filtering. Blank actual is null, not parse failure. Delivered actual IDs absent in promised yield MISSING_PROMISE. Promised-only rows are allowed. Invalid time/date/precision => INVALID_TIMESTAMP; parsed nonzero offset => NON_UTC. No normalization of IDs. All errors terminate the batch; no fallback parser or row skipping. Zero retries.

Reasoning: Typed parsing and one-to-one constraints protect join identity and exact threshold arithmetic.

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
    "T2"
  ],
  "inputs": [
    "snapshot:required C1 READY snapshot",
    "cancel_requested:required boolean; deadline:required monotonic time"
  ],
  "outputs": [
    "outcome:enum VALID|INVALID|CANCELLED; reason:enum NONE|CSV_PARSE|ENCODING|MISSING_HEADER|DUPLICATE_HEADER|ROW_SHAPE|ROW_LIMIT|INVALID_ID|DUPLICATE_ID|MISSING_PROMISE|INVALID_TIMESTAMP|NON_UTC|CANCELLED|TIMEOUT",
    "validated when VALID:required {promised:map[string,int microseconds since epoch],actual:map[string,int microseconds since epoch|null],raw_count_promised:int,raw_count_actual:int}",
    "error when INVALID:required {reason:enum as above,file_role:enum promised|actual,row_number:int}; row 1 means header; no raw field value"
  ],
  "whyCode": "Typed parsing and one-to-one constraints protect join identity and exact threshold arithmetic.",
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

### W2 · VALIDATE

{"state":"VALIDATE","transitions":[{"to":"W3","when":"C2.outcome == VALID","mode":"exclusive"},{"to":"W10","when":"C2.outcome == CANCELLED and C2.reason == CANCELLED","mode":"exclusive"},{"to":"W11","when":"C2.outcome == INVALID or (C2.outcome == CANCELLED and C2.reason == TIMEOUT)","mode":"exclusive"}],"failureDisposition":"All outcomes are enumerated below; unhandled internal exceptions go to W11 as BLOCKED/OUTPUT_IO without a success claim.","timeout":"C1-C4 share C1.deadline (120s); C5 has one additional 5s read-only reconciliation budget; C6 attempts local status once then stderr.","retryPolicy":"Zero except W6\u2192W4 after ABSENT, maximum one retry, bounded by deadline and cancellation.","terminalDisposition":"","guardBindings":"C1.outcome enum READY|BLOCKED|BUSY|CANCELLED; C2.outcome VALID|INVALID|CANCELLED; C3.outcome BUILT|CANCELLED; C4.outcome COMMITTED|ALREADY_COMPLETE|NOT_COMMITTED|UNKNOWN|CONFLICT|CANCELLED; C5.outcome COMMITTED|ABSENT|CONFLICT|UNKNOWN. C1 creates retry_count:int=0; orchestrator increments on W6\u2192W4. cancel_requested:boolean comes only from SIGINT/SIGTERM; deadline_expired:boolean compares monotonic clock with C1.deadline. Exact outcome switches below are exhaustive and exclusive; no guard depends on model text. "}

Reasoning: Explicit outcome switches and bounded readback preserve local report integrity.

Assumptions:

- H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

Data:

```json
{
  "componentId": "C2",
  "taskIds": [
    "T2"
  ],
  "next": [
    "W3",
    "W10",
    "W11"
  ],
  "decision": true,
  "example": "Duplicate order_id O1 returns INVALID/DUPLICATE_ID → W11/INPUT_INVALID."
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
- EV3: Duplicate promised ID fails even with identical rows
- EV4: Duplicate actual ID fails
- EV5: Formula-like ID is inert and rejected
- EV7: Delivered order missing promise
- EV8: Invalid actual date
- EV9: Non-UTC actual offset
- EV10: Missing required header
- EV11: Duplicate header
- EV12: CSV row width mismatch
- EV19: Undelivered and promised-only produce empty valid CSV
- EV20: Revoked local write permission fails safely
- EV21: Symlink path cannot escape input scope
- EV22: Input size exceeds configured bound
- EV30: Offline parser, invariants and end-to-end suite
- EV31: Daily local report and failure monitor
- EV32: Release gate and deployment filesystem proof
## Acceptance criteria

- Implement the declared contract and all named assertions; do not execute live actions without user authority.
