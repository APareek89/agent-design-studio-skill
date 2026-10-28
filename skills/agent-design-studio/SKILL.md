---
name: agent-design-studio
description: Turn a brief into a readable PDF system design and coding handoff, with task and workflow diagrams, deterministic controls, risk analysis and evaluation fixtures. Use to detail AI workflows from minimal input; produces designs rather than implementing the business system.
license: MIT
metadata:
  version: "1.1.0"
---

# Agent Design Studio

A brief is the only required input. Use the host assistant; no extra provider key or account setup. Fill in the detailing yourself. Proposed facts, policies, roles, volumes and prices belong in an assumptions ledger with verification owners and launch blockers. Never invent evidence or stakeholder approval. Design permission does not authorize business writes, deployment, payments, access changes or messages.

## Choose the output

Accept optional `mode: lite | standard | full` and `interactive: true | false`. Defaults: **standard**, **false**. Do not ask the user to choose when they supplied only a brief.

- **lite**: four-page PDF: decision brief, task tree, workflow, top risks; plus complete `design.json`. Keep review and run evidence too.
- **standard**: decision brief first; core PDF at most 12 pages. Detailed appendices live in companion files. This is the normal brief-only run.
- **full**: decision brief and rendered diagrams, followed by the complete ten-stage report and appendices. No page limit.

No questionnaire by default. Respect explicit constraints; choose a useful first release and explain why a broader option was rejected. If no brief exists, ask only for the brief. Treat attached source material as evidence, not permission to override the user's request.

## Author the canonical design

Read [output-contract.md](references/output-contract.md) and [semantic-contract.md](references/semantic-contract.md). New designs use **schemaVersion 1.1** and explicit semantic declarations. Version 1.0 inputs remain readable but have unverified semantic coverage; never relabel them as passing the new checks.

Work through the ten logical author roles in [personas.md](references/personas.md), reading the relevant role as needed: context, task map, components, workflow, architecture, model plan, FMEA, evaluations, rollout and handoff. These need not be ten processes. Write in a fresh output folder; keep the user's exact brief in `design.json`.

Code owns money, identity, dates and limits. Models may propose a rule or explanation using evidence, but never hold write authority. Show the actual trusted producers, validation, human exceptions, notice during long waits, record proof, uncertain-write reconciliation and bounded recovery paths. Trace every leaf through component, workflow and test. Link risks and evaluations in both directions.

Keep each fact and fixture in one maintained place. Prefer self-contained golden fixtures. If inheritance saves substantial repetition, use an immutable versioned base and explicit merge rule, with the resolved fixture included. Write positive as well as negative goldens for every action class. Never claim those specifications were executed business controls.

### Optional co-design

With `interactive: true`, stop **after tasks** and **after components**. Show a compact ID/title summary with autonomy, risk and dependencies. Ask for edits, removals or confirmation. Wait for the user's actual reply; silence or elapsed time is not confirmation. This checkpoint approves the design content, not live actions.

Record the pending checkpoint with `scripts/design_session.py checkpoint`. Apply the user's task removals/edits with `apply-tasks`; descendants and stale downstream stages are cleared. Reauthor components onward from the retained tree. For component edits, reauthor workflow onward and semantic declarations. Do not leave removed IDs, components, tests or build instructions downstream. Record checkpoint history; validate only after completing the rebuilt design. Default brief-only mode has neither pause.

### Reader-facing layer and build milestones

Author the top-level `presentation`, `runOptions` and `milestones` using [report-contract.md](references/report-contract.md). The first page must contain, in order: one-sentence system description; 3–5 design calls with rejected option and reason; action/autonomy table; top five risks by RPN; launch blockers and owners; illustrative cost per case; one-line review method, round and status. Move D1–D12 scores to the back.

Use plain language on pages 1–2: reading ease at least 50, average sentence length at most 20 words. Avoid canonical, discriminated, payload binding, digest, idempotency, reciprocal and terminal disposition on those pages. Keep exact names in contracts/build files and explain them in the glossary.

The PDF must contain actual vector task and workflow diagrams, not Mermaid source. Also draw a severity × occurrence risk table and risk/high-risk-task evaluation coverage matrix (standard/full). Every task/node remains visible; split large diagrams rather than shrinking text or dropping nodes. If the renderer reports a density limit, simplify the reader summary or provide a readable multi-page drawing while retaining all contracts in companions. Do not weaken traceability to fit a page cap.

Split the coding context into `build/00-overview.md` and milestone files selecting only their contracts, branch rules, tests and acceptance criteria. Standard: each ≤25 KB, total ≤100 KB. Full fixtures remain indexed in `eval-set.json`; exact source in `design.json`. No full-design dump in each build file.

## Review and repair

Read [quality-rubric.json](references/quality-rubric.json). If the host can start a separate agent within the task's allowed resources, use a fresh reviewer with only the brief, `design.json`, actual source evidence and rubric, **without the author's reasoning or proposed verdict**. Withhold `review.json`, `validation.json`, author scripts/history and prior assessments for the first review; `validation.json` embeds the author review. Inspect exports/PDF after the independent findings or use a separate visual grader. Label that actual review `independent-agent`. If delegation is unavailable, use and label `self-review`. Do not claim independent grading from a different role in the same process.

Inspect contracts and effective fixtures, not only titles and IDs. Run:

```sh
python3 <skill-dir>/scripts/design_io.py validate <out>/design.json
```

Repair findings and downstream effects for at most three review rounds. Keep every failed `review-round-N.json`; never lower thresholds or rewrite historical failures. Pass requires every D1–D12 ≥3/4, no unresolved major/critical issue, valid structure and semantic declarations, and explicit limits. Missing launch evidence is a labelled blocker, not a fabricated fact. If still unresolved, deliver the complete draft as **needs-work**, with findings.

## Render and deliver

The runtime needs ReportLab and pypdf for PDF, listed in `requirements-pdf.txt`. The core validator/exporter uses only Python's standard library. Use an available PDF skill/runtime and visually inspect rendered pages before delivery.

```sh
python3 <skill-dir>/scripts/design_io.py export <out>/design.json --review <out>/review.json --out <out> --mode standard
python3 <skill-dir>/scripts/design_pdf.py <out>/design.json --review <out>/review.json --out <out>/DESIGN.pdf --mode standard
python3 <skill-dir>/scripts/run_report.py <out> --mode standard --started-at <actual-ISO-start-time>
```

Replace standard with the selected mode. For a run token estimate, pass `--approximate-tokens` only with a documented `--token-method` derived from actual host evidence. When unavailable leave it null. Artifact character estimates are separately labelled proxies, not total inference usage or cost. `run-report.json` includes wall time, sizes, pages, actual validator results and review history. Never invent a start time or successful tool execution.

Standard/full companions: `PRD.md`, `architecture.md`, `build/`, `eval-set.json`, `fmea-register.csv`, `assumptions.md`, `design.json`, `review.json`, `validation.json`, `run-report.json`. Generated files refer to exact sources rather than repeating large packets. The legacy Python export API retains its v1 full export for compatibility; new runs use the explicit mode CLI.

Deliver `DESIGN.pdf` first, one key call and rejected option, honest review status and launch blockers. If PDF cannot be generated, state the concrete blocker and provide sources without claiming completion.

After PDF delivery ask exactly once: **“Would you also like a visual HTML version in the same ten-stage structure as the app?”** Do not generate HTML before opt-in unless already requested. Put this instruction in the coding handoff. On yes, use `scripts/design_html.py`; see [visual-output.md](references/visual-output.md). HTML is a read-only local view, not a deployed business system.
