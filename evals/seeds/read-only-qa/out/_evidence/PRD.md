# Analyst research assistant for the internal report library

> PASS | DESIGN ONLY. self-review; round 1.

## Original brief

We want a research assistant for our 50 internal analysts. They spend hours hunting through our own research reports - about 4,000 PDFs going back six years, plus the weekly market notes - to answer questions such as "what did we say about warehouse automation payback last year" or "which reports cover cold-chain logistics in Vietnam". Today they search by filename and ask whoever wrote the report.

The assistant should answer questions from those reports and cite the page it took each statement from, so an analyst can open the source and check it. It must never take any action: no posting, no editing a report, no sending anything, no updating any system of record. If the reports do not answer the question it should say so plainly rather than guess.

Not every analyst may see every report. Some client work is restricted to the team that did it, and the assistant must respect those entitlements.

We expect roughly 3,000 questions a month from the 50 analysts. English only. We are not in a regulated industry, but an answer that is confidently wrong would cost us more client trust than a slow answer ever would. Success looks like an analyst getting a cited answer in under two minutes where it takes about twenty minutes today.

## Context

- **CTX1 Business decision and boundary**: What the assistant decides, and the boundary it never crosses.
- **CTX2 Actors, users and decision owners**: Who asks, who answers for the answer, and who owns the library.
- **CTX3 Trigger, first-release scope and non-goals**: What starts a case, what the first release covers, and what is out of scope.
- **CTX4 Success measures and end conditions**: The outcome the business is buying, and when a case is finished.
- **CTX5 Constraints, entitlements and privacy**: The limits the design must hold, and the one that is not negotiable.
- **CTX6 Evidence limits and unknowns**: What this design rests on that has not been checked.

## Tasks

- **T0 Answer an analyst's question from the report library**: The whole job, from a question typed in the portal to a cited answer or a decline.
- **T1 Understand what is being asked**: Turn an analyst's question into a retrieval query and the kind of answer wanted.
- **T2 Find the passages that bear on the question**: Retrieve candidate passages and decide whether they actually answer it.
- **T2.1 Retrieve passages this analyst may see**: Search the report index restricted to the reports this analyst is entitled to.
- **T2.2 Judge whether the passages answer the question**: Decide whether what was retrieved supports an answer, or whether the library is silent.
- **T3 Write the answer with a citation for every claim**: Draft the answer so every statement names the report and page it came from.
- **T4 Decline when the reports do not answer it**: Return a decline that names what was searched, so the analyst knows where to look next.
- **A1 Analyst identity and team**: Who is asking, and which teams they belong to.
- **A2 Report entitlement metadata**: Which teams may see which reports.
- **A3 Report passages, pages and version**: The extracted text with its page number, report version and superseded-by marker.

## Components

- **C1 Question interpreter**: Turns the analyst's question into a retrieval query and the shape of answer wanted.
- **C2 Entitlement-filtered retriever**: Searches the report index restricted to the reports this analyst is entitled to see, and returns passages with their report, page and version.
- **C3 Document access check**: Re-checks every returned passage against this analyst's entitlements before anything is drafted, and drops any passage that fails.
- **C8 Document instruction guard**: Neutralises any text inside a retrieved passage that reads as an instruction to the assistant, and marks the passage as containing one.
- **C6 Sufficiency gate**: Decides whether the surviving passages actually support an answer, or whether the library is silent on the question.
- **C4 Answer drafter**: Writes the answer, tying every claim to the passage it came from.
- **C5 Citation check**: Rejects any claim whose cited passage was not among the retrieved passages, and marks any claim drawn from a superseded report.
- **C7 Answer renderer**: Returns the answer with its citation list, or the decline with what was searched, to the analyst in the portal.

## Workflow

- **W1 Read the question**: {"state": "Read-only QuestionState: questionId, analystId, teamIds, questionText, queryText, answerShape, passages with report, page and version, allowedPassages, safePassages, injectionFlags, sufficient, claims, verifiedClaims, uncitedClaims, supersededClaims, searchedScope, outcome. No field of this state is ever written back to any system of record.", "transitions": [{"to": "W2", "when": "question parsed into a query and an answer shape", "mode": "exclusive"}], "failureDisposition": "An unparseable question returns a decline asking the analyst to rephrase.", "timeout": "10s", "retryPolicy": "No retry: a failed step returns a decline naming the step that failed. Nothing is written, so there is nothing to reconcile and nothing a second attempt could duplicate.", "terminalDisposition": ""}
- **W2 Retrieve passages within this analyst's entitlement**: {"state": "Read-only QuestionState: questionId, analystId, teamIds, questionText, queryText, answerShape, passages with report, page and version, allowedPassages, safePassages, injectionFlags, sufficient, claims, verifiedClaims, uncitedClaims, supersededClaims, searchedScope, outcome. No field of this state is ever written back to any system of record.", "transitions": [{"to": "W3", "when": "retrieval returned, with zero or more passages", "mode": "exclusive"}], "failureDisposition": "An index timeout returns a decline saying the library could not be searched, never an answer from the model's own knowledge.", "timeout": "5s", "retryPolicy": "No retry: a failed step returns a decline naming the step that failed. Nothing is written, so there is nothing to reconcile and nothing a second attempt could duplicate.", "terminalDisposition": ""}
- **W3 Check every passage is one this analyst may see**: {"state": "Read-only QuestionState: questionId, analystId, teamIds, questionText, queryText, answerShape, passages with report, page and version, allowedPassages, safePassages, injectionFlags, sufficient, claims, verifiedClaims, uncitedClaims, supersededClaims, searchedScope, outcome. No field of this state is ever written back to any system of record.", "transitions": [{"to": "W4", "when": "at least one passage is within this analyst's entitlement", "mode": "exclusive"}, {"to": "W8", "when": "no retrieved passage is within this analyst's entitlement", "mode": "exclusive"}], "failureDisposition": "A passage whose entitlement cannot be resolved is dropped, never included on the benefit of the doubt.", "timeout": "2s", "retryPolicy": "No retry: a failed step returns a decline naming the step that failed. Nothing is written, so there is nothing to reconcile and nothing a second attempt could duplicate.", "terminalDisposition": ""}
- **W4 Neutralise instructions found inside report text**: {"state": "Read-only QuestionState: questionId, analystId, teamIds, questionText, queryText, answerShape, passages with report, page and version, allowedPassages, safePassages, injectionFlags, sufficient, claims, verifiedClaims, uncitedClaims, supersededClaims, searchedScope, outcome. No field of this state is ever written back to any system of record.", "transitions": [{"to": "W5", "when": "passage text neutralised and any instruction flagged", "mode": "exclusive"}], "failureDisposition": "A passage that cannot be neutralised is dropped and flagged rather than passed to the drafter.", "timeout": "2s", "retryPolicy": "No retry: a failed step returns a decline naming the step that failed. Nothing is written, so there is nothing to reconcile and nothing a second attempt could duplicate.", "terminalDisposition": ""}
- **W5 Decide whether the passages support an answer**: {"state": "Read-only QuestionState: questionId, analystId, teamIds, questionText, queryText, answerShape, passages with report, page and version, allowedPassages, safePassages, injectionFlags, sufficient, claims, verifiedClaims, uncitedClaims, supersededClaims, searchedScope, outcome. No field of this state is ever written back to any system of record.", "transitions": [{"to": "W6", "when": "passages support an answer of the requested shape", "mode": "exclusive"}, {"to": "W8", "when": "passages do not support an answer; the library is silent on this question", "mode": "exclusive"}], "failureDisposition": "If sufficiency cannot be decided the case declines, because a decline is recoverable and a wrong answer is not.", "timeout": "2s", "retryPolicy": "No retry: a failed step returns a decline naming the step that failed. Nothing is written, so there is nothing to reconcile and nothing a second attempt could duplicate.", "terminalDisposition": ""}
- **W6 Draft the answer with a citation per claim**: {"state": "Read-only QuestionState: questionId, analystId, teamIds, questionText, queryText, answerShape, passages with report, page and version, allowedPassages, safePassages, injectionFlags, sufficient, claims, verifiedClaims, uncitedClaims, supersededClaims, searchedScope, outcome. No field of this state is ever written back to any system of record.", "transitions": [{"to": "W7", "when": "draft produced with a passage cited for every claim", "mode": "exclusive"}], "failureDisposition": "A drafter failure returns a decline; a partial draft is never returned.", "timeout": "30s", "retryPolicy": "No retry: a failed step returns a decline naming the step that failed. Nothing is written, so there is nothing to reconcile and nothing a second attempt could duplicate.", "terminalDisposition": ""}
- **W7 Check every claim cites a retrieved passage**: {"state": "Read-only QuestionState: questionId, analystId, teamIds, questionText, queryText, answerShape, passages with report, page and version, allowedPassages, safePassages, injectionFlags, sufficient, claims, verifiedClaims, uncitedClaims, supersededClaims, searchedScope, outcome. No field of this state is ever written back to any system of record.", "transitions": [{"to": "W9", "when": "every claim cites a passage that was actually retrieved", "mode": "exclusive"}, {"to": "W8", "when": "a claim cites no retrieved passage", "mode": "exclusive"}], "failureDisposition": "An uncited claim fails the whole answer rather than being quietly dropped from it, because the analyst would not know what was removed.", "timeout": "2s", "retryPolicy": "No retry: a failed step returns a decline naming the step that failed. Nothing is written, so there is nothing to reconcile and nothing a second attempt could duplicate.", "terminalDisposition": ""}
- **W8 Return a decline naming what was searched**: {"state": "Read-only QuestionState: questionId, analystId, teamIds, questionText, queryText, answerShape, passages with report, page and version, allowedPassages, safePassages, injectionFlags, sufficient, claims, verifiedClaims, uncitedClaims, supersededClaims, searchedScope, outcome. No field of this state is ever written back to any system of record.", "transitions": [], "failureDisposition": "Not applicable: this is a terminal step that returns text to the caller.", "timeout": "2s", "retryPolicy": "No retry: a failed step returns a decline naming the step that failed. Nothing is written, so there is nothing to reconcile and nothing a second attempt could duplicate.", "terminalDisposition": "DECLINED: the analyst is told what was searched and why no answer was given. Nothing is written."}
- **W9 Return the answer with its citations**: {"state": "Read-only QuestionState: questionId, analystId, teamIds, questionText, queryText, answerShape, passages with report, page and version, allowedPassages, safePassages, injectionFlags, sufficient, claims, verifiedClaims, uncitedClaims, supersededClaims, searchedScope, outcome. No field of this state is ever written back to any system of record.", "transitions": [], "failureDisposition": "Not applicable: this is a terminal step that returns text to the caller.", "timeout": "2s", "retryPolicy": "No retry: a failed step returns a decline naming the step that failed. Nothing is written, so there is nothing to reconcile and nothing a second attempt could duplicate.", "terminalDisposition": "ANSWERED: the analyst receives the verified claims and a citation list. Nothing is written."}

## Framework

### F1 · Why an assistant fits

Whether this needs an agent at all.

Reasoning: The honest answer is that most of the value is better search, and the design says so.

Data:

```json
{
  "category": "fit",
  "taskIds": [
    "T0"
  ],
  "choice": "A retrieval assistant, with a model only for reading the question and composing the answer. Most of the gain is entitlement-aware search over 4,000 reports.",
  "alternatives": [
    "A plain search box with better indexing, no model at all",
    "A fine-tuned model trained on the report corpus"
  ],
  "tradeoffs": "Plain search is cheaper and would capture much of the value, but leaves the analyst to read twenty passages. Fine-tuning bakes the corpus into weights, which makes citation impossible and staleness invisible, so it is rejected outright for this use.",
  "permission": "read",
  "blastRadius": "An unhelpful answer wastes an analyst's time; it cannot change any record.",
  "approvalRule": "No approval step: this component takes no action on any system of record, so there is nothing to approve. The analyst remains accountable for anything published from the answer.",
  "leastPrivilege": "The service holds one read-only credential scoped to the report index.",
  "aws": "Amazon Bedrock with OpenSearch",
  "gcp": "Vertex AI with Vector Search",
  "azure": "Azure AI Search with Azure OpenAI",
  "openSource": "An open-source vector store behind a self-hosted model gateway"
}
```


Sources:

- context / user-brief: They spend hours hunting through our own research reports

### F2 · Retrieve, gate, draft, check

The shape of the pipeline.

Reasoning: Putting the sufficiency gate before the drafter is what makes a decline possible.

Data:

```json
{
  "category": "architecture",
  "taskIds": [
    "T2",
    "T3"
  ],
  "choice": "A fixed four-stage pipeline: filtered retrieval, a code sufficiency gate, a model draft, then a code citation check that can fail the whole answer.",
  "alternatives": [
    "A single model call given the passages and asked to cite its sources",
    "An agent loop free to search repeatedly until it is satisfied"
  ],
  "tradeoffs": "One model call is simpler but makes the model the judge of its own evidence, which is the failure in FM3. A free search loop has no bounded cost and no point at which sufficiency is decided, so there is no principled moment to decline. Override needs a named owner.",
  "permission": "read",
  "blastRadius": "A pipeline change can affect every answer, so each stage has its own golden.",
  "approvalRule": "No approval step: this component takes no action on any system of record, so there is nothing to approve. The analyst remains accountable for anything published from the answer.",
  "leastPrivilege": "Each stage receives only the fields the next stage needs.",
  "aws": "Step Functions or a plain service",
  "gcp": "Workflows or a plain service",
  "azure": "Durable Functions or a plain service",
  "openSource": "A plain service; the pipeline is short enough not to need an orchestrator"
}
```


Sources:

- context / user-brief: The assistant should answer questions from those reports and cite the page it took each statement from, so an analyst can open the source and check it.

### F3 · Entitlement in the query

Where the access decision happens.

Reasoning: Filtering after drafting means the restricted text was already in the model's context.

Assumptions:

- H1

- H5

Data:

```json
{
  "category": "permission",
  "taskIds": [
    "T2.1"
  ],
  "choice": "The retriever filters by the analyst's directory groups inside the query, and a separate code check re-tests every returned passage before drafting.",
  "alternatives": [
    "Retrieve everything and filter the answer afterwards",
    "Trust the retriever's filter and skip the second check"
  ],
  "tradeoffs": "Filtering afterwards puts restricted text into the model's context, where a summary can leak it without quoting it. Skipping the second check leaves one point of failure in front of the highest-severity risk.",
  "permission": "read",
  "blastRadius": "A failure here is a confidentiality breach, which is why there are two independent checks.",
  "approvalRule": "No approval step: this component takes no action on any system of record, so there is nothing to approve. The analyst remains accountable for anything published from the answer.",
  "leastPrivilege": "One read-only credential, scoped to the index, with no write scope available to request.",
  "aws": "IAM role with read-only access to the index",
  "gcp": "Service account with viewer role on the index",
  "azure": "Managed identity with read-only data-plane access",
  "openSource": "A read-only index user; the write path is not configured at all"
}
```


Sources:

- context / user-brief: Some client work is restricted to the team that did it, and the assistant must respect those entitlements.

### F5 · Retrieval and embeddings

The capability that finds the passages.

Reasoning: Named as a capability so the candidates can be checked before anything is bought.

Data:

```json
{
  "category": "tooling",
  "taskIds": [
    "T2.1"
  ],
  "choice": "A hybrid index: keyword search for report numbers and places, vector search for topic questions, with entitlement as a hard filter on both.",
  "alternatives": [
    "Vector search alone",
    "Keyword search alone"
  ],
  "tradeoffs": "Vector search alone misses exact report numbers analysts quote; keyword alone misses the topic questions that are most of the value.",
  "permission": "read",
  "blastRadius": "Retrieval quality sets the ceiling for every answer.",
  "approvalRule": "No approval step: this component takes no action on any system of record, so there is nothing to approve. The analyst remains accountable for anything published from the answer.",
  "leastPrivilege": "Read-only index credential.",
  "aws": "Amazon OpenSearch Serverless",
  "gcp": "Vertex AI Vector Search",
  "azure": "Azure AI Search",
  "openSource": "Qdrant, Weaviate or pgvector",
  "capability": "retrieval and embeddings",
  "candidates": [
    {
      "name": "Azure AI Search",
      "kind": "managed",
      "note": "Hybrid keyword and vector search with filters. No web search tool was available during this design, so this candidate is a name to check, not a recommendation.",
      "verified": false,
      "sourceIds": []
    },
    {
      "name": "Qdrant",
      "kind": "open-source",
      "note": "Vector search with payload filtering. No web search tool was available during this design, so this candidate is a name to check, not a recommendation.",
      "verified": false,
      "sourceIds": []
    },
    {
      "name": "pgvector",
      "kind": "open-source",
      "note": "Vector search inside an existing Postgres. No web search tool was available during this design, so this candidate is a name to check, not a recommendation.",
      "verified": false,
      "sourceIds": []
    }
  ]
}
```


Sources:

- context / user-brief: about 4,000 PDFs going back six years, plus the weekly market notes

### F6 · From PDF to a citable passage

Extraction and chunking, chosen together.

Reasoning: Both are constrained by the same requirement: an analyst must be able to open the cited page.

Assumptions:

- H2

- H3

Data:

```json
{
  "category": "tooling",
  "taskIds": [
    "T2.1",
    "T3"
  ],
  "choice": "Extract text with page numbers, including the scanned earlier years, then chunk by section carrying the page, version and superseded-by marker on every chunk.",
  "alternatives": [
    "A plain PDF text library with fixed-size chunks and no page metadata",
    "Whole-report embeddings with no chunking"
  ],
  "tradeoffs": "A plain library is free and fine for born-digital reports but returns nothing for the scanned years, and fixed-size chunks cannot cite a page. Whole-report embeddings cannot point an analyst at anything they can check. Both fail the brief's one explicit requirement. Re-indexing runs on publication and withdrawal so a withdrawn report stops being quoted as current.",
  "permission": "read",
  "blastRadius": "A bad extraction or chunking makes a report unfindable or uncitable; it changes no record.",
  "approvalRule": "No approval step: this component takes no action on any system of record, so there is nothing to approve. The analyst remains accountable for anything published from the answer.",
  "leastPrivilege": "The extractor reads the report store and writes only to the index it owns.",
  "aws": "Amazon Textract plus S3 and OpenSearch",
  "gcp": "Google Document AI plus Vector Search",
  "azure": "Azure AI Document Intelligence plus Azure AI Search",
  "openSource": "OCRmyPDF with Tesseract and pdfplumber, into an open-source vector index",
  "capability": "document AI and OCR",
  "candidates": [
    {
      "name": "Azure AI Document Intelligence",
      "kind": "managed",
      "note": "Layout and page-aware extraction. No web search tool was available during this design, so this candidate is a name to check, not a recommendation.",
      "verified": false,
      "sourceIds": []
    },
    {
      "name": "Amazon Textract",
      "kind": "managed",
      "note": "Page-aware extraction with table support. No web search tool was available during this design, so this candidate is a name to check, not a recommendation.",
      "verified": false,
      "sourceIds": []
    },
    {
      "name": "OCRmyPDF with Tesseract",
      "kind": "open-source",
      "note": "OCR for the scanned back catalogue. No web search tool was available during this design, so this candidate is a name to check, not a recommendation.",
      "verified": false,
      "sourceIds": []
    }
  ]
}
```


Sources:

- context / user-brief: about 4,000 PDFs going back six years


## Models

- **M1 Question interpreter model**: A small model turns a question into a query and an answer shape.
- **M2 Answer drafter model**: A standard model composes the answer from the retrieved passages.

## Fmea

- **FM1 A superseded report is quoted as current**: Wrong or stale source. Hypothetical S/O/D: severity 1 negligible to 10 catastrophic; occurrence 1 rare to 10 frequent; detection 1 caught before harm to 10 rarely detected. Scores prioritise review, not probability. RPN 144.
- **FM2 A claim reaches the analyst with no citation**: Missing citation. Hypothetical S/O/D: severity 1 negligible to 10 catastrophic; occurrence 1 rare to 10 frequent; detection 1 caught before harm to 10 rarely detected. Scores prioritise review, not probability. RPN 189.
- **FM3 The assistant answers from outside the corpus**: An answer outside the corpus. Hypothetical S/O/D: severity 1 negligible to 10 catastrophic; occurrence 1 rare to 10 frequent; detection 1 caught before harm to 10 rarely detected. Scores prioritise review, not probability. RPN 160.
- **FM4 Prompt injection carried in a report**: Prompt injection through documents. Hypothetical S/O/D: severity 1 negligible to 10 catastrophic; occurrence 1 rare to 10 frequent; detection 1 caught before harm to 10 rarely detected. Scores prioritise review, not probability. RPN 120.
- **FM5 A restricted passage reaches an analyst without entitlement**: Leaking content the reader may not see; an access control failure. Hypothetical S/O/D: severity 1 negligible to 10 catastrophic; occurrence 1 rare to 10 frequent; detection 1 caught before harm to 10 rarely detected. Scores prioritise review, not probability. RPN 160.
- **FM6 A confident answer when the corpus is silent**: A confident answer when the corpus is silent. Hypothetical S/O/D: severity 1 negligible to 10 catastrophic; occurrence 1 rare to 10 frequent; detection 1 caught before harm to 10 rarely detected. Scores prioritise review, not probability. RPN 126.

## Evals

- **EV1 A supported question is answered with a citation for every claim**: The positive answer case: two passages support two claims, and both claims carry a report and page.
- **EV2 A question the library does not answer is declined, not guessed**: The negative answer case: passages mention the topic but state no figure, so the case declines.
- **EV3 A claim drawn from a superseded edition is marked as superseded**: A passage whose supersededBy is set is usable, but the answer must say so.
- **EV4 A claim citing a passage that was never retrieved fails the answer**: The drafter invents a plausible citation; the citation check rejects the whole answer.
- **EV5 An instruction inside a report is neutralised, not followed**: A retrieved passage contains instruction-shaped text; the guard flags and neutralises it.
- **EV6 A passage outside the analyst's entitlement is dropped before drafting**: A cross-team passage survives retrieval; the access check drops it and it never reaches the drafter.
- **EV7 Offline answer quality on a labelled question set**: 300 questions with known answers and known gaps, scored for unsupported claims, missing citations and correct declines.
- **EV8 Offline adversarial set for injection and entitlement**: 120 planted cases: instruction text inside reports, and questions aimed at content the asker may not see.
- **EV9 Live sample of answered questions**: Fifty answers a week are re-read against their cited pages by an analyst who did not ask the question.
- **EV10 Live alerting on control failures**: Counts the answers rejected by the citation check, the passages dropped by the access check and the injection flags raised, and alerts on a change in any of them.
- **EV11 Release suite**: Every golden plus both offline sets, run as one gate before any release reaches analysts.

## Rollout

### R1 · Time to a cited answer

The headline measure the brief states.

Reasoning: It is the only number the brief gives, so it is the one the rollout is judged on.

Assumptions:

- H6

Data:

```json
{
  "category": "kpi",
  "businessKpi": "Median minutes from question to a cited answer the analyst accepts: baseline about 20 minutes by hand (H6, stated in the brief and not yet measured) -> target under 2 minutes.",
  "aiMetrics": [
    "Median end-to-end latency; share of answers accepted without correction."
  ],
  "phase": "Measured in shadow, gated at pilot.",
  "gate": "Baseline must be measured on twenty real questions before the shadow phase starts; a target claimed against an unmeasured baseline is not evidence.",
  "owner": "Head of Research Operations",
  "experiment": "Compare the assistant's cited answer against the same analyst's hand search on the same question."
}
```


Sources:

- context / user-brief: Success looks like an analyst getting a cited answer in under two minutes where it takes about twenty minutes today.

### R2 · Answers accepted without correction

Whether analysts trust what comes back.

Reasoning: Speed with a wrong answer is worse than the status quo, so the quality KPI sits beside the time one.

Data:

```json
{
  "category": "kpi",
  "businessKpi": "Share of answered questions the analyst accepts without correcting a claim or a citation: baseline unknown, there is no system today, so it is collected from the first week of the shadow phase -> target above 85 per cent by the end of the pilot.",
  "aiMetrics": [
    "Unsupported-claim rate (EV7); share of sampled claims the cited page does not support (EV9)."
  ],
  "phase": "Collected in shadow, gated at general release.",
  "gate": "No general release until the pilot shows acceptance above 85 per cent with the unsupported-claim rate under 1 per cent.",
  "owner": "Head of Research",
  "experiment": "Reviewers mark each sampled answer accepted, corrected or rejected, with the reason."
}
```


Sources:

- context / user-brief: an answer that is confidently wrong would cost us more client trust than a slow answer ever would

### R3 · Shadow phase

The assistant answers, and only the reviewing analysts see it.

Reasoning: Entry and exit evidence that does not require the results of the phase it gates.

Assumptions:

- H6

Data:

```json
{
  "category": "phase",
  "businessKpi": "No business KPI is claimed in shadow; it exists to collect the R1 and R2 baselines.",
  "aiMetrics": [
    "EV7 and EV8 pass; EV9 sampling runs at fifty a week."
  ],
  "phase": "Shadow: four weeks, questions answered but shown only to the reviewing analysts.",
  "gate": "Entry: both offline sets pass and the R1 baseline is measured. Exit: four weeks of EV9 sampling with zero entitlement findings and zero unmarked superseded citations.",
  "owner": "Research Platform Lead",
  "experiment": "Not an experiment; this phase collects the baseline the later comparison needs."
}
```


Sources:

- hypothesis / H6: A baseline of about twenty minutes to find a cited answer by hand, taken from the brief and not yet measured.

### R4 · Pilot with one team, then all fifty analysts

One team of analysts uses it for real work, then the rest.

Reasoning: A confidentiality failure is contained to one team if it happens, and that team knows to watch for it.

Assumptions:

- H4

Data:

```json
{
  "category": "phase",
  "businessKpi": "R1 under four minutes and R2 above 70 per cent within the pilot team before widening.",
  "aiMetrics": [
    "EV9 weekly; EV10 alerting live with named owners."
  ],
  "phase": "Pilot: six weeks with the logistics team, then all 50 analysts.",
  "gate": "Entry: shadow exit met. Exit to full release: six weeks with no entitlement finding, R2 above 70 per cent, and the decline rate inside its band. A single out-of-entitlement citation returns to shadow.",
  "owner": "Head of Research Operations",
  "experiment": "Compare pilot-team time-to-answer against the same team's measured baseline."
}
```


Sources:

- context / user-brief: We expect roughly 3,000 questions a month from the 50 analysts.

### R5 · Does a decline beat a hedged answer?

The one genuine open question: whether analysts prefer a decline or a caveated partial answer.

Reasoning: The design assumes a decline is better; that assumption is worth testing rather than asserting.

Data:

```json
{
  "category": "experiment",
  "businessKpi": "Share of analysts who rate the response useful, decline against hedged answer.",
  "aiMetrics": [
    "Decline rate; usefulness rating; follow-up question rate after each response type."
  ],
  "phase": "Runs inside the pilot, from week three.",
  "gate": "Only runs once EV2 passes, so both arms are built on a working sufficiency gate. The hedged arm still carries a citation for every claim; it is not permission to answer without evidence.",
  "owner": "Head of Research",
  "experiment": "Split by question, not by analyst: half the insufficient cases return a decline naming the searched scope, half return what was found with an explicit statement of what was missing."
}
```


Sources:

- context / user-brief: If the reports do not answer the question it should say so plainly rather than guess.

### R6 · Named owners

Who owns what, by name of role.

Reasoning: Every gate above names an owner; this card is where they are collected.

Data:

```json
{
  "category": "owner",
  "businessKpi": "Not a KPI card: it records accountability for the gates above.",
  "aiMetrics": [
    "Each owner receives the metric for their own gate, not a shared dashboard."
  ],
  "phase": "All phases.",
  "gate": "No phase advances without its named owner recorded as having seen the exit evidence.",
  "owner": "Head of Research owns answer quality; IT Security owns entitlement and injection; Research Platform Lead owns availability and the live alerts; Head of Research Operations owns the library and the time-to-answer KPI.",
  "experiment": "Not an experiment."
}
```


Sources:

- context / user-brief: We want a research assistant for our 50 internal analysts.


## Export

### X1 · Build handoff

What a coding agent receives, and what it must not infer from it.

Reasoning: The boundary is the whole point of this design, so the handoff restates it.

Assumptions:

- H1

- H2

- H5

Data:

```json
{
  "acceptanceCriteria": [
    "Every claim returned to an analyst resolves to a passage that was actually retrieved for that question; an answer containing an uncited claim is rejected whole (EV1, EV4).",
    "A question the retrieved passages do not support returns a decline naming the searched scope, with zero citations (EV2).",
    "No passage outside the asking analyst's entitlement reaches the drafter or the rendered answer (EV6, EV8).",
    "Instruction-shaped text inside a report is neutralised and flagged, and changes no answer (EV5).",
    "A claim drawn from a superseded edition is marked with the superseding report (EV3).",
    "The service holds a read-only credential. No code path writes to any system of record, and the write scope is not configured, not merely unused."
  ],
  "buildInstructions": "Build the four stages as separate deployable units behind one service: entitlement-filtered retrieval (C2) with its access re-check (C3), the instruction guard (C8) and sufficiency gate (C6), the drafter (C4), and the citation check (C5) with the renderer (C7). Load one milestone file at a time. Treat every H assumption as a blocker until the owner confirms it; H1, H2 and H5 block launch. Do not add a write path, a cache that outlives a session, or a feedback loop that stores the analyst's question against their name, none of which this design authorises."
}
```


Sources:

- context / user-brief: It must never take any action


Full exact data and source evidence: [design.json](../design.json). Launch facts and owners: [assumptions.md](assumptions.md).
