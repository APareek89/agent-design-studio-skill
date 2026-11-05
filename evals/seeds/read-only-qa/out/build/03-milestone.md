# Answer, and prove every citation

> PASS | DESIGN ONLY. self-review; round 1.

Depends on earlier milestones where their outputs are inputs below. Cross-milestone shared types are read by ID from ../design.json, not copied.

## Selected contracts

### C4 · Answer drafter

Writes the answer, tying every claim to the passage it came from.

Reasoning: Composing readable prose from several passages is what a model is for; the checking is not.

Data:

```json
{
  "group": "Agents (LLM)",
  "taskIds": [
    "T3"
  ],
  "inputs": [
    "safePassages: array of {passageId, reportId, page, version, supersededBy, text}, required",
    "questionText: string, required",
    "answerShape: enum FIGURE|LIST|SUMMARY, required"
  ],
  "outputs": [
    "draftText: string",
    "claims: array of {claimText, passageId}",
    "caveats: array of string"
  ],
  "whyCode": "",
  "approvalRule": "No approval step: this component takes no action on any system of record, so there is nothing to approve. The analyst remains accountable for anything published from the answer."
}
```


Sources:

- context / user-brief: cite the page it took each statement from

### C5 · Citation check

Rejects any claim whose cited passage was not among the retrieved passages, and marks any claim drawn from a superseded report.

Reasoning: The drafter proposes citations; this component is what makes them true.

Assumptions:

- H2

Data:

```json
{
  "group": "Code: validation",
  "taskIds": [
    "T3"
  ],
  "inputs": [
    "claims: array of {claimText, passageId}, required",
    "safePassages: array of {passageId, reportId, page, version, supersededBy, text}, required"
  ],
  "outputs": [
    "verifiedClaims: array of {claimText, passageId, reportId, page}",
    "uncitedClaims: array of string",
    "supersededClaims: array of string"
  ],
  "whyCode": "Matching a claim's passage against the retrieved set is an exact lookup. A model asked to check its own citations will agree with itself, which is why this is code.",
  "approvalRule": "No approval step: this component takes no action on any system of record, so there is nothing to approve. The analyst remains accountable for anything published from the answer."
}
```


Sources:

- context / user-brief: so an analyst can open the source and check it

### C7 · Answer renderer

Returns the answer with its citation list, or the decline with what was searched, to the analyst in the portal.

Reasoning: The last step is a formatter, not a decision, and it writes nothing.

Data:

```json
{
  "group": "Code: tools",
  "taskIds": [
    "T3",
    "T4"
  ],
  "inputs": [
    "verifiedClaims: array of {claimText, passageId, reportId, page}, required",
    "searchedScope: string, required",
    "declineReason: string"
  ],
  "outputs": [
    "renderedAnswer: string",
    "citationList: array of {reportId, page}",
    "outcome: enum ANSWERED|DECLINED"
  ],
  "whyCode": "Rendering is deterministic so that what the analyst reads is exactly what passed the citation check, with nothing added between the check and the screen.",
  "approvalRule": "No approval step: this component takes no action on any system of record, so there is nothing to approve. The analyst remains accountable for anything published from the answer."
}
```


Sources:

- context / user-brief: so an analyst can open the source and check it

## Workflow rules

### W6 · Draft the answer with a citation per claim

{"state": "Read-only QuestionState: questionId, analystId, teamIds, questionText, queryText, answerShape, passages with report, page and version, allowedPassages, safePassages, injectionFlags, sufficient, claims, verifiedClaims, uncitedClaims, supersededClaims, searchedScope, outcome. No field of this state is ever written back to any system of record.", "transitions": [{"to": "W7", "when": "draft produced with a passage cited for every claim", "mode": "exclusive"}], "failureDisposition": "A drafter failure returns a decline; a partial draft is never returned.", "timeout": "30s", "retryPolicy": "No retry: a failed step returns a decline naming the step that failed. Nothing is written, so there is nothing to reconcile and nothing a second attempt could duplicate.", "terminalDisposition": ""}

Reasoning: The model composes; it does not decide what counts as evidence.

Data:

```json
{
  "componentId": "C4",
  "taskIds": [
    "T3"
  ],
  "next": [
    "W7"
  ],
  "decision": false,
  "example": "Write two sentences on warehouse automation payback, each citing a report and page."
}
```


Sources:

- context / user-brief: cite the page it took each statement from

### W7 · Check every claim cites a retrieved passage

{"state": "Read-only QuestionState: questionId, analystId, teamIds, questionText, queryText, answerShape, passages with report, page and version, allowedPassages, safePassages, injectionFlags, sufficient, claims, verifiedClaims, uncitedClaims, supersededClaims, searchedScope, outcome. No field of this state is ever written back to any system of record.", "transitions": [{"to": "W9", "when": "every claim cites a passage that was actually retrieved", "mode": "exclusive"}, {"to": "W8", "when": "a claim cites no retrieved passage", "mode": "exclusive"}], "failureDisposition": "An uncited claim fails the whole answer rather than being quietly dropped from it, because the analyst would not know what was removed.", "timeout": "2s", "retryPolicy": "No retry: a failed step returns a decline naming the step that failed. Nothing is written, so there is nothing to reconcile and nothing a second attempt could duplicate.", "terminalDisposition": ""}

Reasoning: This is the component that makes a citation true rather than plausible.

Assumptions:

- H2

Data:

```json
{
  "componentId": "C5",
  "taskIds": [
    "T3"
  ],
  "next": [
    "W9",
    "W8"
  ],
  "decision": true,
  "example": "A claim citing a passage that was never retrieved fails the answer."
}
```


Sources:

- context / user-brief: so an analyst can open the source and check it

### W8 · Return a decline naming what was searched

{"state": "Read-only QuestionState: questionId, analystId, teamIds, questionText, queryText, answerShape, passages with report, page and version, allowedPassages, safePassages, injectionFlags, sufficient, claims, verifiedClaims, uncitedClaims, supersededClaims, searchedScope, outcome. No field of this state is ever written back to any system of record.", "transitions": [], "failureDisposition": "Not applicable: this is a terminal step that returns text to the caller.", "timeout": "2s", "retryPolicy": "No retry: a failed step returns a decline naming the step that failed. Nothing is written, so there is nothing to reconcile and nothing a second attempt could duplicate.", "terminalDisposition": "DECLINED: the analyst is told what was searched and why no answer was given. Nothing is written."}

Reasoning: A decline is a finished case, and naming the searched scope is what makes it useful.

Data:

```json
{
  "componentId": "C7",
  "taskIds": [
    "T4"
  ],
  "next": [],
  "decision": false,
  "example": "Searched 2019-2025 logistics reports; nothing states a payback figure for cold-chain in Vietnam."
}
```


Sources:

- context / user-brief: If the reports do not answer the question it should say so plainly rather than guess.

### W9 · Return the answer with its citations

{"state": "Read-only QuestionState: questionId, analystId, teamIds, questionText, queryText, answerShape, passages with report, page and version, allowedPassages, safePassages, injectionFlags, sufficient, claims, verifiedClaims, uncitedClaims, supersededClaims, searchedScope, outcome. No field of this state is ever written back to any system of record.", "transitions": [], "failureDisposition": "Not applicable: this is a terminal step that returns text to the caller.", "timeout": "2s", "retryPolicy": "No retry: a failed step returns a decline naming the step that failed. Nothing is written, so there is nothing to reconcile and nothing a second attempt could duplicate.", "terminalDisposition": "ANSWERED: the analyst receives the verified claims and a citation list. Nothing is written."}

Reasoning: What the analyst reads is exactly what passed the citation check.

Data:

```json
{
  "componentId": "C7",
  "taskIds": [
    "T3"
  ],
  "next": [],
  "decision": false,
  "example": "Two cited sentences plus a list of the report and page behind each."
}
```


Sources:

- context / user-brief: so an analyst can open the source and check it

## Required tests

For each ID below, load ../_evidence/eval-set.json items[id].data.input, .expected and .passRule. These are the full fixture, expected result and exact assertions; no inherited test context is assumed.

- EV1: A supported question is answered with a citation for every claim
- EV2: A question the library does not answer is declined, not guessed
- EV3: A claim drawn from a superseded edition is marked as superseded
- EV4: A claim citing a passage that was never retrieved fails the answer
- EV5: An instruction inside a report is neutralised, not followed
- EV7: Offline answer quality on a labelled question set
- EV9: Live sample of answered questions
- EV10: Live alerting on control failures
- EV11: Release suite
## Acceptance criteria

- Every claim resolves to a retrieved passage, and an uncited claim fails the whole answer (EV1, EV4).
- A claim from a superseded edition is marked with the superseding report (EV3).
- What the analyst reads is exactly what passed the citation check.
