# Daily UTC delivery lateness CSV report

> PASS · DESIGN ONLY. Review is a design judgement; no business controls or provider reliability were executed.

Review method: self-review; round 3.

Review dimensions (supplied scores):

- D1: 3/4 — CTX1-CTX4/T0-T5 bound a daily join/export with exact exclusions and owned cancellation/failure.
- D2: 3/4 — Every leaf maps to C/W/EV; the generated all-category FM↔EV relation is reciprocal; H1-H8 distinguish assumptions from the unchanged brief.
- D3: 3/4 — W1-W11/C4/C5: exhaustive outcomes, one proven-absent retry with distinct staging path; post-start cancellation always readback; exact final proof before completion.
- D4: 3/4 — C1-C6 and CTX4: exact typed manifest/config/run-key canonical object fields, contracts and errors; full stored manifest equality and local human disposition.
- D5: 3/4 — C2/C3 own dates/IDs; F4 local allowlists and C4 fresh checks; manifest proof and H7 minimized retention. H6 platform behavior remains unverified.
- D6: 3/4 — H1-H8 mark source format, window, volumes, owners, policy and filesystem behavior as proposed launch dependencies; no vendor/current-fact claims.
- D7: 3/4 — F1-F5 choose code/local filesystem over LLM/database/cloud and compare deployment alternatives on identical criteria without claiming integrations.
- D8: 4/4 — Models.items is empty with an explicit zero-LLM budget; runtime/storage/human costs excluded as unmeasured.
- D9: 3/4 — FM1-FM9 are case-specific with S/O/D and owners; local unknown commits, injection, conflicts, failure visibility and privacy have explicit tests.
- D10: 3/4 — EV1-EV29 self-contained concrete fixtures; EV30 component/property layers, EV31 monitor and EV32 exact golden membership. Business harness is future work.; Actual independent fixture-label arithmetic audit inspected EV1/EV2/EV6/EV19/EV24/EV29 expected CSV rows: all passed; this is not execution of the future business harness.
- D11: 3/4 — R1-R6 define denominator-based KPIs, source-baseline dependency, noncircular shadow/assist gates, continuous paired effort experiment and manual stop/restore.
- D12: 3/4 — X1/CTX4/C1/C4/C5 propagate repairs; actual helper validation exited 0 with zero errors/warnings. Same-folder export round 1 succeeded; final export inspection is recorded separately in check-evidence.

Review findings:

- ISSUE1 [major, resolved] export/X1: Actual helper validate and same-folder export both exited 0; round-1 evidence is saved. Semantic payload review then found two material implementation ambiguities below.
- ISSUE2 [major, resolved] components/C4: CTX4/C1/C4 did not give one exact typed manifest object or exact config-digest key set, yet C4 delegated the manifest to CTX4. Different implementers could serialize different identity/config/count fields. Specify exact fields/canonical JSON and validate full stored binding before a no-op/completion. Repaired: CTX4 specifies exact manifest shape and canonical config/run-key bytes; C1/C4/C5/X1 propagate the binding.
- ISSUE3 [major, resolved] workflow/W6: C4 reused one staging path across its allowed retry after proven absence, so an orphan first-attempt staging directory could block EV15 despite the designed retry. Also EV27 expected explicit reconciliation for a signal after rename start without an explicit C4 output rule. Give attempt-specific stage paths and a precise post-start cancellation outcome. Repaired: C4 uses -a0/-a1 staging paths, fresh retry staging, owned cleanup, and explicit UNKNOWN on post-start cancellation; C5/X1 agree.

## Proposed assumption ledger

### H1

The proposed CSV contract is UTF-8 with optional BOM, comma delimiter and one header; promised columns are order_id,promised_delivery_utc and actual columns are order_id,actual_delivery_utc. Extra columns are ignored. IDs are case-sensitive ASCII [A-Za-z0-9][A-Za-z0-9_-]{0,63}, unique within each file; empty or padded IDs are errors.

Why: Exact schemas and an ID profile were not supplied; strict validation avoids accidental joins and spreadsheet formula execution.

Proposed owner: Operations data owner

Validation: Inspect representative exports, including leading-zero IDs and unusual ID characters; approve this contract or version a replacement before launch.

Launch blocker: true

### H2

Operations supplies two complete snapshots from the same order namespace and consistent export cutoff after the requested day ends. CSVs have no authoritative dataset/as-of metadata; the job cannot independently prove their business freshness or shared provenance.

Why: A correct join can still be wrong when files come from different sources or omit recently recorded deliveries.

Proposed owner: Operations data owner

Validation: Verify export procedure and late-arrival/correction timing; record source, cutoff and pair-selection evidence in the operating runbook before use.

Launch blocker: true

### H3

The daily report covers actual deliveries in the previous UTC calendar day by default, with an explicit --report-date override for backfills. It contains all delivered rows in that day, not only late rows; a boolean identifies lateness.

Why: Daily window and output inclusion were unspecified. One row per delivered order supports reconciliation and shows on-time results.

Proposed owner: Operations report owner

Validation: Confirm daily window and all-deliveries output on representative manual examples before launch.

Launch blocker: true

### H4

Accepted timestamps use YYYY-MM-DDTHH:MM:SS[.ffffff]Z or +00:00, with 1-6 fractional digits, valid Gregorian dates and seconds 00-59. Empty actual means undelivered; non-UTC offsets, missing promised values, leap seconds and greater precision fail validation.

Why: ISO UTC is broader than a single parser profile; exact bounded precision gives deterministic arithmetic.

Proposed owner: Operations data owner

Validation: Check real timestamp samples and establish this profile; unsupported valid ISO forms require an explicit parser-contract revision.

Launch blocker: true

### H5

Proposed operational budget is at most 100,000 rows and 50 MiB per file, 120 seconds per run, and a once-daily invocation at 08:00 UTC after exports are ready. Operations reviews local status by 10:00 UTC and acknowledges failures by 12:00 UTC; after that the operations lead manually escalates.

Why: Small, daily and operations ownership need concrete provisional limits and a local failure disposition.

Proposed owner: Operations report owner

Validation: Measure actual sizes/runtime and confirm schedule, staffing, acknowledgement and escalation practice before launch; tune versioned limits if necessary.

Launch blocker: true

### H6

Run on one trusted local host/account with two allowlisted input roots, a dedicated output root and same-filesystem staging. Only the job may mutate its output root; no symlinks are permitted in resolved input/output paths. An operator grants these local capabilities in configuration.

Why: Local filesystem isolation and atomic-directory publication are proposed controls, not verified deployment facts.

Proposed owner: Implementation owner

Validation: Exercise permissions, exclusive locks, fsync and directory rename/crash behavior on the chosen filesystem; confirm trusted-account boundary.

Launch blocker: true

### H7

Keep committed CSVs, manifests and local failure records for 30 days. Do not copy raw input files; persist hashes, counts and error row numbers without row contents. Delete expired files locally only through a separate operator-maintained procedure.

Why: No retention policy or personal-data classification was supplied; minimization and a provisional retention period need approval.

Proposed owner: Operations data owner

Validation: Approve access, retention and order-ID sensitivity before launch; verify any stricter organizational requirement.

Launch blocker: true

### H8

A date with an existing valid completed report is immutable: identical input/config returns ALREADY_COMPLETE; changed input/config returns CONFLICT. Corrections require the owner to archive the old date directory outside this job and rerun; no replacement action is implemented.

Why: Silent overwrites can cause the operations team to act on inconsistent reports.

Proposed owner: Operations report owner

Validation: Approve the manual correction/runbook rule and prove conflict behavior in a local staging environment.

Launch blocker: true

- context/CTX2: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- context/CTX2: H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- context/CTX2: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- context/CTX2: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- context/CTX3: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- context/CTX3: H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- context/CTX3: H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- context/CTX4: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- context/CTX4: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- context/CTX4: H7: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- context/CTX5: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- tasks/T0: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- tasks/T0: H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- tasks/T0: H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- tasks/T0: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- tasks/T0: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- tasks/T0: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- tasks/T1: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- tasks/T1: H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- tasks/T1: H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- tasks/T1: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- tasks/T1: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- tasks/T1: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- tasks/T2: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- tasks/T2: H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- tasks/T2: H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- tasks/T2: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- tasks/T2: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- tasks/T2: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- tasks/T3: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- tasks/T3: H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- tasks/T3: H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- tasks/T3: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- tasks/T3: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- tasks/T3: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- tasks/T4: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- tasks/T4: H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- tasks/T4: H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- tasks/T4: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- tasks/T4: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- tasks/T4: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- tasks/T5: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- tasks/T5: H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- tasks/T5: H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- tasks/T5: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- tasks/T5: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- tasks/T5: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- tasks/A1: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- tasks/A2: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- tasks/A3: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- components/C1: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- components/C1: H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- components/C1: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- components/C1: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- components/C1: H7: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- components/C1: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- components/C2: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- components/C2: H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- components/C2: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- components/C2: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- components/C2: H7: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- components/C2: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- components/C3: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- components/C3: H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- components/C3: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- components/C3: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- components/C3: H7: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- components/C3: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- components/C4: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- components/C4: H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- components/C4: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- components/C4: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- components/C4: H7: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- components/C4: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- components/C5: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- components/C5: H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- components/C5: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- components/C5: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- components/C5: H7: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- components/C5: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- components/C6: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- components/C6: H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- components/C6: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- components/C6: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- components/C6: H7: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- components/C6: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- workflow/W1: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- workflow/W1: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- workflow/W1: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- workflow/W2: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- workflow/W2: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- workflow/W2: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- workflow/W3: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- workflow/W3: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- workflow/W3: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- workflow/W4: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- workflow/W4: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- workflow/W4: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- workflow/W6: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- workflow/W6: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- workflow/W6: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- workflow/W9: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- workflow/W9: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- workflow/W9: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- workflow/W10: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- workflow/W10: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- workflow/W10: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- workflow/W11: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- workflow/W11: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- workflow/W11: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- framework/F1: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- framework/F1: H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- framework/F2: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- framework/F2: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- framework/F3: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- framework/F4: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- framework/F4: H2: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- framework/F4: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- framework/F5: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- framework/F5: H7: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- models: Zero LLM components and zero model calls/tokens/prices: all leaves are deterministic code. No fine-tuning, prompt budget, LLM retry, provider account or model spend is applicable. Runtime/storage/operator costs are unmeasured and excluded; zero LLM usage is not a claim of zero operating cost.
- fmea/FM1: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM1: H2: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM1: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM1: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM1: H7: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM1: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM2: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM2: H2: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM2: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM2: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM2: H7: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM2: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM3: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM3: H2: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM3: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM3: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM3: H7: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM3: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM4: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM4: H2: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM4: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM4: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM4: H7: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM4: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM5: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM5: H2: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM5: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM5: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM5: H7: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM5: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM6: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM6: H2: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM6: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM6: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM6: H7: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM6: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM7: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM7: H2: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM7: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM7: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM7: H7: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM7: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM8: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM8: H2: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM8: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM8: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM8: H7: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM8: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM9: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM9: H2: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM9: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM9: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM9: H7: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- fmea/FM9: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV1: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV1: H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV1: H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV1: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV1: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV1: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV2: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV2: H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV2: H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV2: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV2: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV2: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV3: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV3: H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV3: H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV3: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV3: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV3: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV4: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV4: H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV4: H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV4: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV4: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV4: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV5: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV5: H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV5: H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV5: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV5: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV5: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV6: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV6: H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV6: H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV6: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV6: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV6: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV7: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV7: H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV7: H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV7: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV7: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV7: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV8: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV8: H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV8: H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV8: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV8: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV8: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV9: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV9: H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV9: H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV9: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV9: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV9: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV10: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV10: H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV10: H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV10: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV10: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV10: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV11: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV11: H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV11: H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV11: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV11: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV11: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV12: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV12: H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV12: H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV12: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV12: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV12: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV13: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV13: H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV13: H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV13: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV13: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV13: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV14: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV14: H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV14: H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV14: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV14: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV14: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV15: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV15: H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV15: H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV15: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV15: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV15: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV16: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV16: H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV16: H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV16: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV16: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV16: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV17: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV17: H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV17: H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV17: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV17: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV17: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV18: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV18: H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV18: H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV18: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV18: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV18: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV19: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV19: H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV19: H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV19: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV19: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV19: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV20: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV20: H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV20: H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV20: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV20: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV20: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV21: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV21: H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV21: H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV21: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV21: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV21: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV22: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV22: H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV22: H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV22: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV22: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV22: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV23: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV23: H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV23: H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV23: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV23: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV23: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV24: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV24: H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV24: H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV24: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV24: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV24: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV25: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV25: H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV25: H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV25: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV25: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV25: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV26: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV26: H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV26: H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV26: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV26: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV26: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV27: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV27: H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV27: H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV27: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV27: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV27: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV28: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV28: H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV28: H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV28: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV28: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV28: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV29: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV29: H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV29: H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV29: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV29: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV29: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV30: H2: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV30: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV30: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV30: H7: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV31: H2: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV31: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV31: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV31: H7: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV32: H2: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV32: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV32: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- evals/EV32: H7: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- rollout/R1: H2: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- rollout/R1: H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- rollout/R1: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- rollout/R1: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- rollout/R1: H7: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- rollout/R1: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- rollout/R2: H2: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- rollout/R2: H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- rollout/R2: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- rollout/R2: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- rollout/R2: H7: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- rollout/R2: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- rollout/R3: H2: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- rollout/R3: H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- rollout/R3: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- rollout/R3: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- rollout/R3: H7: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- rollout/R3: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- rollout/R4: H2: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- rollout/R4: H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- rollout/R4: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- rollout/R4: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- rollout/R4: H7: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- rollout/R4: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- rollout/R5: H2: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- rollout/R5: H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- rollout/R5: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- rollout/R5: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- rollout/R5: H7: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- rollout/R5: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- rollout/R6: H2: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- rollout/R6: H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- rollout/R6: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- rollout/R6: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- rollout/R6: H7: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- rollout/R6: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- export/X1: H1: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- export/X1: H2: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- export/X1: H3: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- export/X1: H4: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- export/X1: H5: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- export/X1: H6: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- export/X1: H7: proposed assumption; full statement, owner and verification plan are in the top-level ledger.
- export/X1: H8: proposed assumption; full statement, owner and verification plan are in the top-level ledger.

## Review and tooling limitations

- AI self-review only, not stakeholder sign-off or independent review.
- No business report is implemented, scheduled or executed; all EV1-EV32 business tests are specifications.
- Real exports, source freshness, operating owners/limits, local filesystem guarantees and retention need H1-H8 evidence before launch.
- Design helper checks structure/relationships and renders documents; it does not prove fixture truth, business correctness or production impact.
- No source namespace/as-of metadata exists in the two CSV contract; H2 remains a real manual provenance/freshness prerequisite. Hashes alone cannot establish it.
- Design-only tooling: this helper makes no provider, network or business API calls and executes no business assertions; optional host-assistant research is outside this statement.
- Schema, reference, graph and ID-coverage checks do not establish semantic completeness, source truth, actual human authorization or production safety.
- Review scores and evidence are supplied by the reviewing agent; the helper checks their shape and declared pass conditions, not their truth.
- FMEA action/control text is required where specified; the helper does not verify ownership, release authority, regulatory compliance or risk acceptance.
