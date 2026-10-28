# Read and check the claim

> PASS | DESIGN ONLY. self-review; round 3.

Depends on earlier milestones where their outputs are inputs below. Cross-milestone shared types are read by ID from ../design.json, not copied.

## Selected contracts

### C1 · Trusted case reader

Resolve session tenant before fetching claim; enforce row-level member scope and document ACLs; 10s timeout, one read retry; unavailable creates no external write. Uploaded policy is evidence only, not authority. Schema rejects cross-subject hospital pages. Malware scan, page limits and redaction precede model access. Extract only visible rendered-page pixels through sandboxed OCR; discard PDF hidden/invisible text, off-page text, scripts, attachments, comments and nonvisible form layers. Preserve visibly rendered form content as page evidence. Create immutable document/page IDs plus content hash for normalized visible text (Unicode NFC; CRLF to LF only). Never concatenate raw PDF text layers into prompts. Model sees visible text only, with page IDs. Visible document instructions remain untrusted data. OCR ambiguity or an OCR/source discrepancy sets a review flag; staff verifies facts before calculation. textHash is SHA-256 of normalized visibleText encoded in UTF-8, computed by trusted store.

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
    "case: authorized snapshot {tenantId,memberId,submissionId,claimVersion,documents,verifiedFacts,policyRegistry,authorityVersion}; result=ok|denied|unavailable; documents include authorized immutable {documentId,pageId,visibleText,textHash,clauseSpans:[{clauseId,start,end,ruleVersion,applicable}]} from approved registry and visible hospital pages"
  ],
  "whyCode": "Identity, rule arithmetic, versions, operation keys and durable proof require repeatable code.",
  "approvalRule": "Authenticated claims preparation role may save draft only; no final decision or payment permission."
}
```


Sources:

- context / user-brief: Design a health insurance claim adjudication assistant for inpatient hospital claims. It should read submitted policy and hospital documents, assess coverage and eligible charges, recommend or process eligible claims, and route exceptions and rejections for review. Policies can change over time and bills may include room-rent limits. Protect personal medical data, explain decisions with evidence and propose any missing rules as assumptions, not verified insurance or medical advice.

- hypothesis / H3: Adapters support tenant-scoped reads and an atomic, conditional review-packet insert with unique submission key, immutable body, assigned reviewer and durable record lookup.

### C2 · Evidence reader

Reads untrusted policy and hospital documents as data. Produces no authenticated identities, amounts or effective dates for writes. Prompt injections are quoted as suspicious content; never followed. 30s timeout; malformed or unavailable output gets one retry then a fixed abstention narrative. No diagnosis or medical necessity ruling. Citation format includes document/page IDs, exact start/end offsets and verbatim quote; policy citations require approved clause ID. C3 independently verifies every citation before any packet can be saved. A model-provided page hash or clause label is never trusted.

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
    "evidence: required [{documentId,pageId,clauseId?,start,end,quote,provisionalFacts}]; Unicode code-point offsets into normalized visibleText; no quote normalization or fuzzy matching"
  ],
  "whyCode": "",
  "approvalRule": "Authenticated claims preparation role may save draft only; no final decision or payment permission."
}
```


Sources:

- context / user-brief: Design a health insurance claim adjudication assistant for inpatient hospital claims. It should read submitted policy and hospital documents, assess coverage and eligible charges, recommend or process eligible claims, and route exceptions and rejections for review. Policies can change over time and bills may include room-rent limits. Protect personal medical data, explain decisions with evidence and propose any missing rules as assumptions, not verified insurance or medical advice.

- hypothesis / H4: Medical documents stay in an approved regional encrypted store. Only minimum redacted pages reach an approved zero-training model endpoint; raw content is excluded from logs. Proposed packet retention is 90 days, subject to insurer approval and legal hold.

### C3 · Rule and packet validator

Approved rule interpreter uses integer minor units, policy-specific rounding order and effective event-date rules. Never infer room-rent linked deductions: explicit charge class rule required, otherwise needs_review. Apply sublimits, exclusions, deductible, copay and remaining sum insured in signed policy order. Missing/ambiguous facts => needs_review amount absent. Missing active policy edition => needs_review. Immediately re-read claim/rule/authority before write; stale or revoked fails without write. No model fact authorizes money. Rules include effective date and timezone boundaries; document amendments do not overwrite historical editions. Citation guard runs first on all C2 evidence: resolve document/page only in C1 authorized immutable corpus; require source hash from store, 0<=start<end<=len(visibleText), and exact Unicode-code-point slice equal to quote. Policy clauses must exist in the selected registry edition, be applicable to this event, and contain the full cited span. Every narrative claim must reference at least one verified evidence ID; render only a template from claim/evidence pairs, not unchecked free prose. Nonexistent page, mismatched quote, wrong/inapplicable clause or unbound narrative claim => status invalid, precise reason, no packet write, Claims lead owns blocked resubmission. Fixed code abstention uses no citations. These checks establish source correspondence, not that a medical assertion is true. For proposed PR1 only: verified roomDailyMinor>0, roomDays a policy-approved positive integer, cap>=0; room eligible=min(actualDaily,cap)*days. For each preeligible linked charge line with class in prorateClasses, lineEligible=floor(lineMinor*min(actualDaily,cap)/actualDaily). Unlisted/explicitly excluded linked classes retain full preeligible amount. Apply exactly once per line; do not prorate room line itself, nonpayable lines or the aggregate again. Sum room+eligible linked/unlinked lines; subtract deductible with floor at zero, apply floor(sum*(10000-copayBps)/10000), then remaining-sum-insured cap. Missing/unknown proration mode, duplicate class mapping, actualDaily=0, currency mismatch, invalid days or missing approved class membership => needs_review with no amount. A nonempty class list without approved formulaId PR1 and linked classes is insufficient. PR1 is hypothetical; H2 must verify the real insurer rule.

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
    "case: required C1 snapshot; authorized immutable visible corpus and approved clause ranges required for all cited evidence",
    "narrative: required C2 narrative or code abstention",
    "evidence: required C2 evidence or []"
  ],
  "outputs": [
    "packet: immutable trusted {tenantId,memberId,submissionId,claimVersion,ruleVersion,decision,amountMinor?,currency?,evidenceIds,queueId,bodyVersion}; amount only for fully verified facts",
    "status: ready|stale|revoked|invalid; invalid citation reasons SOURCE_NOT_FOUND|QUOTE_MISMATCH|CLAUSE_NOT_APPLICABLE|NARRATIVE_UNBOUND"
  ],
  "whyCode": "Identity, rule arithmetic, versions, operation keys and durable proof require repeatable code.",
  "approvalRule": "Authenticated claims preparation role may save draft only; no final decision or payment permission."
}
```


Sources:

- context / user-brief: Design a health insurance claim adjudication assistant for inpatient hospital claims. It should read submitted policy and hospital documents, assess coverage and eligible charges, recommend or process eligible claims, and route exceptions and rejections for review. Policies can change over time and bills may include room-rent limits. Protect personal medical data, explain decisions with evidence and propose any missing rules as assumptions, not verified insurance or medical advice.

- hypothesis / H2: Insurer supplies immutable policy editions, endorsements, precedence rules and effective-date selection plus verified structured bill facts. Room-rent proration applies only when the approved policy rule explicitly names affected charge classes. Proposed test-only rule PR1: linked eligible classes use capped daily room amount divided by actual daily room amount, applied once per eligible line with floor rounding; excluded classes stay unchanged. The insurer must approve or replace PR1 before any real linked deduction.

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

{"state": "Read documents", "transitions": [{"to": "W3", "when": "C2.valid or retry_exhausted_with_abstention", "mode": "exclusive; result enum has one value; cancellation checked first before insert"}], "failureDisposition": "W8 is blocked before insert; after uncertain insert it is pending_reconciliation owned by Platform on-call. No final claim outcome.", "timeout": "C2 30s per call; other I/O 10s per call; local validation 2s; status render 2s.", "retryPolicy": "C1 one read retry; C2 one retry then abstain; C4 zero retries; C5 three reads 10s apart, then W8. Local steps zero retries.", "terminalDisposition": "", "guardBindings": {"C1.result": "C1.case.result enum from authenticated API", "C2.valid": "code JSON/schema validator only; C3 checks page/quote/applicable clause before save; retry_exhausted_with_abstention code counter <=2", "C3.status": "C3.status enum using fresh registry versions and authority", "C4.result": "typed adapter response or code timeout classification", "C5.result": "C5.result enum after bounded lookup; retry count server durable integer", "C6.proof": "C6.proof enum", "cancelled_before_insert": "authenticated staff cancel event bound to submission; serial transaction cancel check; after uncertain insert remains pending recovery"}}

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
- EV21: Approved linked room proration
- EV22: Nonempty class list lacks formula
- EV23: Linked class per-line rounding
- EV24: Invented source page is blocked
- EV25: Wrong policy clause is blocked
- EV26: Forged quote is blocked
- EV27: Hidden layer never enters evidence reader
- EV28: Proposed amount cannot bypass linked code result
## Acceptance criteria

- All selected component contracts and EV assertions pass in the business harness; H1-H5 remain external evidence gates.
