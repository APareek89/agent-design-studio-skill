# Canonical design contract

Use `design.json` as the single source for all generated documents. The script reads the bundled `stage-schemas.json`; no app, Node packages or network are required. Schemas describe stage packets, not a web-app project backup. Do not copy app approval flags, timestamps or model credentials into this format.

```json
{
  "schemaVersion": "1.0",
  "title": "A descriptive project name",
  "brief": "The user's original brief, verbatim",
  "assumptions": [
    {"id":"H1","statement":"A specific proposed assumption","why":"Why it is needed","owner":"Proposed accountable role","validation":"Evidence needed to confirm it","launchBlocker":true}
  ],
  "stages": {
    "context":{"items":[],"assumptions":[]},
    "tasks":{"items":[],"assumptions":[]},
    "components":{"items":[],"assumptions":[]},
    "workflow":{"items":[],"assumptions":[]},
    "framework":{"items":[],"assumptions":[]},
    "models":{"items":[],"assumptions":[]},
    "fmea":{"items":[],"assumptions":[]},
    "evals":{"items":[],"assumptions":[]},
    "rollout":{"items":[],"assumptions":[]},
    "export":{"items":[],"assumptions":[]}
  }
}
```

The empty arrays above illustrate the container, not a completed design. Populate every stage; only Models may have zero items, and only with zero LLM components. Keep the brief unchanged. `H1...` record proposed facts, permissions, owners, thresholds, volumes and prices that the user did not supply. Empty assumptions is valid when nothing is assumed. All stage packet `assumptions` arrays contain concise strings; the top-level ledger carries the details.

Every item has `id`, `kind`, `title`, `description`, `reasoning`, `assumptions` (strings), `sources` and `data`. Source entries are `{type,file,passage}`: `context` uses `file:"user-brief"` and an exact quote; `hypothesis` uses an existing H ID and its statement. Do not fabricate an upload or verified citation. If optional source material is supplied, record what it actually establishes in the assumption ledger and prose; do not claim the basic validator verified external material. IDs are stable within a stage; links always use their real responsibility.

Use these complete `data` fields; use empty strings/arrays only for inapplicable fields:

- **Context** `CTX1...`, kind `context`: `field,value,question`. Put `question:""`; resolve missing inputs as labelled assumptions or launch dependencies, not unanswered gates.
- **Tasks** `T0,T1,T1.1...`, kind `task`: `parentId,mode,basis,examples,autonomy,frequency,risk`. Modes `sequence|choose one|leaf`; risks `low|medium|high`. Root `parentId:""`; depth at most root → task → subtask. Examples are strings. Kind `attribute`, IDs `A1...`: `taskIds,sourceSystem,loaded` (`session start|on demand`).
- **Components** `C1...`, kind `component`: `group,taskIds,inputs,outputs,whyCode,approvalRule`. Groups `Agents (LLM)|Code: tools|Code: validation|Code: human triggers`. Inputs/outputs are arrays of compact typed-field strings, including conditional required fields. Deterministic components require a `whyCode` explanation.
- **Workflow** `W1...`, kind `workflow`: `componentId,taskIds,next,decision,example`. The item `description` is a JSON string with `state`, `transitions:[{to,when,mode}]`, `failureDisposition`, `timeout`, `retryPolicy`, `terminalDisposition`. Each next edge has a matching predicate; terminals have no next edges and a nonempty terminal disposition. Put typed producer bindings for guard variables in this contract. Conditional commands and every tool outcome need coherent paths.
- **Architecture** `F1...`, kind `framework`: `category,taskIds,choice,alternatives,tradeoffs,permission,blastRadius,approvalRule,leastPrivilege,aws,gcp,azure,openSource`. Categories `fit|architecture|orchestration|permission|data`; permission `read|write|none`. State a chosen pattern and rejected alternative. Cloud/vendor options can be unverified candidates, clearly labelled; unsupported service/pricing facts are not required.
- **Models** `M1...`, kind `model`: `componentId,tier,rationale,fineTuneWhen,callsPerCase,inputTokens,outputTokens,inputPrice,outputPrice`. One per LLM component, zero for code. Tier `small|standard|reasoning`. Calls, tokens and USD per million token prices are numeric illustrative budgets unless measured. Derive calls from workflow nodes and bounded retries; explain unknown prices, branch mix and excluded costs. Zero cost inputs mean unpriced, not free service.
- **FMEA** `FM1...`, kind `fmea`: `taskIds,componentIds,effect,cause,severity,occurrence,detection,control,detectionMethod,action,metric,kpi,evalIds,acceptedRisk,commonToAll`. S/O/D are integer 1–10; RPN=S×O×D. `acceptedRisk:false` unless the user supplied a specific acceptance. Severity≥8 or RPN≥150 needs an owner and release gate in `action`. Do not manufacture human acceptance.
- **Evaluations** `EV1...`, kind `eval`: `category,taskIds,componentIds,failureModeIds,input,expected,passRule,metric,kpi,target,testSet,labelling,cadence,alertThreshold`. Categories `golden|offline|online|release`. Golden input/expected/passRule are JSON strings containing concrete fixtures, outcomes and assertions. Every unaccepted failure and high-risk leaf needs substantive golden coverage. All risk/eval links, including monitoring/release links, must agree in both directions. Planned tests are not executed tests.
- **Rollout** `R1...`, kind `rollout`: `category,businessKpi,aiMetrics,phase,gate,owner,experiment`. Categories `kpi|phase|experiment|owner`. Cover each with actual evidence definitions, not empty category cards. Phase-specific entry and exit evidence must avoid requiring results of a pilot before it starts.
- **Handoff** `X1...`, kind `export`: `acceptanceCriteria,buildInstructions`. Arrays for acceptance criteria; string instructions. Derive from earlier design decisions and IDs without adding capability or permission.

For a field/type error, inspect only that stage in `stage-schemas.json` or use the validator's precise path. The schemas bound item size and arrays, so split long responsibilities into real items; do not omit required detail merely to fit a single response.

## Review record

Write `review.json` separately, after inspecting the design:

```json
{
  "method":"self-review",
  "round":1,
  "status":"needs-work",
  "dimensions":[{"id":"D1","score":2,"evidence":["T1: specific evidence or omission"]}],
  "issues":[{"id":"ISSUE1","severity":"major","stage":"workflow","itemId":"W1","message":"Evidence, consequence and concrete fix","resolved":false}],
  "limitations":["Design review; business controls and provider reliability have not been executed."]
}
```

Populate D1 through D12 using `quality-rubric.json`; score each 0–4 with actual evidence. Method `independent-agent` requires a different evaluating agent; otherwise use `self-review`. Status can be `pass` only with all twelve scores ≥3, no unresolved critical/major finding, no structural errors and stated limitations. Preserve failed review rounds when revising; do not change thresholds to pass. `validation.json` records structural checks and never substitutes for this review.

## Golden fixtures

Prefer self-contained fixtures. If inheritance saves substantial repetition, each input must identify a named, versioned base available in the exported golden set, with an explicit merge/array-replacement/deletion convention. A different discriminated command must replace its entire payload: revoke/release/correction commands cannot inherit forbidden grant/create fields. Show the resolved effective fixture when reviewing. Validate the positive base first, then isolate one rejection condition and assert the exact reason and forbidden effect. Keep compound scenarios as additional tests. A future implementer must write the business test harness; the helper does not run business controls or verify the truth of model-authored assertions.

## Final presentation

`DESIGN.pdf` is the primary user-facing deliverable. The ten canonical stages and review remain the source; the PDF presents them without repeating complete packets or large inherited fixtures. Machine artifacts remain companions for coding agents. After PDF delivery, ask whether the user wants `DESIGN.html`, a read-only visual view in the same app stage order; do not generate that deliverable before opt-in. See `visual-output.md`.
