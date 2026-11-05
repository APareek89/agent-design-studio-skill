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
