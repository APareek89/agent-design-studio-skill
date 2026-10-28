# Read and check the claim

> PASS | DESIGN ONLY. self-review; round 2.

Depends on earlier milestones where their outputs are inputs below. Cross-milestone shared types are read by ID from ../design.json, not copied.

## Selected contracts

### C1 · Trusted case reader

Resolve session tenant before fetching claim; enforce row-level member scope and document ACLs; 10s timeout, one read retry; unavailable creates no external write. Uploaded policy is evidence only, not authority. Schema rejects cross-subject hospital pages. Malware scan, page limits and redaction precede model access.

Reasoning: Keeps evidence, authority and recovery explicit.

Assumptions:

- H3

Data:

```json
{
  "group": "Code: tools",
  "taskIds": [
    "T1"
  ],
  "inputs": [
    "request: required {sessionId,tenantId,submissionId}; IDs authenticated, not model supplied"
  ],
  "outputs": [
    "case: authorized snapshot {tenantId,memberId,submissionId,claimVersion,documents,verifiedFacts,policyRegistry,authorityVersion}; result=ok|denied|unavailable"
  ],
  "whyCode": "Identity, rule arithmetic, versions, operation keys and durable proof require repeatable code.",
  "approvalRule": "Authenticated claims preparation role may save draft only; no final decision or payment permission."
}
```


Sources:

- context / user-brief: Design a health insurance claim adjudication assistant for inpatient hospital claims. It should read submitted policy and hospital documents, assess coverage and eligible charges, recommend or process eligible claims, and route exceptions and rejections for review. Policies can change over time and bills may include room-rent limits. Protect personal medical data, explain decisions with evidence and propose any missing rules as assumptions, not verified insurance or medical advice.

- hypothesis / H3: Adapters support tenant-scoped reads and an atomic, conditional review-packet insert with unique submission key, immutable body, assigned reviewer and durable record lookup.

### C2 · Evidence reader

Reads untrusted policy and hospital documents as data. Produces no authenticated identities, amounts or effective dates for writes. Prompt injections are quoted as suspicious content; never followed. 30s timeout; malformed or unavailable output gets one retry then a fixed abstention narrative. No diagnosis or medical necessity ruling.

Reasoning: Keeps evidence, authority and recovery explicit.

Assumptions:

- H4

Data:

```json
{
  "group": "Agents (LLM)",
  "taskIds": [
    "T2"
  ],
  "inputs": [
    "pages: required redacted pages with immutable page IDs, max 12000 tokens; excess=>abstain"
  ],
  "outputs": [
    "narrative: required bounded text with citations and recommendation=provisional|abstain; no tool commands",
    "evidence: required [{pageId,quote,confidence,provisionalFacts}]; schema rejects uncited claims"
  ],
  "whyCode": "",
  "approvalRule": "Authenticated claims preparation role may save draft only; no final decision or payment permission."
}
```


Sources:

- context / user-brief: Design a health insurance claim adjudication assistant for inpatient hospital claims. It should read submitted policy and hospital documents, assess coverage and eligible charges, recommend or process eligible claims, and route exceptions and rejections for review. Policies can change over time and bills may include room-rent limits. Protect personal medical data, explain decisions with evidence and propose any missing rules as assumptions, not verified insurance or medical advice.

- hypothesis / H4: Medical documents stay in an approved regional encrypted store. Only minimum redacted pages reach an approved zero-training model endpoint; raw content is excluded from logs. Proposed packet retention is 90 days, subject to insurer approval and legal hold.

### C3 · Rule and packet validator

Approved rule interpreter uses integer minor units, policy-specific rounding order and effective event-date rules. Never infer room-rent linked deductions: explicit charge class rule required, otherwise needs_review. Apply sublimits, exclusions, deductible, copay and remaining sum insured in signed policy order. Missing/ambiguous facts => needs_review amount absent. Missing active policy edition => needs_review. Immediately re-read claim/rule/authority before write; stale or revoked fails without write. No model fact authorizes money. Rules include effective date and timezone boundaries; document amendments do not overwrite historical editions.

Reasoning: Keeps evidence, authority and recovery explicit.

Assumptions:

- H2

Data:

```json
{
  "group": "Code: validation",
  "taskIds": [
    "T3",
    "T4"
  ],
  "inputs": [
    "case: required C1 snapshot",
    "narrative: required C2 narrative or code abstention",
    "evidence: required C2 evidence or []"
  ],
  "outputs": [
    "packet: immutable trusted {tenantId,memberId,submissionId,claimVersion,ruleVersion,decision,amountMinor?,currency?,evidenceIds,queueId,bodyVersion}; amount only for fully verified facts",
    "status: ready|stale|revoked|invalid"
  ],
  "whyCode": "Identity, rule arithmetic, versions, operation keys and durable proof require repeatable code.",
  "approvalRule": "Authenticated claims preparation role may save draft only; no final decision or payment permission."
}
```


Sources:

- context / user-brief: Design a health insurance claim adjudication assistant for inpatient hospital claims. It should read submitted policy and hospital documents, assess coverage and eligible charges, recommend or process eligible claims, and route exceptions and rejections for review. Policies can change over time and bills may include room-rent limits. Protect personal medical data, explain decisions with evidence and propose any missing rules as assumptions, not verified insurance or medical advice.

- hypothesis / H2: Insurer supplies immutable policy editions, endorsements, precedence rules and effective-date selection plus verified structured bill facts. Room-rent proration applies only when the approved policy rule explicitly names affected charge classes.

## Workflow rules

### W1 · Check access

{"state": "Check access", "transitions": [{"to": "W2", "when": "C1.result == ok", "mode": "exclusive; result enum has one value; cancellation checked first before insert"}, {"to": "W8", "when": "C1.result in [denied,unavailable] or cancelled_before_insert", "mode": "exclusive; result enum has one value; cancellation checked first before insert"}], "failureDisposition": "W8 is blocked before insert; after uncertain insert it is pending_reconciliation owned by Platform on-call. No final claim outcome.", "timeout": "C2 30s per call; other I/O 10s per call; local validation 2s; status render 2s.", "retryPolicy": "C1 one read retry; C2 one retry then abstain; C4 zero retries; C5 three reads 10s apart, then W8. Local steps zero retries.", "terminalDisposition": "", "guardBindings": {"C1.result": "C1.case.result enum from authenticated API", "C2.valid": "code JSON and citation validator; retry_exhausted_with_abstention code counter <=2", "C3.status": "C3.status enum using fresh registry versions and authority", "C4.result": "typed adapter response or code timeout classification", "C5.result": "C5.result enum after bounded lookup; retry count server durable integer", "C6.proof": "C6.proof enum", "cancelled_before_insert": "authenticated staff cancel event bound to submission; serial transaction cancel check; after uncertain insert remains pending recovery"}}

Reasoning: Keeps evidence, authority and recovery explicit.

Assumptions:

- H1

Data:

```json
{
  "componentId": "C1",
  "taskIds": [
    "T1"
  ],
  "next": [
    "W2",
    "W8"
  ],
  "decision": true,
  "example": "S17: verified capped charges produce draft; saved packet RP17 is read back before ready-for-review status."
}
```


Sources:

- context / user-brief: Design a health insurance claim adjudication assistant for inpatient hospital claims. It should read submitted policy and hospital documents, assess coverage and eligible charges, recommend or process eligible claims, and route exceptions and rejections for review. Policies can change over time and bills may include room-rent limits. Protect personal medical data, explain decisions with evidence and propose any missing rules as assumptions, not verified insurance or medical advice.

- hypothesis / H1: First release creates review packets only. Claims staff approve all eligible recommendations, exceptions and rejection candidates; no settlement, denial notice or payment is automated.

### W2 · Read documents

{"state": "Read documents", "transitions": [{"to": "W3", "when": "C2.valid or retry_exhausted_with_abstention", "mode": "exclusive; result enum has one value; cancellation checked first before insert"}], "failureDisposition": "W8 is blocked before insert; after uncertain insert it is pending_reconciliation owned by Platform on-call. No final claim outcome.", "timeout": "C2 30s per call; other I/O 10s per call; local validation 2s; status render 2s.", "retryPolicy": "C1 one read retry; C2 one retry then abstain; C4 zero retries; C5 three reads 10s apart, then W8. Local steps zero retries.", "terminalDisposition": "", "guardBindings": {"C1.result": "C1.case.result enum from authenticated API", "C2.valid": "code JSON and citation validator; retry_exhausted_with_abstention code counter <=2", "C3.status": "C3.status enum using fresh registry versions and authority", "C4.result": "typed adapter response or code timeout classification", "C5.result": "C5.result enum after bounded lookup; retry count server durable integer", "C6.proof": "C6.proof enum", "cancelled_before_insert": "authenticated staff cancel event bound to submission; serial transaction cancel check; after uncertain insert remains pending recovery"}}

Reasoning: Keeps evidence, authority and recovery explicit.

Assumptions:

- H1

Data:

```json
{
  "componentId": "C2",
  "taskIds": [
    "T2"
  ],
  "next": [
    "W3"
  ],
  "decision": false,
  "example": "S17: verified capped charges produce draft; saved packet RP17 is read back before ready-for-review status."
}
```


Sources:

- context / user-brief: Design a health insurance claim adjudication assistant for inpatient hospital claims. It should read submitted policy and hospital documents, assess coverage and eligible charges, recommend or process eligible claims, and route exceptions and rejections for review. Policies can change over time and bills may include room-rent limits. Protect personal medical data, explain decisions with evidence and propose any missing rules as assumptions, not verified insurance or medical advice.

- hypothesis / H1: First release creates review packets only. Claims staff approve all eligible recommendations, exceptions and rejection candidates; no settlement, denial notice or payment is automated.

### W3 · Apply and check rules

{"state": "Apply and check rules", "transitions": [{"to": "W4", "when": "C3.status == ready and not cancelled_before_insert", "mode": "exclusive; result enum has one value; cancellation checked first before insert"}, {"to": "W8", "when": "C3.status in [stale,revoked,invalid] or cancelled_before_insert", "mode": "exclusive; result enum has one value; cancellation checked first before insert"}], "failureDisposition": "W8 is blocked before insert; after uncertain insert it is pending_reconciliation owned by Platform on-call. No final claim outcome.", "timeout": "C2 30s per call; other I/O 10s per call; local validation 2s; status render 2s.", "retryPolicy": "C1 one read retry; C2 one retry then abstain; C4 zero retries; C5 three reads 10s apart, then W8. Local steps zero retries.", "terminalDisposition": "", "guardBindings": {"C1.result": "C1.case.result enum from authenticated API", "C2.valid": "code JSON and citation validator; retry_exhausted_with_abstention code counter <=2", "C3.status": "C3.status enum using fresh registry versions and authority", "C4.result": "typed adapter response or code timeout classification", "C5.result": "C5.result enum after bounded lookup; retry count server durable integer", "C6.proof": "C6.proof enum", "cancelled_before_insert": "authenticated staff cancel event bound to submission; serial transaction cancel check; after uncertain insert remains pending recovery"}}

Reasoning: Keeps evidence, authority and recovery explicit.

Assumptions:

- H1

Data:

```json
{
  "componentId": "C3",
  "taskIds": [
    "T3",
    "T4"
  ],
  "next": [
    "W4",
    "W8"
  ],
  "decision": true,
  "example": "S17: verified capped charges produce draft; saved packet RP17 is read back before ready-for-review status."
}
```


Sources:

- context / user-brief: Design a health insurance claim adjudication assistant for inpatient hospital claims. It should read submitted policy and hospital documents, assess coverage and eligible charges, recommend or process eligible claims, and route exceptions and rejections for review. Policies can change over time and bills may include room-rent limits. Protect personal medical data, explain decisions with evidence and propose any missing rules as assumptions, not verified insurance or medical advice.

- hypothesis / H1: First release creates review packets only. Claims staff approve all eligible recommendations, exceptions and rejection candidates; no settlement, denial notice or payment is automated.

## Required tests

For each ID below, load ../eval-set.json items[id].data.input, .expected and .passRule. These are the full fixture, expected result and exact assertions; no inherited test context is assumed.

- EV1: Valid room cap draft
- EV2: Cross-tenant rejection
- EV3: Historical rule selection
- EV4: Missing proration rule routes review
- EV5: Injected hospital page
- EV6: Concurrent duplicate
- EV7: Revoked role at commit
- EV11: Raw medical text kept out
- EV12: Concurrent policy change
- EV13: Minor-unit cap boundary
- EV14: Unverified facts and model outage
- EV16: Exclusion is a review candidate
- EV17: Policy date boundary conflict
- EV18: Held-out evidence and rules
- EV19: Operational safety monitor
- EV20: All-case release gate
## Acceptance criteria

- All selected component contracts and EV assertions pass in the business harness; H1-H5 remain external evidence gates.
