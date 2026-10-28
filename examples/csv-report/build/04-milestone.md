# Atomic local publisher

> PASS | DESIGN ONLY. self-review; round 3.

Depends on earlier milestones where their outputs are inputs below. Cross-milestone shared types are read by ID from ../design.json, not copied.

## Selected contracts

### C4 · Atomic local publisher

Final directory ROOT/YYYY-MM-DD contains report.csv and manifest.json. Under acquired per-date lock, existing COMPLETE manifest with same run_key and matching CSV hash => ALREADY_COMPLETE; any differing or incomplete final directory => CONFLICT. Stage at ROOT/.staging-<date>-<run_key>-<pid>-a<retry_count>; create files exclusively, fsync each and directory. Manifest schema is in CTX4; input counts are C2/C3 outputs. Recheck output-root permission and lock ownership before rename. Publish by same-filesystem directory rename then fsync output root; any exception after rename begins => UNKNOWN and C5 reconciliation, never immediate retry. Before rename, cancellation deletes staging and returns CANCELLED; failures known before rename return NOT_COMMITTED. After rename begins defer cancellation until reconciliation determines whether published. Stage no later than deadline; uncertain timeout is UNKNOWN. No network, input mutation or automatic overwrite. The exact typed manifest/canonical JSON is CTX4. Before ALREADY_COMPLETE verify all stored date/schema/config/input hashes and derived counts against the current expected manifest, plus actual report hash; any discrepancy is CONFLICT. A retry uses its fresh -a1 directory; best-effort remove the owned prior -a0 stage after ABSENT proof, but cleanup failure never authorizes reading/reusing that stage. No automatic deletion of another run stage. Any cancellation signal received after rename begins makes C4 return UNKNOWN, even if rename appears successful, so W6 proves COMMITTED or ABSENT before selecting terminal; no post-start CANCELLED outcome bypasses readback.

Reasoning: Atomic publication with content identity prevents partial reports, duplicate runs and false completion.

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
    "T4"
  ],
  "inputs": [
    "snapshot:required C1 snapshot; report:required C3 BUILT report",
    "retry_count:required int in 0..1; cancel_requested:required boolean",
    "capability:required output-root permission from local execution account, rechecked before staging and rename; date lock still held"
  ],
  "outputs": [
    "outcome:enum COMMITTED|ALREADY_COMPLETE|NOT_COMMITTED|UNKNOWN|CONFLICT|CANCELLED; reason:enum NONE|PERMISSION_DENIED|STAGE_IO|PUBLISH_AMBIGUOUS|EXISTING_CONFLICT|CANCELLED|TIMEOUT",
    "proof when COMMITTED or ALREADY_COMPLETE:required {final_dir:absolute path,manifest_path:absolute path,run_key:hex64,report_sha256:hex64,manifest_status:COMPLETE}",
    "candidate_final_dir:required absolute path; cleanup_warning:optional enum STAGING_CLEANUP_FAILED|LOCK_CLEANUP_FAILED"
  ],
  "whyCode": "Atomic publication with content identity prevents partial reports, duplicate runs and false completion.",
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

### W4 · STAGE_PUBLISH

{"state":"STAGE_PUBLISH","transitions":[{"to":"W9","when":"C4.outcome in [COMMITTED,ALREADY_COMPLETE]","mode":"exclusive"},{"to":"W6","when":"C4.outcome == UNKNOWN","mode":"exclusive"},{"to":"W10","when":"C4.outcome == CANCELLED","mode":"exclusive"},{"to":"W11","when":"C4.outcome in [NOT_COMMITTED,CONFLICT]","mode":"exclusive"}],"failureDisposition":"All outcomes are enumerated below; unhandled internal exceptions go to W11 as BLOCKED/OUTPUT_IO without a success claim.","timeout":"C1-C4 share C1.deadline (120s); C5 has one additional 5s read-only reconciliation budget; C6 attempts local status once then stderr.","retryPolicy":"Zero except W6\u2192W4 after ABSENT, maximum one retry, bounded by deadline and cancellation.","terminalDisposition":"","guardBindings":"C1.outcome enum READY|BLOCKED|BUSY|CANCELLED; C2.outcome VALID|INVALID|CANCELLED; C3.outcome BUILT|CANCELLED; C4.outcome COMMITTED|ALREADY_COMPLETE|NOT_COMMITTED|UNKNOWN|CONFLICT|CANCELLED; C5.outcome COMMITTED|ABSENT|CONFLICT|UNKNOWN. C1 creates retry_count:int=0; orchestrator increments on W6\u2192W4. cancel_requested:boolean comes only from SIGINT/SIGTERM; deadline_expired:boolean compares monotonic clock with C1.deadline. Exact outcome switches below are exhaustive and exclusive; no guard depends on model text. "}

Reasoning: Explicit outcome switches and bounded readback preserve local report integrity.

Assumptions:

- H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

- H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

Data:

```json
{
  "componentId": "C4",
  "taskIds": [
    "T4"
  ],
  "next": [
    "W9",
    "W6",
    "W10",
    "W11"
  ],
  "decision": true,
  "example": "Rename succeeds but fsync result is unknown → W6; never blind retry."
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
- EV13: Known pre-publication disk-full
- EV14: Unknown commit reconciles without duplicate publish
- EV15: Proven absent permits one retry
- EV16: Unresolved publication is blocked
- EV17: Concurrent run cannot write
- EV18: Changed input never overwrites report
- EV20: Revoked local write permission fails safely
- EV21: Symlink path cannot escape input scope
- EV22: Input size exceeds configured bound
- EV23: Retry budget cannot loop
- EV24: Exact rerun returns durable no-op
- EV25: Stale lock is never auto-broken
- EV26: Cancellation before publication
- EV27: Cancellation after commit start defers to proof
- EV29: Extra data is minimized from outputs and logs
- EV30: Offline parser, invariants and end-to-end suite
- EV31: Daily local report and failure monitor
- EV32: Release gate and deployment filesystem proof
## Acceptance criteria

- Implement the declared contract and all named assertions; do not execute live actions without user authority.
