# Semantic contract (schema 1.1)

New designs set `schemaVersion` to `1.1` and include `semantics`. Version 1.0 remains readable with `semanticCoverage: unverified` and an explicit warning; a structural pass is not a semantic pass. Version 1.1 missing or incomplete declarations fails `SEM000`. A supplied semantic contract is checked even on a 1.0 artifact.

Active repository development fixtures are in `evals/seeded-defects/v2/`; the original parent-directory fixtures are immutable history. The original `passing-v1.1.json` is now known invalid under SEM003 and SEM007; the v2 manifest records its unchanged hash and the exact corrections and mutations used for the active cases. They are not required installed resources. Use the exact shape below when authoring. The helper checks declarations, graph paths and fixture consistency. It does not run a tool, execute a golden, infer effects from prose, verify external bases, or establish that declared provenance is truthful. Record-ID guards, approvals and validation are declared node roles, not certification of their implementation.

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

Every actual golden eval has one declaration. Write-action goldens use its action class; read-only goldens use `actionClass: ""`. `polarity` is `positive` or `negative`. Actual `eval.data.input` and `eval.data.expected` are JSON strings per the stage schema; parsing those strings must produce JSON objects. Self-contained `fixture` has exactly `input` and `expected`, both nonempty objects, identical to those actual eval values. A positive write golden includes integer `expected.writes >= 1`; a negative includes integer `expected.writes: 0`. Both require an explicit integer `passRule.equals.writes` identical to `expected.writes` (booleans and numeric strings are invalid), and `eval.data.componentIds` must include a writer component for that action class. The negative case may block before calling the writer; linking that writer identifies the forbidden effect being tested, not an invocation. Only cases meeting these requirements count toward the positive/negative write-action coverage pair. Supplemental maths-only or read-only cases use empty `actionClass` and never satisfy write coverage. These checks establish consistency of declared assertions; they do not execute fixtures or certify implementation.

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

## Record-ID guards

A guard node requires `recordProof` as one object, or a nonempty list of alternative source objects:

```json
{"id": "W6", "kind": "record_id_guard", "recordProof": [
  {"field": "recordId", "sourceComponentId": "C2", "sourceField": "recordId"},
  {"field": "recordId", "sourceComponentId": "C4", "sourceField": "recordId"}
]}
```

The guard's actual workflow component must be `Code: validation`. Its input must declare the exact `field` as required string, and every producer must declare the exact `sourceField` as required string. A direct projection such as `recordId:string! on COMMITTED; absent on TIMEOUT` is supported. Explicit dotted declarations such as `receipt.recordId:string!` are supported; fields are never inferred from an opaque object or prose envelope. A source component must be deterministic (`Code: tools` or `Code: validation`) and occur upstream as a semantic writer, reconciler, or an adapter with `componentEffects.effect: read`. Thus a previously existing authoritative case record can supply proof without a new write. An LLM cannot produce or validate the proof.

The actual guard workflow description must also bind its input to these sources. For a singleton, use `bindings.recordId: {"sourceComponentId":"C2","sourceField":"recordId"}`. For alternatives sharing a field, use an array in the same order as `recordProof`, e.g. `bindings.recordId: [{"sourceComponentId":"C2","sourceField":"recordId"},{"sourceComponentId":"C4","sourceField":"recordId"}]`. Distinct input fields each have their own binding. Every alternative must pass the provenance/type checks; one good source cannot excuse an invalid one.

The deterministic guard's contract must reject missing or empty proof and only allow a confirmed completion after checking a committed writer result, authoritative found result, or verified existing record. A timeout alone supplies no record proof. Graph validation proves completion cannot bypass the declared guard and checks source/field consistency; it does not execute the presence check or certify a producer's real truthfulness.

## Stable diagnostics

- `SEM000`: absent, incomplete, malformed, unsupported or conflicting metadata; exact stage coverage and graph annotation mismatches.
- `SEM001`: a reachable write has a path from a root without an upstream validation or approval. Removing all guards and checking remaining reachability catches bypasses, joins and cycles.
- `SEM002`: a human wait over one hour lacks an outgoing `notice` transition to a `requester_notice` node. A requester notice is a separate branch from waiting for a decision.
- `SEM003`: any write action class lacks a positive or negative writer-linked golden, or typed expected/asserted write counts disagree with each other or polarity.
- `SEM004`: golden fixture is not self-contained and consistent with the eval, or inheritance lacks a versioned base, supported merge rule and resolved fixture.
- `SEM005`: an LLM output supplies a money, date or identity binding to a write.
- `SEM006`: a writer's `TIMEOUT` or `unknown_commit` successor can reach a write before a reconciliation node. Checking all possible paths prevents a safe reconciliation branch from masking a direct retry.
- `SEM007`: a record-ID guard lacks consistent trusted input/output provenance and deterministic validation, or a completion is reachable without passing such a valid guard. The graph check covers every root/path, not merely the existence of a role label somewhere.

Store semantic diagnostic `ruleId` values alongside JSON paths. `semanticCoverage: verified-declarations` means these declared invariants passed; it does not certify a built or deployed system.
