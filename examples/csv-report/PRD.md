# Daily UTC delivery lateness CSV report

> PASS | DESIGN ONLY. self-review; round 3.

## Original brief

Design a small daily report that joins two CSV files by order ID. One has promised-delivery timestamps and the other actual-delivery timestamps, both ISO UTC. Flag delivered orders more than 24 hours late and export a CSV for the operations team. No emails, remote updates, forecasting or conversational interface.

## Context

- **CTX1 Business decision and actors**: Operations uses the exported daily CSV to identify which delivered orders exceeded their promised delivery timestamp by strictly more than 24 hours. The tool reports facts; it does not decide compensation, contact customers or change orders. Proposed owner roles are not named people or confirmed appointments.
- **CTX2 Trigger, scope and completion**: A manual CLI or existing local scheduler invokes one local batch run with two CSV paths and optional report date. Default is the previous UTC date. Join uses exact order_id equality; no normalization or fuzzy match. Success means one durable date directory with report.csv and a checksum-verified COMPLETE manifest. A valid empty day produces a header-only CSV. Non-goals: emails, messaging, remote updates, forecasting, chat UI, LLMs, customer actions and automatic correction of prior reports.
- **CTX3 Date and data rules**: Validate entire snapshots before filtering. Blank actual timestamps are undelivered and excluded. A delivered actual ID with no promised row fails the run, even outside the report window; promised-only rows are counted as undelivered/not matched. Duplicate IDs in either file fail the entire run even if rows are identical. Only actual rows within [D 00:00:00Z,(D+1) 00:00:00Z) are reported. Signed lateness uses exact integer microseconds: flag iff actual-promised > 86400000000. Actual before promised is valid and not late. Empty values, bad headers/CSV/UTF-8, duplicate header names, invalid timestamps, non-UTC values and unsafe IDs block publication.
- **CTX4 Output and local authority**: CSV columns in order: order_id,promised_delivery_utc,actual_delivery_utc,lateness_seconds,is_more_than_24h_late. Sort by case-sensitive ASCII order_id, preserve leading zeros, normalize timestamps to UTC Z with six fractional digits, emit signed decimal seconds with exactly six decimals and lowercase true/false. UTF-8 without BOM, CRLF records, standard CSV escaping. Local manifest includes schema_version, report_date, config_digest, input SHA-256 hashes, row counts, excluded-undelivered/out-of-window counts, report SHA-256, status COMPLETE and run_key. No raw rows in logs. This design exercise writes only design artifacts; running or scheduling the business report is separate implementation work. Manifest is exactly {schema_version:string="delivery-report-v1",report_date:YYYY-MM-DD,config_digest:hex64,promised_sha256:hex64,actual_sha256:hex64,raw_count_promised:int>=0,raw_count_actual:int>=0,rows:int>=0,flagged_rows:int>=0,excluded_undelivered:int>=0,excluded_out_of_window:int>=0,promised_only_rows:int>=0,report_sha256:hex64,status:string="COMPLETE",run_key:hex64}; no timestamp or absolute path is included in this deterministic object. Serialize manifest JSON with sorted keys and compact separators in UTF-8 followed by one LF. config_digest = SHA256 of compact sorted-key UTF-8 JSON with exactly {schema_version,threshold_microseconds,max_rows,max_bytes_per_file,deadline_seconds}; parser/ID/output contracts are versioned by schema_version; allowlisted paths are deployment capabilities, excluded from digest. run_key = SHA256 of compact sorted-key UTF-8 JSON with exactly {schema_version,report_date,config_digest,promised_sha256,actual_sha256}. No LF in either hashed JSON input. Fields use the typed values in C1/C2/C3, not stringified numbers.
- **CTX5 Quality and value measurements**: R1 defines daily record accuracy, publication completeness and operations review-time KPIs. Baselines are unknown. Hypothesis: exact deterministic fixtures pass 100%; all published files have valid manifests; reviewer effort decreases without any missed/extra flagged rows. Actual business impact requires future shadow/manual comparison and the R5 experiment; no savings or production accuracy is claimed.

## Tasks

- **T0 Produce the daily operations CSV**: Acquire and snapshot → validate → join/classify → publish → record a local outcome. On failure or cancellation stop publication and emit an owned local outcome.
- **T1 Acquire the local run and immutable input bytes**: Resolve configured paths and permissions; derive UTC window, reject current/future date, acquire exclusive per-date directory lock, bound sizes and read immutable bytes. Record hashes after reading; do not reread changing files.
- **T2 Validate both CSV snapshots**: Parse the entire files using H1/H4, enforce required unique headers and ID uniqueness and ensure delivered actual IDs have promised rows. Reject all malformed or contradictory inputs with exact reason and row number.
- **T3 Join delivered orders and compute strict lateness**: Exact string join, then daily-window filtering; compute signed microseconds without floats; build sorted rows, counts and deterministic CSV bytes.
- **T4 Publish a complete immutable report**: Under the date lock, compare any existing completed date directory. Stage CSV and COMPLETE manifest, fsync files and staging directory, then rename date directory and fsync parent. Reconcile uncertain publication before any retry.
- **T5 Record completion, cancellation or owned failure**: Write local status safely; release acquired lock on normal exit. Operations inspects the local result each day. Failure gets proposed owner, acknowledgement deadline, next action and visible state. Unknown publication and stale locks require manual inspection.
- **A1 Immutable CSV evidence**: Two operator-provided local CSV files; exact content hashes produced by C1.
- **A2 Run policy and report identity**: Versioned local config: schema_version=delivery-report-v1, threshold_microseconds=86400000000, UTC report date, allowlisted roots and H1/H4 parser profile; no live remote policy.
- **A3 Durable publication and failure state**: Dedicated local output root, per-date lock, staging directory, committed manifest/CSV and status record; C4/C5 produce record evidence.

## Components

- **C1 Run controller and immutable read**: CLI run --promised PATH --actual PATH [--report-date D] --out ROOT. Reject future/current day; fail rather than use partial reads. Before and after reading verify same inode/size/mtime_ns; change gives INPUT_IO. Hash exact bytes in memory. Lock mkdir is exclusive; never break an existing lock automatically. SHA256 run_key is hash of compact sorted-key UTF-8 JSON {schema_version,report_date,config_digest,promised_sha256,actual_sha256}; canonical JSON has no spaces. config_digest hashes parser/limits/output/threshold settings, excluding absolute paths. Cancellation checked at bounded row batches and immediately before publication; lock metadata contains pid, start time and run key when known. Whole-run deadline 120s; no read retries. Exact digest key sets/serialization are CTX4; schema_version versions all parser/ID/output behavior. config_digest excludes allowlisted paths and includes only schema_version,threshold_microseconds,max_rows,max_bytes_per_file,deadline_seconds with native JSON numeric types.
- **C2 CSV integrity validator**: CSV parser strict mode, utf-8-sig decode and exact header names; header order may vary and extra columns are ignored, but repeated headers/row-width mismatches fail. Reject all IDs outside H1 and duplicate IDs including identical rows. Validate all promised timestamps and nonblank actual timestamps before filtering. Blank actual is null, not parse failure. Delivered actual IDs absent in promised yield MISSING_PROMISE. Promised-only rows are allowed. Invalid time/date/precision => INVALID_TIMESTAMP; parsed nonzero offset => NON_UTC. No normalization of IDs. All errors terminate the batch; no fallback parser or row skipping. Zero retries.
- **C3 Exact join and renderer**: For each actual-map ID with nonnull timestamp use matching promised timestamp; include iff start<=actual<end. Calculate signed delta as int microseconds; flag delta>86400000000. Decimal seconds formatting has exactly six digits, including negative values; never round before comparison. Canonical timestamps use six fractional digits and Z. Sort ASCII order IDs, UTF-8 no BOM and CRLF including final record; all columns deterministic. Blank-actual records count as excluded_undelivered; promised-only_rows counts promised IDs absent from actual map. Empty valid input produces just the header. Check deadline/cancel every 1000 rows. No retries.
- **C4 Atomic local publisher**: Final directory ROOT/YYYY-MM-DD contains report.csv and manifest.json. Under acquired per-date lock, existing COMPLETE manifest with same run_key and matching CSV hash => ALREADY_COMPLETE; any differing or incomplete final directory => CONFLICT. Stage at ROOT/.staging-<date>-<run_key>-<pid>-a<retry_count>; create files exclusively, fsync each and directory. Manifest schema is in CTX4; input counts are C2/C3 outputs. Recheck output-root permission and lock ownership before rename. Publish by same-filesystem directory rename then fsync output root; any exception after rename begins => UNKNOWN and C5 reconciliation, never immediate retry. Before rename, cancellation deletes staging and returns CANCELLED; failures known before rename return NOT_COMMITTED. After rename begins defer cancellation until reconciliation determines whether published. Stage no later than deadline; uncertain timeout is UNKNOWN. No network, input mutation or automatic overwrite. The exact typed manifest/canonical JSON is CTX4. Before ALREADY_COMPLETE verify all stored date/schema/config/input hashes and derived counts against the current expected manifest, plus actual report hash; any discrepancy is CONFLICT. A retry uses its fresh -a1 directory; best-effort remove the owned prior -a0 stage after ABSENT proof, but cleanup failure never authorizes reading/reusing that stage. No automatic deletion of another run stage. Any cancellation signal received after rename begins makes C4 return UNKNOWN, even if rename appears successful, so W6 proves COMMITTED or ABSENT before selecting terminal; no post-start CANCELLED outcome bypasses readback.
- **C5 Read-only publication reconciler**: Read final manifest and CSV under held lock. COMPLETE + expected run_key + actual CSV SHA256 match => COMMITTED. No final directory => ABSENT; readable nonmatching/incomplete final => CONFLICT; read failure or reconciliation deadline => UNKNOWN. One reconciliation attempt, no write. ABSENT may authorize one C4 retry only if retry_count==0 and cancellation/deadline have not fired; increment before retry. Any unresolved ambiguity blocks owned outcome; an expired caller or stale lock never authorizes another publication. Matching proof also requires every expected manifest field from CTX4 (date/schema/config/input hashes and counts), not only status/run_key/output hash; mismatch yields CONFLICT. Read-only C5 never repairs or deletes a final directory.
- **C6 Local outcome recorder**: Append a unique per-invocation local JSON status under ROOT/status (exclusive create + fsync), storing report date, run_key when known, terminal/reason, proof, proposed owner, ack_due_utc and manual next action. COMPLETE exits 0 only with C4/C5 proof; BLOCKED exits 2, CANCELLED exits 130. If status write fails emit structured stderr and status_proof=STDERR_ONLY; this does not convert a proved committed report to failure. Remove owned lock at normal exit; cleanup failure is visible stderr/status warning. Hard crash may leave stale lock: operator confirms no running process and read-only checks final manifest before manual lock removal. Operations checks local statuses by 10:00 UTC, acknowledges failure in a separate local operating log by 12:00 UTC, then manually escalates to lead if overdue. No automatic messaging and no indefinite waiting loop.

## Workflow

- **W1 ENTRY_ACQUIRE**: {"state":"ENTRY_ACQUIRE","transitions":[{"to":"W2","when":"C1.outcome == READY","mode":"exclusive"},{"to":"W10","when":"C1.outcome == CANCELLED","mode":"exclusive"},{"to":"W11","when":"C1.outcome in [BLOCKED,BUSY]","mode":"exclusive"}],"failureDisposition":"All outcomes are enumerated below; unhandled internal exceptions go to W11 as BLOCKED/OUTPUT_IO without a success claim.","timeout":"C1-C4 share C1.deadline (120s); C5 has one additional 5s read-only reconciliation budget; C6 attempts local status once then stderr.","retryPolicy":"Zero except W6\u2192W4 after ABSENT, maximum one retry, bounded by deadline and cancellation.","terminalDisposition":"","guardBindings":"C1.outcome enum READY|BLOCKED|BUSY|CANCELLED; C2.outcome VALID|INVALID|CANCELLED; C3.outcome BUILT|CANCELLED; C4.outcome COMMITTED|ALREADY_COMPLETE|NOT_COMMITTED|UNKNOWN|CONFLICT|CANCELLED; C5.outcome COMMITTED|ABSENT|CONFLICT|UNKNOWN. C1 creates retry_count:int=0; orchestrator increments on W6\u2192W4. cancel_requested:boolean comes only from SIGINT/SIGTERM; deadline_expired:boolean compares monotonic clock with C1.deadline. Exact outcome switches below are exhaustive and exclusive; no guard depends on model text. "}
- **W2 VALIDATE**: {"state":"VALIDATE","transitions":[{"to":"W3","when":"C2.outcome == VALID","mode":"exclusive"},{"to":"W10","when":"C2.outcome == CANCELLED and C2.reason == CANCELLED","mode":"exclusive"},{"to":"W11","when":"C2.outcome == INVALID or (C2.outcome == CANCELLED and C2.reason == TIMEOUT)","mode":"exclusive"}],"failureDisposition":"All outcomes are enumerated below; unhandled internal exceptions go to W11 as BLOCKED/OUTPUT_IO without a success claim.","timeout":"C1-C4 share C1.deadline (120s); C5 has one additional 5s read-only reconciliation budget; C6 attempts local status once then stderr.","retryPolicy":"Zero except W6\u2192W4 after ABSENT, maximum one retry, bounded by deadline and cancellation.","terminalDisposition":"","guardBindings":"C1.outcome enum READY|BLOCKED|BUSY|CANCELLED; C2.outcome VALID|INVALID|CANCELLED; C3.outcome BUILT|CANCELLED; C4.outcome COMMITTED|ALREADY_COMPLETE|NOT_COMMITTED|UNKNOWN|CONFLICT|CANCELLED; C5.outcome COMMITTED|ABSENT|CONFLICT|UNKNOWN. C1 creates retry_count:int=0; orchestrator increments on W6\u2192W4. cancel_requested:boolean comes only from SIGINT/SIGTERM; deadline_expired:boolean compares monotonic clock with C1.deadline. Exact outcome switches below are exhaustive and exclusive; no guard depends on model text. "}
- **W3 JOIN_RENDER**: {"state":"JOIN_RENDER","transitions":[{"to":"W4","when":"C3.outcome == BUILT","mode":"exclusive"},{"to":"W10","when":"C3.outcome == CANCELLED and C3.reason == CANCELLED","mode":"exclusive"},{"to":"W11","when":"C3.outcome == CANCELLED and C3.reason == TIMEOUT","mode":"exclusive"}],"failureDisposition":"All outcomes are enumerated below; unhandled internal exceptions go to W11 as BLOCKED/OUTPUT_IO without a success claim.","timeout":"C1-C4 share C1.deadline (120s); C5 has one additional 5s read-only reconciliation budget; C6 attempts local status once then stderr.","retryPolicy":"Zero except W6\u2192W4 after ABSENT, maximum one retry, bounded by deadline and cancellation.","terminalDisposition":"","guardBindings":"C1.outcome enum READY|BLOCKED|BUSY|CANCELLED; C2.outcome VALID|INVALID|CANCELLED; C3.outcome BUILT|CANCELLED; C4.outcome COMMITTED|ALREADY_COMPLETE|NOT_COMMITTED|UNKNOWN|CONFLICT|CANCELLED; C5.outcome COMMITTED|ABSENT|CONFLICT|UNKNOWN. C1 creates retry_count:int=0; orchestrator increments on W6\u2192W4. cancel_requested:boolean comes only from SIGINT/SIGTERM; deadline_expired:boolean compares monotonic clock with C1.deadline. Exact outcome switches below are exhaustive and exclusive; no guard depends on model text. "}
- **W4 STAGE_PUBLISH**: {"state":"STAGE_PUBLISH","transitions":[{"to":"W9","when":"C4.outcome in [COMMITTED,ALREADY_COMPLETE]","mode":"exclusive"},{"to":"W6","when":"C4.outcome == UNKNOWN","mode":"exclusive"},{"to":"W10","when":"C4.outcome == CANCELLED","mode":"exclusive"},{"to":"W11","when":"C4.outcome in [NOT_COMMITTED,CONFLICT]","mode":"exclusive"}],"failureDisposition":"All outcomes are enumerated below; unhandled internal exceptions go to W11 as BLOCKED/OUTPUT_IO without a success claim.","timeout":"C1-C4 share C1.deadline (120s); C5 has one additional 5s read-only reconciliation budget; C6 attempts local status once then stderr.","retryPolicy":"Zero except W6\u2192W4 after ABSENT, maximum one retry, bounded by deadline and cancellation.","terminalDisposition":"","guardBindings":"C1.outcome enum READY|BLOCKED|BUSY|CANCELLED; C2.outcome VALID|INVALID|CANCELLED; C3.outcome BUILT|CANCELLED; C4.outcome COMMITTED|ALREADY_COMPLETE|NOT_COMMITTED|UNKNOWN|CONFLICT|CANCELLED; C5.outcome COMMITTED|ABSENT|CONFLICT|UNKNOWN. C1 creates retry_count:int=0; orchestrator increments on W6\u2192W4. cancel_requested:boolean comes only from SIGINT/SIGTERM; deadline_expired:boolean compares monotonic clock with C1.deadline. Exact outcome switches below are exhaustive and exclusive; no guard depends on model text. "}
- **W6 RECONCILE**: {"state":"RECONCILE","transitions":[{"to":"W9","when":"C5.outcome == COMMITTED","mode":"exclusive"},{"to":"W4","when":"C5.outcome == ABSENT and retry_count == 0 and not cancel_requested and not deadline_expired; increment retry_count before invoking C4","mode":"exclusive"},{"to":"W10","when":"C5.outcome == ABSENT and cancel_requested","mode":"exclusive"},{"to":"W11","when":"C5.outcome in [CONFLICT,UNKNOWN] or (C5.outcome == ABSENT and not cancel_requested and (retry_count == 1 or deadline_expired))","mode":"exclusive"}],"failureDisposition":"All outcomes are enumerated below; unhandled internal exceptions go to W11 as BLOCKED/OUTPUT_IO without a success claim.","timeout":"C1-C4 share C1.deadline (120s); C5 has one additional 5s read-only reconciliation budget; C6 attempts local status once then stderr.","retryPolicy":"Zero except W6\u2192W4 after ABSENT, maximum one retry, bounded by deadline and cancellation.","terminalDisposition":"","guardBindings":"C1.outcome enum READY|BLOCKED|BUSY|CANCELLED; C2.outcome VALID|INVALID|CANCELLED; C3.outcome BUILT|CANCELLED; C4.outcome COMMITTED|ALREADY_COMPLETE|NOT_COMMITTED|UNKNOWN|CONFLICT|CANCELLED; C5.outcome COMMITTED|ABSENT|CONFLICT|UNKNOWN. C1 creates retry_count:int=0; orchestrator increments on W6\u2192W4. cancel_requested:boolean comes only from SIGINT/SIGTERM; deadline_expired:boolean compares monotonic clock with C1.deadline. Exact outcome switches below are exhaustive and exclusive; no guard depends on model text. Cancellation after publication begins is deferred until final state known: COMMITTED still wins; ABSENT+CANCEL gives CANCELLED; UNKNOWN remains BLOCKED/PUBLICATION_UNKNOWN."}
- **W9 COMPLETE**: {"state":"COMPLETE","transitions":[],"failureDisposition":"All outcomes are enumerated below; unhandled internal exceptions go to W11 as BLOCKED/OUTPUT_IO without a success claim.","timeout":"C1-C4 share C1.deadline (120s); C5 has one additional 5s read-only reconciliation budget; C6 attempts local status once then stderr.","retryPolicy":"Zero except W6\u2192W4 after ABSENT, maximum one retry, bounded by deadline and cancellation.","terminalDisposition":"COMPLETE with required proof; C6 status write failure yields STDERR_ONLY and a warning; never invents a report proof.","guardBindings":"C1.outcome enum READY|BLOCKED|BUSY|CANCELLED; C2.outcome VALID|INVALID|CANCELLED; C3.outcome BUILT|CANCELLED; C4.outcome COMMITTED|ALREADY_COMPLETE|NOT_COMMITTED|UNKNOWN|CONFLICT|CANCELLED; C5.outcome COMMITTED|ABSENT|CONFLICT|UNKNOWN. C1 creates retry_count:int=0; orchestrator increments on W6\u2192W4. cancel_requested:boolean comes only from SIGINT/SIGTERM; deadline_expired:boolean compares monotonic clock with C1.deadline. Exact outcome switches below are exhaustive and exclusive; no guard depends on model text. The reason is READY for new/reconciled commit or ALREADY_COMPLETE for identical rerun."}
- **W10 CANCELLED**: {"state":"CANCELLED","transitions":[],"failureDisposition":"All outcomes are enumerated below; unhandled internal exceptions go to W11 as BLOCKED/OUTPUT_IO without a success claim.","timeout":"C1-C4 share C1.deadline (120s); C5 has one additional 5s read-only reconciliation budget; C6 attempts local status once then stderr.","retryPolicy":"Zero except W6\u2192W4 after ABSENT, maximum one retry, bounded by deadline and cancellation.","terminalDisposition":"CANCELLED; final absent has been proved if publication was attempted; owned lock released where possible.","guardBindings":"C1.outcome enum READY|BLOCKED|BUSY|CANCELLED; C2.outcome VALID|INVALID|CANCELLED; C3.outcome BUILT|CANCELLED; C4.outcome COMMITTED|ALREADY_COMPLETE|NOT_COMMITTED|UNKNOWN|CONFLICT|CANCELLED; C5.outcome COMMITTED|ABSENT|CONFLICT|UNKNOWN. C1 creates retry_count:int=0; orchestrator increments on W6\u2192W4. cancel_requested:boolean comes only from SIGINT/SIGTERM; deadline_expired:boolean compares monotonic clock with C1.deadline. Exact outcome switches below are exhaustive and exclusive; no guard depends on model text. Before publication, no final report created by this attempt. Post-start cancellation routes via W6. Signal-free timeout routes W11/TIMEOUT."}
- **W11 BLOCKED**: {"state":"BLOCKED","transitions":[],"failureDisposition":"All outcomes are enumerated below; unhandled internal exceptions go to W11 as BLOCKED/OUTPUT_IO without a success claim.","timeout":"C1-C4 share C1.deadline (120s); C5 has one additional 5s read-only reconciliation budget; C6 attempts local status once then stderr.","retryPolicy":"Zero except W6\u2192W4 after ABSENT, maximum one retry, bounded by deadline and cancellation.","terminalDisposition":"BLOCKED with reason and proposed owner; exit 2. Publication ambiguity retains run identity for manual read-only inspection and forbids another blind write.","guardBindings":"C1.outcome enum READY|BLOCKED|BUSY|CANCELLED; C2.outcome VALID|INVALID|CANCELLED; C3.outcome BUILT|CANCELLED; C4.outcome COMMITTED|ALREADY_COMPLETE|NOT_COMMITTED|UNKNOWN|CONFLICT|CANCELLED; C5.outcome COMMITTED|ABSENT|CONFLICT|UNKNOWN. C1 creates retry_count:int=0; orchestrator increments on W6\u2192W4. cancel_requested:boolean comes only from SIGINT/SIGTERM; deadline_expired:boolean compares monotonic clock with C1.deadline. Exact outcome switches below are exhaustive and exclusive; no guard depends on model text. Reason mapping: C1 PATH_DENIED/OUTPUT_IO\u2192OUTPUT_IO, INPUT_IO/FILE_TOO_LARGE/INVALID_DATE\u2192INPUT_IO, BUSY\u2192BUSY; C2 INVALID\u2192INPUT_INVALID; deadline\u2192TIMEOUT; C4 NOT_COMMITTED\u2192OUTPUT_IO, CONFLICT\u2192CONFLICT; C5 CONFLICT\u2192CONFLICT, UNKNOWN\u2192PUBLICATION_UNKNOWN, exhausted ABSENT\u2192OUTPUT_IO. Local status is the handoff, not a remote queue."}

## Framework

### F1 · Code workflow fit

A deterministic Python CLI is the complete first release; zero agent framework and zero model calls.

Reasoning: Choose only capabilities required by the brief; external products remain unverified candidates.

Assumptions:

- H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

Data:

```json
{
  "category": "fit",
  "taskIds": [
    "T1",
    "T2",
    "T3",
    "T4",
    "T5"
  ],
  "choice": "A deterministic Python CLI is the complete first release; zero agent framework and zero model calls.",
  "alternatives": [
    "Rejected LLM/multi-agent system: adds parsing uncertainty, credentials, cost and orchestration with no judgement task."
  ],
  "tradeoffs": "Both options assessed on exact join/date correctness, local deployment, retries/audit and operating burden; code directly satisfies every criterion. No vendor capability claim is needed.",
  "permission": "none",
  "blastRadius": "No external systems.",
  "approvalRule": "Use locally granted path capabilities; no account connection or remote write. Proposed owners confirm launch prerequisites, not this design review.",
  "leastPrivilege": "Read-only configured input roots; create/write/delete staging and own lock/status only inside dedicated output root; never alter inputs or existing committed date reports. No network capability or secrets.",
  "aws": "If future hosting is requested: private object/file storage plus a scheduled container, unverified candidate requiring equivalent immutable-pair, atomic-publication, permission and retention tests; no current integration.",
  "gcp": "If future hosting is requested: private object/file storage plus a scheduled container, unverified candidate on the same criteria; no current integration.",
  "azure": "If future hosting is requested: private object/file storage plus a scheduled container, unverified candidate on the same criteria; no current integration.",
  "openSource": "Chosen: Python 3 standard library csv, datetime, decimal/integer formatting, hashlib, json, pathlib/os; local filesystem. Existing local scheduler optional after deployment verification; no paid SDK or LLM service."
}
```


Sources:

- context / user-brief: Design a small daily report that joins two CSV files by order ID. One has promised-delivery timestamps and the other actual-delivery timestamps, both ISO UTC. Flag delivered orders more than 24 hours late and export a CSV for the operations team. No emails, remote updates, forecasting or conversational interface.

- hypothesis / H1: The proposed CSV contract is UTF-8 with optional BOM, comma delimiter and one header; promised columns are order_id,promised_delivery_utc and actual columns are order_id,actual_delivery_utc. Extra columns are ignored. IDs are case-sensitive ASCII [A-Za-z0-9][A-Za-z0-9_-]{0,63}, unique within each file; empty or padded IDs are errors.

- hypothesis / H4: Accepted timestamps use YYYY-MM-DDTHH:MM:SS[.ffffff]Z or +00:00, with 1-6 fractional digits, valid Gregorian dates and seconds 00-59. Empty actual means undelivered; non-UTC offsets, missing promised values, leap seconds and greater precision fail validation.

### F2 · One-host durable batch architecture

C1→C2→C3→C4 with C5 reconciliation and C6 local terminal status. Per-date exclusive lock, content-bound run identity and immutable report directory.

Reasoning: Choose only capabilities required by the brief; external products remain unverified candidates.

Assumptions:

- H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

Data:

```json
{
  "category": "architecture",
  "taskIds": [
    "T1",
    "T2",
    "T3",
    "T4",
    "T5"
  ],
  "choice": "C1→C2→C3→C4 with C5 reconciliation and C6 local terminal status. Per-date exclusive lock, content-bound run identity and immutable report directory.",
  "alternatives": [
    "Rejected database/workflow service for this small local report: extra infrastructure and operational state without a remote or long-running approval requirement."
  ],
  "tradeoffs": "Local filesystem behavior is a launch dependency; a future distributed execution would require a new concurrency/publication design.",
  "permission": "write",
  "blastRadius": "Only the configured local report root.",
  "approvalRule": "Use locally granted path capabilities; no account connection or remote write. Proposed owners confirm launch prerequisites, not this design review.",
  "leastPrivilege": "Read-only configured input roots; create/write/delete staging and own lock/status only inside dedicated output root; never alter inputs or existing committed date reports. No network capability or secrets.",
  "aws": "If future hosting is requested: private object/file storage plus a scheduled container, unverified candidate requiring equivalent immutable-pair, atomic-publication, permission and retention tests; no current integration.",
  "gcp": "If future hosting is requested: private object/file storage plus a scheduled container, unverified candidate on the same criteria; no current integration.",
  "azure": "If future hosting is requested: private object/file storage plus a scheduled container, unverified candidate on the same criteria; no current integration.",
  "openSource": "Chosen: Python 3 standard library csv, datetime, decimal/integer formatting, hashlib, json, pathlib/os; local filesystem. Existing local scheduler optional after deployment verification; no paid SDK or LLM service."
}
```


Sources:

- context / user-brief: Design a small daily report that joins two CSV files by order ID. One has promised-delivery timestamps and the other actual-delivery timestamps, both ISO UTC. Flag delivered orders more than 24 hours late and export a CSV for the operations team. No emails, remote updates, forecasting or conversational interface.

- hypothesis / H6: Run on one trusted local host/account with two allowlisted input roots, a dedicated output root and same-filesystem staging. Only the job may mutate its output root; no symlinks are permitted in resolved input/output paths. An operator grants these local capabilities in configuration.

- hypothesis / H8: A date with an existing valid completed report is immutable: identical input/config returns ALREADY_COMPLETE; changed input/config returns CONFLICT. Corrections require the owner to archive the old date directory outside this job and rerun; no replacement action is implemented.

### F3 · Schedule and bounded orchestration

Invoke CLI manually first; use an existing local daily scheduler at proposed 08:00 UTC after export availability is verified. One run bounded to 120s plus 5s ambiguous-commit readback.

Reasoning: Choose only capabilities required by the brief; external products remain unverified candidates.

Assumptions:

- H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

Data:

```json
{
  "category": "orchestration",
  "taskIds": [
    "T1",
    "T2",
    "T3",
    "T4",
    "T5"
  ],
  "choice": "Invoke CLI manually first; use an existing local daily scheduler at proposed 08:00 UTC after export availability is verified. One run bounded to 120s plus 5s ambiguous-commit readback.",
  "alternatives": [
    "Rejected cron-like remote service provisioning: outside design scope and not necessary for a small local job."
  ],
  "tradeoffs": "Manual invocation and an existing scheduler have the same validation, locks, exact data and publication rules; scheduling only changes trigger ownership. No automation is created in this exercise.",
  "permission": "none",
  "blastRadius": "One run for one completed UTC date.",
  "approvalRule": "Use locally granted path capabilities; no account connection or remote write. Proposed owners confirm launch prerequisites, not this design review.",
  "leastPrivilege": "Read-only configured input roots; create/write/delete staging and own lock/status only inside dedicated output root; never alter inputs or existing committed date reports. No network capability or secrets.",
  "aws": "If future hosting is requested: private object/file storage plus a scheduled container, unverified candidate requiring equivalent immutable-pair, atomic-publication, permission and retention tests; no current integration.",
  "gcp": "If future hosting is requested: private object/file storage plus a scheduled container, unverified candidate on the same criteria; no current integration.",
  "azure": "If future hosting is requested: private object/file storage plus a scheduled container, unverified candidate on the same criteria; no current integration.",
  "openSource": "Chosen: Python 3 standard library csv, datetime, decimal/integer formatting, hashlib, json, pathlib/os; local filesystem. Existing local scheduler optional after deployment verification; no paid SDK or LLM service."
}
```


Sources:

- context / user-brief: Design a small daily report that joins two CSV files by order ID. One has promised-delivery timestamps and the other actual-delivery timestamps, both ISO UTC. Flag delivered orders more than 24 hours late and export a CSV for the operations team. No emails, remote updates, forecasting or conversational interface.

- hypothesis / H5: Proposed operational budget is at most 100,000 rows and 50 MiB per file, 120 seconds per run, and a once-daily invocation at 08:00 UTC after exports are ready. Operations reviews local status by 10:00 UTC and acknowledges failures by 12:00 UTC; after that the operations lead manually escalates.

### F4 · Filesystem authority and inert inputs

Treat CSV content as untrusted data; strict parser/ID profile, no eval or shell interpolation. Resolve paths against allowlisted roots, forbid symlinks, fresh capability checks and exclusive creation.

Reasoning: Choose only capabilities required by the brief; external products remain unverified candidates.

Assumptions:

- H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H2: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

Data:

```json
{
  "category": "permission",
  "taskIds": [
    "T1",
    "T2",
    "T3",
    "T4",
    "T5"
  ],
  "choice": "Treat CSV content as untrusted data; strict parser/ID profile, no eval or shell interpolation. Resolve paths against allowlisted roots, forbid symlinks, fresh capability checks and exclusive creation.",
  "alternatives": [
    "Rejected processing arbitrary paths and preserving formula-like IDs directly in spreadsheet CSV: unclear scope and formula risk."
  ],
  "tradeoffs": "The narrow ID profile is a confirmable source-contract dependency. Wrong-namespace/stale snapshot risk still needs the source-owner procedure; hashes establish byte identity, not business provenance.",
  "permission": "write",
  "blastRadius": "Input bytes read only; local output and status contain order identifiers and timestamps.",
  "approvalRule": "Use locally granted path capabilities; no account connection or remote write. Proposed owners confirm launch prerequisites, not this design review.",
  "leastPrivilege": "Read-only configured input roots; create/write/delete staging and own lock/status only inside dedicated output root; never alter inputs or existing committed date reports. No network capability or secrets.",
  "aws": "If future hosting is requested: private object/file storage plus a scheduled container, unverified candidate requiring equivalent immutable-pair, atomic-publication, permission and retention tests; no current integration.",
  "gcp": "If future hosting is requested: private object/file storage plus a scheduled container, unverified candidate on the same criteria; no current integration.",
  "azure": "If future hosting is requested: private object/file storage plus a scheduled container, unverified candidate on the same criteria; no current integration.",
  "openSource": "Chosen: Python 3 standard library csv, datetime, decimal/integer formatting, hashlib, json, pathlib/os; local filesystem. Existing local scheduler optional after deployment verification; no paid SDK or LLM service."
}
```


Sources:

- context / user-brief: Design a small daily report that joins two CSV files by order ID. One has promised-delivery timestamps and the other actual-delivery timestamps, both ISO UTC. Flag delivered orders more than 24 hours late and export a CSV for the operations team. No emails, remote updates, forecasting or conversational interface.

- hypothesis / H1: The proposed CSV contract is UTF-8 with optional BOM, comma delimiter and one header; promised columns are order_id,promised_delivery_utc and actual columns are order_id,actual_delivery_utc. Extra columns are ignored. IDs are case-sensitive ASCII [A-Za-z0-9][A-Za-z0-9_-]{0,63}, unique within each file; empty or padded IDs are errors.

- hypothesis / H2: Operations supplies two complete snapshots from the same order namespace and consistent export cutoff after the requested day ends. CSVs have no authoritative dataset/as-of metadata; the job cannot independently prove their business freshness or shared provenance.

- hypothesis / H6: Run on one trusted local host/account with two allowlisted input roots, a dedicated output root and same-filesystem staging. Only the job may mutate its output root; no symlinks are permitted in resolved input/output paths. An operator grants these local capabilities in configuration.

### F5 · Minimized data and retention

Memory-only snapshots; retain output CSV, hashes, count/manifest and error codes/row numbers locally for proposed 30 days. No customer names, addresses or raw rows in logs.

Reasoning: Choose only capabilities required by the brief; external products remain unverified candidates.

Assumptions:

- H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H7: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

Data:

```json
{
  "category": "data",
  "taskIds": [
    "T1",
    "T2",
    "T3",
    "T4",
    "T5"
  ],
  "choice": "Memory-only snapshots; retain output CSV, hashes, count/manifest and error codes/row numbers locally for proposed 30 days. No customer names, addresses or raw rows in logs.",
  "alternatives": [
    "Rejected cloud warehouse/vector store: no retrieval or analytics need and extra data movement."
  ],
  "tradeoffs": "Memory/row limits are provisional; real export profiling and retention approval remain launch gates. All cloud alternatives face the same access, schema, provenance, durability, deletion and observability criteria; no price or reliability assumptions are asserted.",
  "permission": "write",
  "blastRadius": "A single operator-controlled filesystem; no upload.",
  "approvalRule": "Use locally granted path capabilities; no account connection or remote write. Proposed owners confirm launch prerequisites, not this design review.",
  "leastPrivilege": "Read-only configured input roots; create/write/delete staging and own lock/status only inside dedicated output root; never alter inputs or existing committed date reports. No network capability or secrets.",
  "aws": "If future hosting is requested: private object/file storage plus a scheduled container, unverified candidate requiring equivalent immutable-pair, atomic-publication, permission and retention tests; no current integration.",
  "gcp": "If future hosting is requested: private object/file storage plus a scheduled container, unverified candidate on the same criteria; no current integration.",
  "azure": "If future hosting is requested: private object/file storage plus a scheduled container, unverified candidate on the same criteria; no current integration.",
  "openSource": "Chosen: Python 3 standard library csv, datetime, decimal/integer formatting, hashlib, json, pathlib/os; local filesystem. Existing local scheduler optional after deployment verification; no paid SDK or LLM service."
}
```


Sources:

- context / user-brief: Design a small daily report that joins two CSV files by order ID. One has promised-delivery timestamps and the other actual-delivery timestamps, both ISO UTC. Flag delivered orders more than 24 hours late and export a CSV for the operations team. No emails, remote updates, forecasting or conversational interface.

- hypothesis / H5: Proposed operational budget is at most 100,000 rows and 50 MiB per file, 120 seconds per run, and a once-daily invocation at 08:00 UTC after exports are ready. Operations reviews local status by 10:00 UTC and acknowledges failures by 12:00 UTC; after that the operations lead manually escalates.

- hypothesis / H7: Keep committed CSVs, manifests and local failure records for 30 days. Do not copy raw input files; persist hashes, counts and error row numbers without row contents. Delete expired files locally only through a separate operator-maintained procedure.


## Models


## Fmea

- **FM1 Wrong or duplicate order identity**: Hypothetical prioritization only: S severity 1 negligible to 10 catastrophic; O occurrence 1 rare to 10 frequent; D detection 1 caught before harm to 10 hard to detect. RPN=63. No measured frequency or accepted residual risk. Prompt injection as model manipulation is inapplicable with zero LLMs; unsafe CSV/shell content is FM6. Remote unknown commits, tenant grants, compensation and revoked remote authority are outside this local-only scope.
- **FM2 Threshold or UTC-window error**: Hypothetical prioritization only: S severity 1 negligible to 10 catastrophic; O occurrence 1 rare to 10 frequent; D detection 1 caught before harm to 10 hard to detect. RPN=96. No measured frequency or accepted residual risk. Prompt injection as model manipulation is inapplicable with zero LLMs; unsafe CSV/shell content is FM6. Remote unknown commits, tenant grants, compensation and revoked remote authority are outside this local-only scope.
- **FM3 Incomplete, malformed or stale evidence**: Hypothetical prioritization only: S severity 1 negligible to 10 catastrophic; O occurrence 1 rare to 10 frequent; D detection 1 caught before harm to 10 hard to detect. RPN=128. No measured frequency or accepted residual risk. Prompt injection as model manipulation is inapplicable with zero LLMs; unsafe CSV/shell content is FM6. Remote unknown commits, tenant grants, compensation and revoked remote authority are outside this local-only scope.
- **FM4 Partial or false-complete local publication**: Hypothetical prioritization only: S severity 1 negligible to 10 catastrophic; O occurrence 1 rare to 10 frequent; D detection 1 caught before harm to 10 hard to detect. RPN=96. No measured frequency or accepted residual risk. Prompt injection as model manipulation is inapplicable with zero LLMs; unsafe CSV/shell content is FM6. Remote unknown commits, tenant grants, compensation and revoked remote authority are outside this local-only scope.
- **FM5 Concurrent or conflicting re-publication**: Hypothetical prioritization only: S severity 1 negligible to 10 catastrophic; O occurrence 1 rare to 10 frequent; D detection 1 caught before harm to 10 hard to detect. RPN=63. No measured frequency or accepted residual risk. Prompt injection as model manipulation is inapplicable with zero LLMs; unsafe CSV/shell content is FM6. Remote unknown commits, tenant grants, compensation and revoked remote authority are outside this local-only scope.
- **FM6 Unsafe input or filesystem scope**: Hypothetical prioritization only: S severity 1 negligible to 10 catastrophic; O occurrence 1 rare to 10 frequent; D detection 1 caught before harm to 10 hard to detect. RPN=64. No measured frequency or accepted residual risk. Prompt injection as model manipulation is inapplicable with zero LLMs; unsafe CSV/shell content is FM6. Remote unknown commits, tenant grants, compensation and revoked remote authority are outside this local-only scope.
- **FM7 Cancellation, deadline or size-limit mishandling**: Hypothetical prioritization only: S severity 1 negligible to 10 catastrophic; O occurrence 1 rare to 10 frequent; D detection 1 caught before harm to 10 hard to detect. RPN=63. No measured frequency or accepted residual risk. Prompt injection as model manipulation is inapplicable with zero LLMs; unsafe CSV/shell content is FM6. Remote unknown commits, tenant grants, compensation and revoked remote authority are outside this local-only scope.
- **FM8 Failure is not owned or seen**: Hypothetical prioritization only: S severity 1 negligible to 10 catastrophic; O occurrence 1 rare to 10 frequent; D detection 1 caught before harm to 10 hard to detect. RPN=96. No measured frequency or accepted residual risk. Prompt injection as model manipulation is inapplicable with zero LLMs; unsafe CSV/shell content is FM6. Remote unknown commits, tenant grants, compensation and revoked remote authority are outside this local-only scope.
- **FM9 Exposure or uncontrolled retention**: Hypothetical prioritization only: S severity 1 negligible to 10 catastrophic; O occurrence 1 rare to 10 frequent; D detection 1 caught before harm to 10 hard to detect. RPN=72. No measured frequency or accepted residual risk. Prompt injection as model manipulation is inapplicable with zero LLMs; unsafe CSV/shell content is FM6. Remote unknown commits, tenant grants, compensation and revoked remote authority are outside this local-only scope.

## Evals

- **EV1 Positive one-row late delivery**: Planned synthetic business-harness test, not executed by design_io. The fixture is self-contained, with no inherited or hidden base. The harness must compute hashes/canonical manifests from these exact bytes and verify all assertions.
- **EV2 Exactly 24 hours is not late**: Planned synthetic business-harness test, not executed by design_io. The fixture is self-contained, with no inherited or hidden base. The harness must compute hashes/canonical manifests from these exact bytes and verify all assertions.
- **EV3 Duplicate promised ID fails even with identical rows**: Planned synthetic business-harness test, not executed by design_io. The fixture is self-contained, with no inherited or hidden base. The harness must compute hashes/canonical manifests from these exact bytes and verify all assertions.
- **EV4 Duplicate actual ID fails**: Planned synthetic business-harness test, not executed by design_io. The fixture is self-contained, with no inherited or hidden base. The harness must compute hashes/canonical manifests from these exact bytes and verify all assertions.
- **EV5 Formula-like ID is inert and rejected**: Planned synthetic business-harness test, not executed by design_io. The fixture is self-contained, with no inherited or hidden base. The harness must compute hashes/canonical manifests from these exact bytes and verify all assertions.
- **EV6 UTC day, sorting, leading zero and early delivery**: Planned synthetic business-harness test, not executed by design_io. The fixture is self-contained, with no inherited or hidden base. The harness must compute hashes/canonical manifests from these exact bytes and verify all assertions.
- **EV7 Delivered order missing promise**: Planned synthetic business-harness test, not executed by design_io. The fixture is self-contained, with no inherited or hidden base. The harness must compute hashes/canonical manifests from these exact bytes and verify all assertions.
- **EV8 Invalid actual date**: Planned synthetic business-harness test, not executed by design_io. The fixture is self-contained, with no inherited or hidden base. The harness must compute hashes/canonical manifests from these exact bytes and verify all assertions.
- **EV9 Non-UTC actual offset**: Planned synthetic business-harness test, not executed by design_io. The fixture is self-contained, with no inherited or hidden base. The harness must compute hashes/canonical manifests from these exact bytes and verify all assertions.
- **EV10 Missing required header**: Planned synthetic business-harness test, not executed by design_io. The fixture is self-contained, with no inherited or hidden base. The harness must compute hashes/canonical manifests from these exact bytes and verify all assertions.
- **EV11 Duplicate header**: Planned synthetic business-harness test, not executed by design_io. The fixture is self-contained, with no inherited or hidden base. The harness must compute hashes/canonical manifests from these exact bytes and verify all assertions.
- **EV12 CSV row width mismatch**: Planned synthetic business-harness test, not executed by design_io. The fixture is self-contained, with no inherited or hidden base. The harness must compute hashes/canonical manifests from these exact bytes and verify all assertions.
- **EV13 Known pre-publication disk-full**: Planned synthetic business-harness test, not executed by design_io. The fixture is self-contained, with no inherited or hidden base. The harness must compute hashes/canonical manifests from these exact bytes and verify all assertions.
- **EV14 Unknown commit reconciles without duplicate publish**: Planned synthetic business-harness test, not executed by design_io. The fixture is self-contained, with no inherited or hidden base. The harness must compute hashes/canonical manifests from these exact bytes and verify all assertions.
- **EV15 Proven absent permits one retry**: Planned synthetic business-harness test, not executed by design_io. The fixture is self-contained, with no inherited or hidden base. The harness must compute hashes/canonical manifests from these exact bytes and verify all assertions.
- **EV16 Unresolved publication is blocked**: Planned synthetic business-harness test, not executed by design_io. The fixture is self-contained, with no inherited or hidden base. The harness must compute hashes/canonical manifests from these exact bytes and verify all assertions.
- **EV17 Concurrent run cannot write**: Planned synthetic business-harness test, not executed by design_io. The fixture is self-contained, with no inherited or hidden base. The harness must compute hashes/canonical manifests from these exact bytes and verify all assertions.
- **EV18 Changed input never overwrites report**: Planned synthetic business-harness test, not executed by design_io. The fixture is self-contained, with no inherited or hidden base. The harness must compute hashes/canonical manifests from these exact bytes and verify all assertions.
- **EV19 Undelivered and promised-only produce empty valid CSV**: Planned synthetic business-harness test, not executed by design_io. The fixture is self-contained, with no inherited or hidden base. The harness must compute hashes/canonical manifests from these exact bytes and verify all assertions.
- **EV20 Revoked local write permission fails safely**: Planned synthetic business-harness test, not executed by design_io. The fixture is self-contained, with no inherited or hidden base. The harness must compute hashes/canonical manifests from these exact bytes and verify all assertions.
- **EV21 Symlink path cannot escape input scope**: Planned synthetic business-harness test, not executed by design_io. The fixture is self-contained, with no inherited or hidden base. The harness must compute hashes/canonical manifests from these exact bytes and verify all assertions.
- **EV22 Input size exceeds configured bound**: Planned synthetic business-harness test, not executed by design_io. The fixture is self-contained, with no inherited or hidden base. The harness must compute hashes/canonical manifests from these exact bytes and verify all assertions.
- **EV23 Retry budget cannot loop**: Planned synthetic business-harness test, not executed by design_io. The fixture is self-contained, with no inherited or hidden base. The harness must compute hashes/canonical manifests from these exact bytes and verify all assertions.
- **EV24 Exact rerun returns durable no-op**: Planned synthetic business-harness test, not executed by design_io. The fixture is self-contained, with no inherited or hidden base. The harness must compute hashes/canonical manifests from these exact bytes and verify all assertions.
- **EV25 Stale lock is never auto-broken**: Planned synthetic business-harness test, not executed by design_io. The fixture is self-contained, with no inherited or hidden base. The harness must compute hashes/canonical manifests from these exact bytes and verify all assertions.
- **EV26 Cancellation before publication**: Planned synthetic business-harness test, not executed by design_io. The fixture is self-contained, with no inherited or hidden base. The harness must compute hashes/canonical manifests from these exact bytes and verify all assertions.
- **EV27 Cancellation after commit start defers to proof**: Planned synthetic business-harness test, not executed by design_io. The fixture is self-contained, with no inherited or hidden base. The harness must compute hashes/canonical manifests from these exact bytes and verify all assertions.
- **EV28 Local status failure remains visible**: Planned synthetic business-harness test, not executed by design_io. The fixture is self-contained, with no inherited or hidden base. The harness must compute hashes/canonical manifests from these exact bytes and verify all assertions.
- **EV29 Extra data is minimized from outputs and logs**: Planned synthetic business-harness test, not executed by design_io. The fixture is self-contained, with no inherited or hidden base. The harness must compute hashes/canonical manifests from these exact bytes and verify all assertions.
- **EV30 Offline parser, invariants and end-to-end suite**: Planned evaluation; business tests and live checks are not executed by this skill.
- **EV31 Daily local report and failure monitor**: Planned evaluation; business tests and live checks are not executed by this skill.
- **EV32 Release gate and deployment filesystem proof**: Planned evaluation; business tests and live checks are not executed by this skill.

## Rollout

### R1 · Exact report accuracy and business evidence

Operations can prioritize late deliveries only when IDs, daily inclusion and strict flags are correct. No downstream business outcome is promised.

Reasoning: Operational release requires evidence and named proposed accountability, not a design score.

Assumptions:

- H2: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H7: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

Data:

```json
{
  "category": "kpi",
  "businessKpi": "Daily record accuracy = correctly included/flagged rows divided by independently expected rows; track missing and extra rows separately so denominator cannot hide omissions. Weekly aggregate is secondary to any integrity breach. Baseline unknown: manual source comparison in shadow. Target hypothesis: exact agreement 100%; any error blocks consumption.",
  "aiMetrics": [
    "No AI metrics. Exact join/UTC fixture pass fraction causally protects correct queue selection by eliminating date/identity errors. Source freshness is separately required: correct arithmetic cannot repair omitted deliveries."
  ],
  "phase": "All phases",
  "gate": "Do not declare production accuracy from synthetic EVs; record verified manual sample denominator and mismatch counts daily; all known integrity defects must be zero.",
  "owner": "Operations data owner",
  "experiment": "R5 measures operations effort only after accuracy gates pass."
}
```


Sources:

- context / user-brief: Design a small daily report that joins two CSV files by order ID. One has promised-delivery timestamps and the other actual-delivery timestamps, both ISO UTC. Flag delivered orders more than 24 hours late and export a CSV for the operations team. No emails, remote updates, forecasting or conversational interface.

- hypothesis / H2: Operations supplies two complete snapshots from the same order namespace and consistent export cutoff after the requested day ends. CSVs have no authoritative dataset/as-of metadata; the job cannot independently prove their business freshness or shared provenance.

- hypothesis / H3: The daily report covers actual deliveries in the previous UTC calendar day by default, with an explicit --report-date override for backfills. It contains all delivered rows in that day, not only late rows; a boolean identifies lateness.

- hypothesis / H5: Proposed operational budget is at most 100,000 rows and 50 MiB per file, 120 seconds per run, and a once-daily invocation at 08:00 UTC after exports are ready. Operations reviews local status by 10:00 UTC and acknowledges failures by 12:00 UTC; after that the operations lead manually escalates.

- hypothesis / H6: Run on one trusted local host/account with two allowlisted input roots, a dedicated output root and same-filesystem staging. Only the job may mutate its output root; no symlinks are permitted in resolved input/output paths. An operator grants these local capabilities in configuration.

- hypothesis / H7: Keep committed CSVs, manifests and local failure records for 30 days. Do not copy raw input files; persist hashes, counts and error row numbers without row contents. Delete expired files locally only through a separate operator-maintained procedure.

- hypothesis / H8: A date with an existing valid completed report is immutable: identical input/config returns ALREADY_COMPLETE; changed input/config returns CONFLICT. Corrections require the owner to archive the old date directory outside this job and rerun; no replacement action is implemented.

### R2 · Completeness and durable report KPI

Durability and visible failure prevent the operations team treating a missing or partial report as a valid zero-late day.

Reasoning: Operational release requires evidence and named proposed accountability, not a design score.

Assumptions:

- H2: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H7: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

Data:

```json
{
  "category": "kpi",
  "businessKpi": "Publication completeness = expected report dates with one checksum-verified COMPLETE directory by 10:00 UTC / expected scheduled report dates in each UTC week; blocked/cancelled/missing dates remain in denominator. Baseline unknown; target hypothesis 100%.",
  "aiMetrics": [
    "Guardrail: false-complete count must be 0; correct durable proof makes a report safely consumable. Busy/conflict/unknown counts diagnose reliability, not delivery performance."
  ],
  "phase": "All phases",
  "gate": "Any invalid hash/false completion stops report use immediately, irrespective of average timeliness.",
  "owner": "Operations report owner",
  "experiment": "Observe during shadow before proposing service level."
}
```


Sources:

- context / user-brief: Design a small daily report that joins two CSV files by order ID. One has promised-delivery timestamps and the other actual-delivery timestamps, both ISO UTC. Flag delivered orders more than 24 hours late and export a CSV for the operations team. No emails, remote updates, forecasting or conversational interface.

- hypothesis / H2: Operations supplies two complete snapshots from the same order namespace and consistent export cutoff after the requested day ends. CSVs have no authoritative dataset/as-of metadata; the job cannot independently prove their business freshness or shared provenance.

- hypothesis / H3: The daily report covers actual deliveries in the previous UTC calendar day by default, with an explicit --report-date override for backfills. It contains all delivered rows in that day, not only late rows; a boolean identifies lateness.

- hypothesis / H5: Proposed operational budget is at most 100,000 rows and 50 MiB per file, 120 seconds per run, and a once-daily invocation at 08:00 UTC after exports are ready. Operations reviews local status by 10:00 UTC and acknowledges failures by 12:00 UTC; after that the operations lead manually escalates.

- hypothesis / H6: Run on one trusted local host/account with two allowlisted input roots, a dedicated output root and same-filesystem staging. Only the job may mutate its output root; no symlinks are permitted in resolved input/output paths. An operator grants these local capabilities in configuration.

- hypothesis / H7: Keep committed CSVs, manifests and local failure records for 30 days. Do not copy raw input files; persist hashes, counts and error row numbers without row contents. Delete expired files locally only through a separate operator-maintained procedure.

- hypothesis / H8: A date with an existing valid completed report is immutable: identical input/config returns ALREADY_COMPLETE; changed input/config returns CONFLICT. Corrections require the owner to archive the old date directory outside this job and rerun; no replacement action is implemented.

### R3 · Manual review effort

A complete CSV can reduce repeated manual joins; unmeasured time savings remain a hypothesis.

Reasoning: Operational release requires evidence and named proposed accountability, not a design score.

Assumptions:

- H2: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H7: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

Data:

```json
{
  "category": "kpi",
  "businessKpi": "Operations review effort = minutes from export pair availability to verified daily queue, including correction/investigation time, per UTC report day. Baseline unknown; collect manual timers during shadow. Target hypothesis: reduce median time without any accuracy/completeness breach.",
  "aiMetrics": [
    "Runtime p95 under provisional 120s and output verification time are operational metrics. Runtime affects availability but is not a substitute for correctness. Human ack rate is a guardrail for failures."
  ],
  "phase": "Shadow onward",
  "gate": "Do not claim savings before R5 measurement; safety/error gates are applied per day.",
  "owner": "Operations report owner",
  "experiment": "R5 uses date-level paired observations and continuous-outcome power analysis."
}
```


Sources:

- context / user-brief: Design a small daily report that joins two CSV files by order ID. One has promised-delivery timestamps and the other actual-delivery timestamps, both ISO UTC. Flag delivered orders more than 24 hours late and export a CSV for the operations team. No emails, remote updates, forecasting or conversational interface.

- hypothesis / H2: Operations supplies two complete snapshots from the same order namespace and consistent export cutoff after the requested day ends. CSVs have no authoritative dataset/as-of metadata; the job cannot independently prove their business freshness or shared provenance.

- hypothesis / H3: The daily report covers actual deliveries in the previous UTC calendar day by default, with an explicit --report-date override for backfills. It contains all delivered rows in that day, not only late rows; a boolean identifies lateness.

- hypothesis / H5: Proposed operational budget is at most 100,000 rows and 50 MiB per file, 120 seconds per run, and a once-daily invocation at 08:00 UTC after exports are ready. Operations reviews local status by 10:00 UTC and acknowledges failures by 12:00 UTC; after that the operations lead manually escalates.

- hypothesis / H6: Run on one trusted local host/account with two allowlisted input roots, a dedicated output root and same-filesystem staging. Only the job may mutate its output root; no symlinks are permitted in resolved input/output paths. An operator grants these local capabilities in configuration.

- hypothesis / H7: Keep committed CSVs, manifests and local failure records for 30 days. Do not copy raw input files; persist hashes, counts and error row numbers without row contents. Delete expired files locally only through a separate operator-maintained procedure.

- hypothesis / H8: A date with an existing valid completed report is immutable: identical input/config returns ALREADY_COMPLETE; changed input/config returns CONFLICT. Corrections require the owner to archive the old date directory outside this job and rerun; no replacement action is implemented.

### R4 · Shadow then assist-only rollout

This is a read-and-export workflow. An assist-only end state is justified; no pilot of customer/order actions is in scope. Every phase has entry evidence distinct from its own exit evidence.

Reasoning: Operational release requires evidence and named proposed accountability, not a design score.

Assumptions:

- H2: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H7: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

Data:

```json
{
  "category": "phase",
  "businessKpi": "R1/R2/R3 definitions above.",
  "aiMetrics": [
    "EV1-EV30 executed pass; local monitor EV31 and release evidence EV32."
  ],
  "phase": "Shadow → Assist-only → Routine assist; no autonomous operations action phase.",
  "gate": "Shadow entry: implemented CLI/harness and EV32 local synthetic/dependency evidence complete; no user consumption. Shadow exit: five consecutive complete daily export pairs spanning approved source strata, exact manually adjudicated report agreement and no unknown publication, with H2 source cutoff checks. Assist entry: shadow exit signed locally by proposed owners. Assist exit: five additional days with checks and failure drill; R5 effort evidence may extend duration. Routine assist entry: owners approve runbook and monitoring. Any wrong row, privacy leak, invalid proof or unowned failure stops consumption; preserve artifacts, disable schedule manually and use current manual join procedure. Re-enable only after cause fixed and EV32 rerun.",
  "owner": "Operations report owner owns stop/restore; Implementation owner repairs; Data owner confirms source truth.",
  "experiment": "No expansion of side-effect authority at any phase. Shadow/assist day counts are proposed minimum coverage, not statistical power or observed data."
}
```


Sources:

- context / user-brief: Design a small daily report that joins two CSV files by order ID. One has promised-delivery timestamps and the other actual-delivery timestamps, both ISO UTC. Flag delivered orders more than 24 hours late and export a CSV for the operations team. No emails, remote updates, forecasting or conversational interface.

- hypothesis / H2: Operations supplies two complete snapshots from the same order namespace and consistent export cutoff after the requested day ends. CSVs have no authoritative dataset/as-of metadata; the job cannot independently prove their business freshness or shared provenance.

- hypothesis / H3: The daily report covers actual deliveries in the previous UTC calendar day by default, with an explicit --report-date override for backfills. It contains all delivered rows in that day, not only late rows; a boolean identifies lateness.

- hypothesis / H5: Proposed operational budget is at most 100,000 rows and 50 MiB per file, 120 seconds per run, and a once-daily invocation at 08:00 UTC after exports are ready. Operations reviews local status by 10:00 UTC and acknowledges failures by 12:00 UTC; after that the operations lead manually escalates.

- hypothesis / H6: Run on one trusted local host/account with two allowlisted input roots, a dedicated output root and same-filesystem staging. Only the job may mutate its output root; no symlinks are permitted in resolved input/output paths. An operator grants these local capabilities in configuration.

- hypothesis / H7: Keep committed CSVs, manifests and local failure records for 30 days. Do not copy raw input files; persist hashes, counts and error row numbers without row contents. Delete expired files locally only through a separate operator-maintained procedure.

- hypothesis / H8: A date with an existing valid completed report is immutable: identical input/config returns ALREADY_COMPLETE; changed input/config returns CONFLICT. Corrections require the owner to archive the old date directory outside this job and rerun; no replacement action is implemented.

### R5 · Measure effort with paired days

Time is continuous, so binary proportion formulas would be inappropriate. No fabricated baseline, sample-size number, confidence interval or measured benefit is supplied.

Reasoning: Operational release requires evidence and named proposed accountability, not a design score.

Assumptions:

- H2: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H7: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

Data:

```json
{
  "category": "experiment",
  "businessKpi": "R3 minutes per report day; R1/R2 integrity are non-negotiable guardrails.",
  "aiMetrics": [
    "Paired difference in independently timed manual versus tool-assisted review minutes; medians and mean paired difference with confidence interval; no AI accuracy claim."
  ],
  "phase": "During shadow/assist after deterministic release gates.",
  "gate": "Eligibility: complete approved source pairs in the requested UTC day; strata by row-count bands and late-order prevalence measured from sources. Each day is one paired block. Two separate operators review same snapshot independently; randomize method-to-operator order within day and rotate roles. Hide each other’s result until timing/labels recorded; reconcile afterwards. Start with baseline collection across weekdays/volume strata, estimate paired-difference SD, choose minimum meaningful minutes reduction with owner, use paired continuous-mean power calculation for 80% power and two-sided alpha 0.05. Adjust for repeated operator/week clusters using estimated intracluster correlation or cluster bootstrap; report uncertainty when sample size is insufficient. Continue complete weekly cycles until precomputed sample and strata achieved; five-day phase minima are not a powered sample. Any integrity breach stops experiment use, not averaged away.",
  "owner": "Operations report owner approves effect threshold; analyst/implementation owner computes sample and review.",
  "experiment": "Unit is UTC report date; no randomization of customer service. Operators must not share report outputs before timing. If independent operators unavailable, record limitation and run descriptive timings without causal savings claim."
}
```


Sources:

- context / user-brief: Design a small daily report that joins two CSV files by order ID. One has promised-delivery timestamps and the other actual-delivery timestamps, both ISO UTC. Flag delivered orders more than 24 hours late and export a CSV for the operations team. No emails, remote updates, forecasting or conversational interface.

- hypothesis / H2: Operations supplies two complete snapshots from the same order namespace and consistent export cutoff after the requested day ends. CSVs have no authoritative dataset/as-of metadata; the job cannot independently prove their business freshness or shared provenance.

- hypothesis / H3: The daily report covers actual deliveries in the previous UTC calendar day by default, with an explicit --report-date override for backfills. It contains all delivered rows in that day, not only late rows; a boolean identifies lateness.

- hypothesis / H5: Proposed operational budget is at most 100,000 rows and 50 MiB per file, 120 seconds per run, and a once-daily invocation at 08:00 UTC after exports are ready. Operations reviews local status by 10:00 UTC and acknowledges failures by 12:00 UTC; after that the operations lead manually escalates.

- hypothesis / H6: Run on one trusted local host/account with two allowlisted input roots, a dedicated output root and same-filesystem staging. Only the job may mutate its output root; no symlinks are permitted in resolved input/output paths. An operator grants these local capabilities in configuration.

- hypothesis / H7: Keep committed CSVs, manifests and local failure records for 30 days. Do not copy raw input files; persist hashes, counts and error row numbers without row contents. Delete expired files locally only through a separate operator-maintained procedure.

- hypothesis / H8: A date with an existing valid completed report is immutable: identical input/config returns ALREADY_COMPLETE; changed input/config returns CONFLICT. Corrections require the owner to archive the old date directory outside this job and rerun; no replacement action is implemented.

### R6 · Accountability and manual recovery

Local failures are visible through status/exit/stderr and a manual operating queue. Unassigned people, policy and capacity are launch dependencies.

Reasoning: Operational release requires evidence and named proposed accountability, not a design score.

Assumptions:

- H2: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H7: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

Data:

```json
{
  "category": "owner",
  "businessKpi": "R1 source correctness: Data owner. R2 schedule/outcome/ack: Report owner. R3 timing: Report owner. Code/filesystem/control repairs: Implementation owner.",
  "aiMetrics": [
    "Local status proof, overdue acknowledgements and source export checks."
  ],
  "phase": "All phases",
  "gate": "Before launch each proposed role must be assigned to an actual person. Report owner checks by 10:00 UTC, ack by 12:00 UTC and manual escalation to operations lead thereafter. No automated messaging is added. Unknown publication: lock out rerun, inspect final manifest/hash under read-only check, document disposition. Stale lock: confirm no active process and inspect report before manual removal. Correction: archive old date directory with owner approval outside this job, preserve evidence then rerun. Retention deletion is a separate manual procedure.",
  "owner": "Proposed roles only; appointment and capacity require H5/H7/H8 evidence.",
  "experiment": "Owners approve rollout and residual risk explicitly; acceptedRisk remains false in this design."
}
```


Sources:

- context / user-brief: Design a small daily report that joins two CSV files by order ID. One has promised-delivery timestamps and the other actual-delivery timestamps, both ISO UTC. Flag delivered orders more than 24 hours late and export a CSV for the operations team. No emails, remote updates, forecasting or conversational interface.

- hypothesis / H2: Operations supplies two complete snapshots from the same order namespace and consistent export cutoff after the requested day ends. CSVs have no authoritative dataset/as-of metadata; the job cannot independently prove their business freshness or shared provenance.

- hypothesis / H3: The daily report covers actual deliveries in the previous UTC calendar day by default, with an explicit --report-date override for backfills. It contains all delivered rows in that day, not only late rows; a boolean identifies lateness.

- hypothesis / H5: Proposed operational budget is at most 100,000 rows and 50 MiB per file, 120 seconds per run, and a once-daily invocation at 08:00 UTC after exports are ready. Operations reviews local status by 10:00 UTC and acknowledges failures by 12:00 UTC; after that the operations lead manually escalates.

- hypothesis / H6: Run on one trusted local host/account with two allowlisted input roots, a dedicated output root and same-filesystem staging. Only the job may mutate its output root; no symlinks are permitted in resolved input/output paths. An operator grants these local capabilities in configuration.

- hypothesis / H7: Keep committed CSVs, manifests and local failure records for 30 days. Do not copy raw input files; persist hashes, counts and error row numbers without row contents. Delete expired files locally only through a separate operator-maintained procedure.

- hypothesis / H8: A date with an existing valid completed report is immutable: identical input/config returns ALREADY_COMPLETE; changed input/config returns CONFLICT. Corrections require the owner to archive the old date directory outside this job and rerun; no replacement action is implemented.


## Export

### X1 · Build the bounded daily CSV report

Implement only the final canonical design, preserving IDs in code docs/test names. This package is proposed design, not the report implementation or an executed operational run.

Reasoning: Observable byte-level behavior, contract checks and real future evidence make the handoff implementable.

Assumptions:

- H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H2: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H7: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

Data:

```json
{
  "acceptanceCriteria": [
    "CTX2/F1: implement a local deterministic CLI only; zero LLM/network calls, emails, remote updates, forecasts or conversation.",
    "T1/C1: accept only allowed no-symlink paths, completed UTC date and bounded immutable file bytes; enforce exclusive date lock and exact run/config/input hashes.",
    "T2/C2: enforce H1/H4 over complete files, exact IDs, unique headers/IDs, valid UTC timestamps and promised match for every delivered actual; fail entire run with exact reason/row and no final report.",
    "T3/C3: all and only delivered actual rows inside H3 half-open day, strict integer-microsecond >24h, negative deltas false, sorted stable output; EV1/EV2/EV6/EV19 exact CSV bytes pass.",
    "T4/C4/C5: committed report is immutable with COMPLETE manifest+matching CSV SHA256; identical rerun verified no-op, conflict never overwrite; uncertain publication readback before at most one retry; EV13-EV18 and EV23-EV27 pass.",
    "T5/C6: proof-required exit 0; failure exit 2, cancellation 130; local owner/deadline/next action, stderr fallback and visible cleanup warnings; no remote notification.",
    "FM1-FM9/EV1-EV32: implement future isolated harness and store actual results; no synthetic assertion is counted as executed before harness runs; release suite enumerates all EV1-EV29.",
    "R4/R6: owners verify H1-H8 and EV32 evidence before consumption, execute shadow then assist-only runbook and manual rollback; no hidden schedule provisioning or permission expansion.",
    "F5/EV29: persist only five output columns, hashes/counts and error row numbers; no raw-input copies/contents or extra customer fields in output/status/stderr.",
    "ISSUE2/ISSUE3 repair: deterministic exact CTX4 manifest/config/run key JSON bindings; full stored manifest checks, distinct -a0/-a1 stage paths, and post-start cancellation always reconciled."
  ],
  "buildInstructions": "Build a Python 3 standard-library CLI with modules for C1 acquisition/config/locks, C2 strict CSV validation, C3 join/render, C4 staged immutable publication, C5 readback reconciliation and C6 local outcomes. Start at W1 and implement the exact enums/exclusive transitions through W9/W10/W11. Use strings for order IDs, aware UTC integer-microsecond timestamps and fixed decimal seconds; no float comparison. State ownership: C1 owns immutable snapshot/lock/run identity, C2 maps, C3 deterministic bytes/counts, C4 final write, C5 proof, C6 terminal status. Include stable config_digest/run_key canonical sorted compact JSON serialization and complete manifest shape from CTX4. Capability scope, no-symlink and trusted-host assumptions are F4/H6; no credentials or network adapters are required. Every expected error is explicit in C1-C6; an unexpected exception must block without inventing completion. Existing status failure cannot fabricate rollback of a proved final report. Implement in isolated /sandbox roots for EV1-EV29; materialize each complete fixture, compute hashes from its exact bytes, capture ordered mock calls and assert expected records and forbidden effects. Add EV30 component/property classes and fault injection on selected deployment filesystem. Store actual executed results separately; do not mistake design_io validation for a business harness. Verify H1-H8 source/schema/timing/permissions/retention/correction dependencies with proposed owners, then use EV32 release gate and R4/R6 runbook. Manual rollback disables local schedule and returns to manual join without deleting evidence. No email, messaging, remote update, forecasting, chat UI, order mutation, automatic overwrite or remote cloud provisioning. Persist stable error codes/row numbers only. Open questions are explicit launch dependencies, not permission to invent source guarantees. Use the exact CTX4 manifest and canonical digest fields. C4 stages at an attempt-specific -a0/-a1 path and signals after rename begins return UNKNOWN for C5 proof. Never reuse an orphan stage or treat matching filenames as a matching report."
}
```


Sources:

- context / user-brief: Design a small daily report that joins two CSV files by order ID. One has promised-delivery timestamps and the other actual-delivery timestamps, both ISO UTC. Flag delivered orders more than 24 hours late and export a CSV for the operations team. No emails, remote updates, forecasting or conversational interface.

- hypothesis / H1: The proposed CSV contract is UTF-8 with optional BOM, comma delimiter and one header; promised columns are order_id,promised_delivery_utc and actual columns are order_id,actual_delivery_utc. Extra columns are ignored. IDs are case-sensitive ASCII [A-Za-z0-9][A-Za-z0-9_-]{0,63}, unique within each file; empty or padded IDs are errors.

- hypothesis / H2: Operations supplies two complete snapshots from the same order namespace and consistent export cutoff after the requested day ends. CSVs have no authoritative dataset/as-of metadata; the job cannot independently prove their business freshness or shared provenance.

- hypothesis / H3: The daily report covers actual deliveries in the previous UTC calendar day by default, with an explicit --report-date override for backfills. It contains all delivered rows in that day, not only late rows; a boolean identifies lateness.

- hypothesis / H4: Accepted timestamps use YYYY-MM-DDTHH:MM:SS[.ffffff]Z or +00:00, with 1-6 fractional digits, valid Gregorian dates and seconds 00-59. Empty actual means undelivered; non-UTC offsets, missing promised values, leap seconds and greater precision fail validation.

- hypothesis / H5: Proposed operational budget is at most 100,000 rows and 50 MiB per file, 120 seconds per run, and a once-daily invocation at 08:00 UTC after exports are ready. Operations reviews local status by 10:00 UTC and acknowledges failures by 12:00 UTC; after that the operations lead manually escalates.

- hypothesis / H6: Run on one trusted local host/account with two allowlisted input roots, a dedicated output root and same-filesystem staging. Only the job may mutate its output root; no symlinks are permitted in resolved input/output paths. An operator grants these local capabilities in configuration.

- hypothesis / H7: Keep committed CSVs, manifests and local failure records for 30 days. Do not copy raw input files; persist hashes, counts and error row numbers without row contents. Delete expired files locally only through a separate operator-maintained procedure.

- hypothesis / H8: A date with an existing valid completed report is immutable: identical input/config returns ALREADY_COMPLETE; changed input/config returns CONFLICT. Corrections require the owner to archive the old date directory outside this job and rerun; no replacement action is implemented.


Full exact data and source evidence: [design.json](design.json). Launch facts and owners: [assumptions.md](assumptions.md).
