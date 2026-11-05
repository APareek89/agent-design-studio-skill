# Product decisions for v1.3

Every decision the v1.3 brief left to me, with the reason. Written as the work
went, so the order is the order of the fixes.

## Where the work landed

**Committed to `main`, not to an unmerged `v1.3` branch.** The v1.3 brief asks
for a `v1.3` branch handed back unmerged; the person running the work asked for
the result on `main`. Their instruction wins, so `main` carries it.

## Fix 1, brief classifier

**Short function words are dropped from language detection.** Scoring the raw
stop-word lists made a 25-word English brief read as Portuguese ("a") or
Italian ("per"). Only words of three letters or more that exactly one language
claims are scored, and a Latin-script brief with fewer than two such words is
called English with low confidence rather than "undetermined": English is the
safe default for a keyword gap check, and the host is told to correct it.

**A non-Latin brief is never called English.** Arabic and Cyrillic are written
by several languages, so each names its most common one (Arabic, Russian) and a
sibling's function word overrides it. Falling through to the Latin stop-word
path would have called an Arabic brief English.

**A write verb whose object is a deliverable is not a write.** "Write a Python
script", "create a weekly report" change no system of record. Without this the
not-an-agent brief was also classified as a writing system, which would have
switched off the read-only profile for a brief that needs it.

**An empty brief is not an agent system.** With no words there is no decision
step to find, and the "empty" message already tells the host to ask for a
brief, so no second message is raised.

**The shape signals are marked unreliable for a non-English brief, not
suppressed.** The write, real-time and multi-tenant checks are English
keywords. Reporting them with `shapeSignalsReliable: false` and saying so in
the language message is more useful than reporting nothing, and the host
re-runs them on its translation.

**A brief conflict is a validator error once it is recorded.** When
`intake.briefProfile.briefConflicts` is non-empty, the Context card "Trigger
and first-release scope" and the Decision brief must both say what the brief
asked, what the design keeps and that an override needs a named owner. A
silent redesign is the failure this fix exists to prevent, so it fails
validation rather than warning. Designs with no `briefProfile` are unaffected.

## Fix 2, PDF fonts

**Noto Sans, Noto Sans Mono, Noto Sans Devanagari and Noto Sans Arabic ship;
CJK does not.** The first four are 2.6 MB together. Noto Sans CJK is about
16 MB, which is more than this repository should carry for a script no example
uses. A CJK glyph therefore takes the documented path: it renders as `?` and
adds one warning line naming the code points and the font to drop into
`fonts/`. Dropping `NotoSansCJK-Regular.ttf` into that folder switches it on
with no code change.

**Arabic renders but is neither shaped nor re-ordered.** ReportLab has no
OpenType shaping engine, so Arabic letters draw in isolated forms, and it
reverses a right-to-left run so the text layer holds the word in visual order.
Every character survives and nothing is a box, which is the fix; joined Arabic
would need a shaping dependency the skill does not have. Recorded in the
CHANGELOG under what it still cannot do.

**The font warning is merged into `validation.json` beside the PDF, replacing
any earlier font line.** Re-rendering into the same folder would otherwise
stack a duplicate warning per run.

## Fix 3, derived reader layer

**Design calls come only from `architecture`, `orchestration` and `permission`
framework cards, even when that yields two.** The telecom example has one
architecture card and one permission card, so its derived page shows two design
calls. Topping the list up from `data` and `fit` cards would put stack
descriptions on page one labelled as decisions, which is the mislabelling this
fix exists to remove. Two real calls beat five padded ones.

**Autonomy rows are action classes, from the workflow graph.** Every declared
`semantics.writeActions` class is its own row; the remaining nodes collapse by
`kind` into "checks in code", "decisions that wait for a person", "drafting and
classification", "notices to the requester" and "closing the case". The reader
is asking what the system does, not which of eighteen components does it.

**A KPI with no target number says "see definition".** The first attempt
matched any number near a preposition and pulled "7" out of the formula
"reopened within 7d / complaints receiving a decision". A number only counts as
a target when a target word introduces it, a bound word introduces it with a
unit, or it is a bare percentage, and never from the definition after "=".

**The Decision brief is headed "Decision brief".** It was headed with the
design title, which the top bar already carries, so the title appeared twice.

## Stress harness expectations

**Variant `06_zero_models_all_code` is expected to be rejected.** The v1.3
brief lists an expected outcome for fourteen of the fifteen mutations and omits
06. Emptying the model stage leaves components that declare a model with
nothing to bind to, and the validator says so, which is correct behaviour; it
is recorded as "rejected with the current message" rather than left undefined.

## Fix 4, long briefs

**Generated documents quote the brief; they never copy it.** `BRIEF_QUOTE_BYTES`
is 2,000 and the same rule applies in `build/00-overview.md`, the HTML Brief
panel and the Context section of the PDF. Below that length nothing changes.

**The size error names the field, not a remedy that cannot work.** It used to
say "split milestones" for an overview that was large because the brief was
60 KB. It now reports each oversize file with its byte count and the part of
the design that dominates it, and reports a total overrun separately.

**Nothing is hidden to fit a limit.** The HTML collapses a long brief behind a
"Show full brief" control with the whole text still in the page, and the full
PDF carries it as appendix D. Only the build overview points elsewhere, and it
says where.

## Fix 5, flow layout

**Edges are orthogonal with one gutter per source.** An edge leaves its source
sideways into a lane reserved for that source in the gap after its column,
travels vertically there, and enters the target from the left. Several columns
apart, it crosses in a corridor between node rows and drops into a lane
reserved for the target, so a long edge passes between rows rather than
through a node.

**Plates are placed at the target end and then moved until they are clear.**
Each plate starts on the final vertical segment near the target and slides up
and down that line in half-plate steps until it touches no other plate and no
node box, counting a node's tag lines as part of it. If nowhere is clear the
plate stays on its edge rather than being dropped: a lost condition is worse
than a crowded one. Measured over both seeds and six stress variants, there
are now no plate-plate and no plate-node overlaps, including the two the v1.2
changelog recorded in the health-claims flow.

**Over six exits from one node become a numbered legend.** The plate carries
the number, the numbered conditions print under the node, and the node detail
table keeps every condition in full. Six is the point where plates in one
gutter stop being readable at 1440 px.

**A cross-band edge says "continues at" at both ends.** It used to say
"continues at W17" at one end and "from W16" at the other, which read as two
different things.

## Fixes 6 to 8, brief profiles

**A design with no `briefProfile` keeps the v1.2 rules exactly.** Every profile
rule is switched on by a recorded profile, so the two seed examples and every
earlier design validate unchanged. This is checked by a test.

**Read-only risk families replace the write families; they do not join them.**
A system that answers and never acts cannot post a duplicate payment. Padding
the register with families that cannot occur is how a register stops being
read. COV17 names the read-only families a register is missing; money and
duplicate-write families become "n/a" with the reason.

**`answer` is an action class, checked by SEM008.** A read-only design has no
write node for SEM003 to check, so its pair of goldens is a cited answer and a
refusal when the corpus is silent, each naming a component whose declared
effect is `read`, each with an integer `expected.citations`, and each naming
the `citationField` it asserts on.

**Barge-in is an error, not a warning.** Where the design says the system
speaks, leaving out what happens when the user talks over it is a hole in the
design rather than a missing nicety, so the validator fails it. The latency
budget is a warning, because a budget can be exceeded for stated reasons.

**The latency check needs a node budget to work.** With a target in the brief
and no `latencyBudgetMs` anywhere, the validator says the path cannot be
checked rather than passing silently.

**SEM009 looks at inputs, not at prose.** A component whose declared inputs
name a record ID and no tenant is flagged; adding `tenantId` to its inputs
satisfies it. An identity binding must carry a tenant, and that tenant must be
`trusted`: a tenant the model supplied is the whole of the risk.

**The key attributes grid orders on the attribute's own name.** Ordering on the
source system too put a row first because its source string happened to
mention a tenant field.

## Fix 9, host degradation

**`runConditions` is one sentence with a clause per capability**, in the
wording the brief gives, and it is written by the run report, read from
`run-report.json` beside the design, and shown on the HTML status bar of every
view and on page 1 of the PDF. A design with no run report shows no line
rather than guessing.

**"Independent" is a validation error in a self-review.** The `method` field
is an enum so it cannot claim both, but the limitations and issues are free
text and were where the claim actually appeared. Setting the telecom review to
`self-review` now fails until its limitations are rewritten, which is the
point.
