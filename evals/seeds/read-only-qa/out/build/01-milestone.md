# Retrieve only what this analyst may see

> PASS | DESIGN ONLY. self-review; round 1.

Depends on earlier milestones where their outputs are inputs below. Cross-milestone shared types are read by ID from ../design.json, not copied.

## Selected contracts

### C1 · Question interpreter

Turns the analyst's question into a retrieval query and the shape of answer wanted.

Reasoning: A model is the right tool here because the input is free-form language and nothing it produces reaches a system of record.

Data:

```json
{
  "group": "Agents (LLM)",
  "taskIds": [
    "T1"
  ],
  "inputs": [
    "questionText: string, required",
    "analystId: string, required"
  ],
  "outputs": [
    "queryText: string",
    "answerShape: enum FIGURE|LIST|SUMMARY",
    "topicTerms: array of string"
  ],
  "whyCode": "",
  "approvalRule": "No approval step: this component takes no action on any system of record, so there is nothing to approve. The analyst remains accountable for anything published from the answer."
}
```


Sources:

- context / user-brief: Today they search by filename and ask whoever wrote the report.

### C2 · Entitlement-filtered retriever

Searches the report index restricted to the reports this analyst is entitled to see, and returns passages with their report, page and version.

Reasoning: Filtering inside the query means a restricted passage never enters the model's context.

Assumptions:

- H1

- H5

Data:

```json
{
  "group": "Code: tools",
  "taskIds": [
    "T2.1"
  ],
  "inputs": [
    "queryText: string, required",
    "analystId: string, required",
    "teamIds: array of string, required"
  ],
  "outputs": [
    "passages: array of {passageId, reportId, page, version, supersededBy, text} on OK; empty on NO_MATCH",
    "passageCount: integer",
    "searchedScope: string",
    "status: enum OK|NO_MATCH|INDEX_UNAVAILABLE|ENTITLEMENT_UNRESOLVED",
    "errorDetail: string, required when status is not OK"
  ],
  "whyCode": "Entitlement filtering is a set operation on directory groups and report metadata. It must be repeatable and auditable, and it must not depend on anything a model produced.",
  "approvalRule": "No approval step: this component takes no action on any system of record, so there is nothing to approve. The analyst remains accountable for anything published from the answer."
}
```


Sources:

- hypothesis / H1: The report library exposes a read-only search index with per-report entitlement metadata, so the retriever can filter by what the asking analyst may see before any passage is read.

- hypothesis / H5: Analyst identity and team membership come from the corporate directory at session start and are not supplied by the analyst or inferred by the model.

### C3 · Document access check

Re-checks every returned passage against this analyst's entitlements before anything is drafted, and drops any passage that fails.

Reasoning: Defence in depth: the retriever filters, and this proves the filter held.

Assumptions:

- H1

Data:

```json
{
  "group": "Code: validation",
  "taskIds": [
    "T2.1"
  ],
  "inputs": [
    "passages: array of {passageId, reportId, page, version, supersededBy, text}, required",
    "analystId: string, required",
    "teamIds: array of string, required"
  ],
  "outputs": [
    "allowedPassages: array of {passageId, reportId, page, version, supersededBy, text}",
    "droppedCount: integer"
  ],
  "whyCode": "An access decision is a rule, not a judgement. It is deterministic code so the same analyst and the same report always produce the same answer, and so the check can be tested exhaustively.",
  "approvalRule": "No approval step: this component takes no action on any system of record, so there is nothing to approve. The analyst remains accountable for anything published from the answer."
}
```


Sources:

- context / user-brief: Not every analyst may see every report.

## Workflow rules

### W1 · Read the question

{"state": "Read-only QuestionState: questionId, analystId, teamIds, questionText, queryText, answerShape, passages with report, page and version, allowedPassages, safePassages, injectionFlags, sufficient, claims, verifiedClaims, uncitedClaims, supersededClaims, searchedScope, outcome. No field of this state is ever written back to any system of record.", "transitions": [{"to": "W2", "when": "question parsed into a query and an answer shape", "mode": "exclusive"}], "failureDisposition": "An unparseable question returns a decline asking the analyst to rephrase.", "timeout": "10s", "retryPolicy": "No retry: a failed step returns a decline naming the step that failed. Nothing is written, so there is nothing to reconcile and nothing a second attempt could duplicate.", "terminalDisposition": ""}

Reasoning: The only model step before retrieval; it shapes the search and nothing else.

Data:

```json
{
  "componentId": "C1",
  "taskIds": [
    "T1"
  ],
  "next": [
    "W2"
  ],
  "decision": false,
  "example": "Turn 'what did we say about warehouse automation payback last year' into a dated figure query."
}
```


Sources:

- context / user-brief: Today they search by filename and ask whoever wrote the report.

### W2 · Retrieve passages within this analyst's entitlement

{"state": "Read-only QuestionState: questionId, analystId, teamIds, questionText, queryText, answerShape, passages with report, page and version, allowedPassages, safePassages, injectionFlags, sufficient, claims, verifiedClaims, uncitedClaims, supersededClaims, searchedScope, outcome. No field of this state is ever written back to any system of record.", "transitions": [{"to": "W3", "when": "retrieval returned, with zero or more passages", "mode": "exclusive"}], "failureDisposition": "An index timeout returns a decline saying the library could not be searched, never an answer from the model's own knowledge.", "timeout": "5s", "retryPolicy": "No retry: a failed step returns a decline naming the step that failed. Nothing is written, so there is nothing to reconcile and nothing a second attempt could duplicate.", "terminalDisposition": ""}

Reasoning: Entitlement is applied inside the query, so a restricted passage is never retrieved at all.

Assumptions:

- H1

Data:

```json
{
  "componentId": "C2",
  "taskIds": [
    "T2.1"
  ],
  "next": [
    "W3"
  ],
  "decision": false,
  "example": "Search the 2024 and 2025 logistics reports this analyst's teams may see."
}
```


Sources:

- hypothesis / H1: The report library exposes a read-only search index with per-report entitlement metadata, so the retriever can filter by what the asking analyst may see before any passage is read.

### W3 · Check every passage is one this analyst may see

{"state": "Read-only QuestionState: questionId, analystId, teamIds, questionText, queryText, answerShape, passages with report, page and version, allowedPassages, safePassages, injectionFlags, sufficient, claims, verifiedClaims, uncitedClaims, supersededClaims, searchedScope, outcome. No field of this state is ever written back to any system of record.", "transitions": [{"to": "W4", "when": "at least one passage is within this analyst's entitlement", "mode": "exclusive"}, {"to": "W8", "when": "no retrieved passage is within this analyst's entitlement", "mode": "exclusive"}], "failureDisposition": "A passage whose entitlement cannot be resolved is dropped, never included on the benefit of the doubt.", "timeout": "2s", "retryPolicy": "No retry: a failed step returns a decline naming the step that failed. Nothing is written, so there is nothing to reconcile and nothing a second attempt could duplicate.", "terminalDisposition": ""}

Reasoning: The retriever filters and this proves the filter held; the two are separate components on purpose.

Assumptions:

- H1

- H5

Data:

```json
{
  "componentId": "C3",
  "taskIds": [
    "T2.1"
  ],
  "next": [
    "W4",
    "W8"
  ],
  "decision": true,
  "example": "Drop a passage from a client report belonging to a team this analyst is not on."
}
```


Sources:

- context / user-brief: Not every analyst may see every report.

## Required tests

For each ID below, load ../_evidence/eval-set.json items[id].data.input, .expected and .passRule. These are the full fixture, expected result and exact assertions; no inherited test context is assumed.

- EV1: A supported question is answered with a citation for every claim
- EV2: A question the library does not answer is declined, not guessed
- EV3: A claim drawn from a superseded edition is marked as superseded
- EV6: A passage outside the analyst's entitlement is dropped before drafting
- EV7: Offline answer quality on a labelled question set
- EV8: Offline adversarial set for injection and entitlement
- EV10: Live alerting on control failures
- EV11: Release suite
## Acceptance criteria

- A passage outside the asking analyst's entitlement is never returned by the retriever and is dropped again by the access check (EV6).
- The service runs on a read-only credential; the write scope is not configured.
- Entitlement comes from the directory at session start and is never taken from the request.
