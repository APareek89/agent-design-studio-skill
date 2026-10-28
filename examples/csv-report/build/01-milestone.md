# Run controller and immutable read

> PASS | DESIGN ONLY. self-review; round 3.

Depends on earlier milestones where their outputs are inputs below. Cross-milestone shared types are read by ID from ../design.json, not copied.

## Selected contracts

### C1 · Run controller and immutable read

CLI run --promised PATH --actual PATH [--report-date D] --out ROOT. Reject future/current day; fail rather than use partial reads. Before and after reading verify same inode/size/mtime_ns; change gives INPUT_IO. Hash exact bytes in memory. Lock mkdir is exclusive; never break an existing lock automatically. SHA256 run_key is hash of compact sorted-key UTF-8 JSON {schema_version,report_date,config_digest,promised_sha256,actual_sha256}; canonical JSON has no spaces. config_digest hashes parser/limits/output/threshold settings, excluding absolute paths. Cancellation checked at bounded row batches and immediately before publication; lock metadata contains pid, start time and run key when known. Whole-run deadline 120s; no read retries. Exact digest key sets/serialization are CTX4; schema_version versions all parser/ID/output behavior. config_digest excludes allowlisted paths and includes only schema_version,threshold_microseconds,max_rows,max_bytes_per_file,deadline_seconds with native JSON numeric types.

Reasoning: Dates, hashes, identity and locks are exact deterministic operations; no natural-language interpretation is needed.

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
  "group": "Code: tools",
  "taskIds": [
    "T1"
  ],
  "inputs": [
    "command: required object {promised_path:absolute path,actual_path:absolute path,output_root:absolute path,report_date:YYYY-MM-DD optional default yesterday UTC}",
    "config: required immutable {schema_version:string,threshold_microseconds:int=86400000000,allowlisted_roots:array[path],max_rows:int=100000,max_bytes_per_file:int=52428800,deadline_seconds:int=120}",
    "clock.now_utc:required aware UTC datetime; signal.cancel_requested:required boolean, initially false"
  ],
  "outputs": [
    "outcome:enum READY|BLOCKED|BUSY|CANCELLED; reason:enum NONE|INVALID_DATE|PATH_DENIED|INPUT_IO|FILE_TOO_LARGE|OUTPUT_IO|LOCK_BUSY|CANCELLED|TIMEOUT",
    "snapshot when READY:required {promised_bytes:bytes,actual_bytes:bytes,promised_sha256:hex64,actual_sha256:hex64,config_digest:hex64,run_key:hex64,report_date:date,window_start:UTC datetime,window_end:UTC datetime,lock_path:path,deadline:monotonic time}",
    "lock_acquired:required boolean; retry_count:required int=0; error:optional {file_role:enum promised|actual|output,row_number:optional int}; no row contents"
  ],
  "whyCode": "Dates, hashes, identity and locks are exact deterministic operations; no natural-language interpretation is needed.",
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

### W1 · ENTRY_ACQUIRE

{"state":"ENTRY_ACQUIRE","transitions":[{"to":"W2","when":"C1.outcome == READY","mode":"exclusive"},{"to":"W10","when":"C1.outcome == CANCELLED","mode":"exclusive"},{"to":"W11","when":"C1.outcome in [BLOCKED,BUSY]","mode":"exclusive"}],"failureDisposition":"All outcomes are enumerated below; unhandled internal exceptions go to W11 as BLOCKED/OUTPUT_IO without a success claim.","timeout":"C1-C4 share C1.deadline (120s); C5 has one additional 5s read-only reconciliation budget; C6 attempts local status once then stderr.","retryPolicy":"Zero except W6\u2192W4 after ABSENT, maximum one retry, bounded by deadline and cancellation.","terminalDisposition":"","guardBindings":"C1.outcome enum READY|BLOCKED|BUSY|CANCELLED; C2.outcome VALID|INVALID|CANCELLED; C3.outcome BUILT|CANCELLED; C4.outcome COMMITTED|ALREADY_COMPLETE|NOT_COMMITTED|UNKNOWN|CONFLICT|CANCELLED; C5.outcome COMMITTED|ABSENT|CONFLICT|UNKNOWN. C1 creates retry_count:int=0; orchestrator increments on W6\u2192W4. cancel_requested:boolean comes only from SIGINT/SIGTERM; deadline_expired:boolean compares monotonic clock with C1.deadline. Exact outcome switches below are exhaustive and exclusive; no guard depends on model text. "}

Reasoning: Explicit outcome switches and bounded readback preserve local report integrity.

Assumptions:

- H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

Data:

```json
{
  "componentId": "C1",
  "taskIds": [
    "T1"
  ],
  "next": [
    "W2",
    "W10",
    "W11"
  ],
  "decision": true,
  "example": "Valid two-file command for 2026-10-27 acquires the date lock then W2."
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
- EV5: Formula-like ID is inert and rejected
- EV7: Delivered order missing promise
- EV8: Invalid actual date
- EV9: Non-UTC actual offset
- EV10: Missing required header
- EV11: Duplicate header
- EV12: CSV row width mismatch
- EV16: Unresolved publication is blocked
- EV17: Concurrent run cannot write
- EV18: Changed input never overwrites report
- EV19: Undelivered and promised-only produce empty valid CSV
- EV20: Revoked local write permission fails safely
- EV21: Symlink path cannot escape input scope
- EV22: Input size exceeds configured bound
- EV24: Exact rerun returns durable no-op
- EV25: Stale lock is never auto-broken
- EV26: Cancellation before publication
- EV27: Cancellation after commit start defers to proof
- EV30: Offline parser, invariants and end-to-end suite
- EV31: Daily local report and failure monitor
- EV32: Release gate and deployment filesystem proof
## Acceptance criteria

- Implement the declared contract and all named assertions; do not execute live actions without user authority.
