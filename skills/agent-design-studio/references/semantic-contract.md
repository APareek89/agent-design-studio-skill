# Semantic contract (schema 1.1)

New designs set `schemaVersion` to `1.1` and include `semantics`. Version 1.0 remains readable with `semanticCoverage: unverified` and an explicit warning; a structural pass is not a semantic pass. Version 1.1 missing or incomplete declarations fails `SEM000`. A supplied semantic contract is checked even on a 1.0 artifact.

Use the complete passing example at `evals/seeded-defects/passing-v1.1.json` in the repository. The helper checks declarations, graph paths and fixture consistency. It does not run a tool, execute a golden, infer effects from prose, verify external bases, or establish that declared provenance is truthful. Record-ID guards, approvals and validation are declared node roles, not certification of their implementation.

## Exact metadata shape

All collections below are required, including empty arrays. Unknown fields fail. IDs refer to existing stage items.

```json
{
  "version": "1.1",
  "entrypoints": ["W1"],
  "nodes": [
    {"id": "W1", "kind": "validation"},
    {"id": "W2", "kind": "write", "actionClass": "refund", "bindings": [
      {"field": "customerId", "category": "identity", "source": "trusted"}
    ]}
  ],
  "transitions": [
    {"from": "W1", "to": "W2", "when": "valid", "outcome": "normal"}
  ],
  "componentEffects": [
    {"componentId": "C1", "effect": "none"},
    {"componentId": "C2", "effect": "write"}
  ],
  "modelOutputs": [
    {"componentId": "C1", "field": "explanation", "category": "other"}
  ],
  "writeActions": [{"actionClass": "refund", "nodeIds": ["W2"]}],
  "goldens": [{
    "evalId": "EV1", "actionClass": "refund", "polarity": "negative",
    "fixture": {"input": {"customerId": null}, "expected": {"writes": 0}}
  }]
}
```

This fragment illustrates keys; the full design example contains both golden polarities and every workflow node. `entrypoints` equals all actual roots. `nodes` covers every workflow item exactly once. Kinds are `start`, `validation`, `approval`, `write`, `human_wait`, `requester_notice`, `reconcile`, `record_id_guard`, `completion`, `other`. Human waits require numeric `waitHours`. Writers require a nonempty `actionClass` and `bindings`. Bindings cover every input field of the writer's component, without duplicates. Input/output field names are the portion before `:` in the component's typed field declarations.

`componentEffects` covers every component once; effects are `none`, `read`, `write`. Every workflow node using a write component must be `write`, and every write node must use a write component. `writeActions` covers all writers exactly once, grouped by action class. Use separate components when a tool wrapper mixes read and write responsibilities.

`modelOutputs` categorizes every output of every `Agents (LLM)` component, exactly once. Categories are `money`, `date`, `identity`, `other`. Every writer binding has `field`, `category`, `source` (`llm`, `trusted`, `literal`). A component-output source additionally names `sourceComponentId` and `sourceField`; `llm` sources must name an actual categorized model output. A source naming an LLM component is checked as LLM-origin even if labeled `trusted`; its category must agree with the output declaration. An undeclared intermediary cannot establish trusted provenance: model-derived values remain model-derived and must retain their LLM source declaration through transformations. Replacing an LLM-proposed amount or identity with a separately authenticated value is a new trusted binding, not sanitization of the proposal.

Every actual workflow description transition has one semantic annotation, matched by `from`, `to`, and exact `when`. This includes multiple predicates sharing one successor. Outcomes are `normal`, `TIMEOUT`, `unknown_commit`, `repeat`, `notice`. Actual `data.next` remains the graph used for reachability; a shadow semantic graph cannot hide a bypass. Declare uncertain writer outcomes explicitly when those outcomes can occur; an outcome omitted from the underlying contract cannot be discovered from prose by this checker.

## Golden fixtures

Every actual golden eval has one declaration. Write-action goldens use its action class; read-only goldens use `actionClass: ""`. `polarity` is `positive` or `negative`. Actual `eval.data.input` and `eval.data.expected` must be JSON objects. Self-contained `fixture` has exactly `input` and `expected`, both nonempty objects, identical to those actual eval values. A positive write golden includes integer `expected.writes >= 1`; a negative includes integer `expected.writes: 0`. This checks declared expected behavior; it does not execute the fixture or prove the pass-rule assertions are sufficient.

Alternatively replace `fixture` with:

```json
{
  "base": {"id": "refund-fixture", "version": "2.1"},
  "mergeRule": "deep-merge-v1",
  "overrides": {"input": {"customerId": "CUS2"}},
  "resolvedFixture": {"input": {"customerId": "CUS2"}, "expected": {"writes": 1}}
}
```

`deep-merge-v1` recursively merges objects; scalar/array values replace the base value; omitted keys retain base values; null is a literal value, not deletion. The base must be immutable at the supplied version. Include `resolvedFixture` matching actual eval input/expected so the artifact remains reviewable. The helper checks the version, merge-rule declaration and resolved consistency; it does not fetch or verify the external base or independently recompute its merge. Do not encode inheritance as prose or hidden references inside a supposedly self-contained fixture.

## Stable diagnostics

- `SEM000`: absent, incomplete, malformed, unsupported or conflicting metadata; exact stage coverage and graph annotation mismatches.
- `SEM001`: a reachable write has a path from a root without an upstream validation or approval. Removing all guards and checking remaining reachability catches bypasses, joins and cycles.
- `SEM002`: a human wait over one hour lacks an outgoing `notice` transition to a `requester_notice` node. A requester notice is a separate branch from waiting for a decision.
- `SEM003`: any write action class lacks a positive or negative actual golden, or expected write counts contradict polarity.
- `SEM004`: golden fixture is not self-contained and consistent with the eval, or inheritance lacks a versioned base, supported merge rule and resolved fixture.
- `SEM005`: an LLM output supplies a money, date or identity binding to a write.
- `SEM006`: a writer's `TIMEOUT` or `unknown_commit` successor can reach a write before a reconciliation node. Checking all possible paths prevents a safe reconciliation branch from masking a direct retry.
- `SEM007`: a completion node is reachable without passing a `record_id_guard`. The graph check covers every root/path, not merely the existence of a guard somewhere.

Store semantic diagnostic `ruleId` values alongside JSON paths. `semanticCoverage: verified-declarations` means these declared invariants passed; it does not certify a built or deployed system.
