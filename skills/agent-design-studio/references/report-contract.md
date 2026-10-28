# Reader layer, modes and milestone context

New v1.1 designs add these optional top-level objects to the exact canonical stage contract. The author supplies the summaries from the actual design; they cannot add authority or capability. Exact source facts stay in the ten stages. The reporter sanitizes internal words only in reader summaries, never in contracts.

```json
{
  "runOptions": {"mode":"standard", "interactive":false},
  "presentation": {
    "systemSentence":"Help staff resolve a complaint with proof and clear limits.",
    "designCalls":[
      {"choice":"Code sets the amount.","rejected":"Model maths","why":"Rules must be repeatable"},
      {"choice":"People decide exceptions.","rejected":"Free agent writes","why":"Staff keep control"},
      {"choice":"Check before retry.","rejected":"Blind second write","why":"Avoid double credits"}
    ],
    "autonomy":[
      {"action":"Find account records", "level":"acts alone"},
      {"action":"Explain the case", "level":"suggests"},
      {"action":"Approve exceptions", "level":"human decides"}
    ],
    "scopeSummary":"The first release handles service credits. Other disputes stay with staff.",
    "taskLabels":{"T0":"Resolve a complaint", "T1":"Check the account"},
    "workflowLabels":{"W1":"Check the account"}
  },
  "milestones":[
    {"id":"01", "title":"Validate the case", "taskIds":["T1"],
     "componentIds":["C1"], "evalIds":["EV1"],
     "acceptanceCriteria":["Reject a mismatched account before any private record is read."]}
  ]
}
```

Use 3–5 short calls (choice + rejected option + why, about 20 words combined), and action classes rather than one autonomy row per tiny component. Use a short plain sentence per thought. Limit page-one facts to what supports a two-minute decision; full risks and blockers remain in the linked ledger. The PDF shows all launch-blocker IDs and owners, not a silent subset. If there are many blockers, group them by owner in the first-page summary while preserving each ID and link to details.

`taskLabels` and `workflowLabels` can shorten diagram labels, never remove or rename stable IDs. Task diagrams include all task cards with mode and risk; workflow diagrams include all nodes and edges, coloured by component group, with decision diamonds. Wide graphs need dedicated drawing layout, not smaller unreadable type. Current renderer explicitly refuses diagrams beyond its readable layout limits; a host may extend it or render a suitable SVG before delivery. Document that limitation rather than calling an unrendered picture a pass.

Milestones cover every component and all tests linked to those components. Build files carry exact selected component and branch contracts and expected/assertion summaries, referring by ID to complete fixtures in `eval-set.json`. Shared cross-milestone types are read by ID. A >25 KB milestone or >100 KB total standard build fails export; split responsibilities and remove duplicate context, never drop a control. The full canonical design remains an explicit companion.

## Provenance of run measurements

Start the wall clock before authoring. `run-report.py` records actual elapsed seconds from an available start timestamp, pages, file sizes, schema/semantic validation and review round filenames. Supply actual host token counters or explicitly documented estimates when available. A text-character/4 artifact estimate does not include reasoning, retries, tool messages or loaded context; it must never satisfy a total-token savings claim.

The repository-only `scripts/score_run.py` evaluates S1–S12. Its judged items require a different grader and source hashes. Missing or unverified evidence is a failed/unmeasured target, never an automatic pass. Keep failed scorecards and source hashes across iterations.
