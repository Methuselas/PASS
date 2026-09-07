# PASS — Software Card Field Tests

status: active
owner: docs/domains/software-engineering
last_reviewed: 2026-09-07

A software card field test asks a practical question: **does this card help a
model understand, reproduce, or improve a real engineering decision found in
human-written software?** It is not a Drill sitting and it is not a
treatment/control experiment.

The review subject is existing software. The card supplies the engineering
lens; the human code supplies a real design with real constraints; a small proof
of concept shows whether the model can turn what it learned into working code.

## Qualification is not ordinary use

This protocol has two distinct routes:

- **Maintainer qualification** asks whether a card functions as intended before
  its author trusts it as guidance for AI developers. This is the primary route
  described below. It deliberately inspects real human code, builds a proof of
  concept, and records evidence that may strengthen or repair the card.
- **Project application** uses already-published cards to help with a user's
  software. An ordinary user does not have to qualify the card, supply a neutral
  catalog, or complete this protocol before receiving help. If application
  exposes a defect, the result may be reported for later maintainer review.

Route from the user's goal. “Test or validate these cards” selects maintainer
qualification. “Help me review, fix, or build this project” selects ordinary
project application unless the user asks to evaluate the card itself.

## Declare why this source was selected

Before reading code, give the review subject one selection role:

- **Neutral external corpus.** Select a real project through an external catalog
  rather than because its implementation is already known to support a claim.
  A public ranking, ecosystem index, or previously frozen random selection may
  supply the candidates. The catalog is a selection frame, not the code under
  review and not a statistical control arm.
- **Project-relevant reference.** Select a project because its domain,
  architecture, or implementation may inform software the user actually wants
  to build or repair. Its practical relevance is a strength, but selection is
  not neutral.
- **Interest-led investigation.** Select a project to answer a personal
  feasibility or exploration question. Do not silently mix it into the neutral
  corpus.

These roles affect what may be claimed about selection; they do not make one
kind of code more or less capable of exposing a broken card. Record the role in
the review notes. Never infer a role from the repository's subject matter or
silently inherit another user's choices.

## Model-guided quick start

The user does not need a catalog, a manifest, or PASS terminology to begin. A
request such as “test this card against this repository” is enough.

- When the user supplies code and a practical goal, classify it as
  project-relevant and proceed. Do not ask them to complete setup paperwork.
- When the user supplies code but the selection reason would change the claim,
  ask one plain-language question: “Did you choose this because it helps your
  project, because you are personally interested in it, or from an outside list
  for a neutral check?” Record the answer yourself.
- When the user wants a neutral check but supplies no source, offer to choose a
  project for the relevant language. The user may paste a catalog URL or file,
  name a catalog they prefer, or ask the model to select a reasonable public
  catalog. For example, a model may offer
  [EvanLi/Github-Ranking](https://github.com/EvanLi/Github-Ranking); it must not
  assume that catalog without telling the user.
- When the user supplies neither code nor a selection goal, ask only whether to
  use code relevant to their project or choose a neutral public example. Let the
  answer determine the remaining setup.

A catalog does only one job: it defines the pool from which a neutral review
subject is chosen. Supplying one can be as simple as pasting a link. The model
records the catalog, date or revision when available, language, selection rule,
and chosen repository in the review note. The user should not have to author or
maintain metadata.

When several local sources have already been classified, the model may copy
[`../templates/SOFTWARE_FIELD_TEST_CONTEXT_TEMPLATE.md`](../templates/SOFTWARE_FIELD_TEST_CONTEXT_TEMPLATE.md)
into the user's ignored workspace and fill it in there. This is model-maintained
working context, not a form or prerequisite for the user. The resulting local
map keeps repeated reviews aligned without turning one user's corpus into PASS
canon or a release dependency. If no map exists, classify only the current
subject from the user's stated reason for selecting it and continue.

## One-card, one-slice protocol

Run one bounded review at a time. One review may use a small prerequisite chain
when the selected card requires it, but it must name one primary card and one
coherent source-code slice.

1. **Name the engineering decision.** State what the review is trying to learn
   and why the selected source is relevant.
2. **Read the primary card completely.** Follow its prerequisites and load only
   the few cards needed to apply it. Prefer a language-specific card when the
   code is in an authored language; use core cards where the real decision calls
   for them rather than testing the whole core first.
3. **Read the real implementation.** Inspect the implementation, declarations,
   call sites, tests, build configuration, and failure paths needed to establish
   the card's `IF` condition. A single convenient file is not automatically the
   review boundary.
4. **Make notes before judging.** Record the human design, apparent constraints,
   tradeoffs, and uncertainties. Human code is evidence and precedent, not
   infallible ground truth.
5. **Build a small proof of concept.** Reproduce the decision in an isolated
   artifact small enough to understand. Apply the card and the lessons learned
   from the human implementation; do not recreate the entire project.
6. **Exercise it.** Compile and run the proof of concept. Include a failure,
   misuse, or boundary case when the claimed behavior is enforcement or
   robustness. Preserve the machine output.
7. **Compare the designs.** Compare the proof of concept with the human code in
   terms of behavior, constraints, clarity, ownership, failure handling,
   testability, and language idiom. Counts of assertions, comments, files,
   attributes, or lines may describe the artifacts but never decide which is
   better.
8. **Attribute the result.** Decide whether the evidence concerns the card,
   missing language specialization, retrieval, application, incomplete source
   context, the proof-of-concept fixture, or the toolchain.
9. **Record and stop.** Write the empirical result to Skillset Memory and report
   the single review. Do not launch another source, card, model, or repetition
   automatically.

The proof of concept is intentionally informed by both the card and the human
code. This workflow studies whether a model can learn and improve from those two
inputs together. It does not isolate the card's causal effect.

## Required review note

Use this compact record for each field test:

```markdown
# Software card field test

- Selection role: neutral external corpus | project-relevant reference | interest-led investigation
- Review subject: repository and revision
- Evaluation route: maintainer qualification | project application
- Language and module under test:
- Primary card: object id
- Supporting cards: object ids, if any
- Engineering decision:
- Source slice inspected: implementation, declarations, call sites, tests, build files
- Card IF established:

## Human implementation notes

## Proof of concept

## Machine evidence

## Comparison

## Attribution

## Memory disposition
```

Repository identity and revision belong in the empirical review note so the
observation can be checked later. They never enter the canonical card.

## What this workflow may establish

A valid field test can show that a card:

- identifies a real decision in production code;
- gives a model enough guidance to build and exercise a working example;
- helps the model find a genuine defect in human code and demonstrate the defect
  with source context or machine evidence;
- misses a constraint, language idiom, precondition, or failure mode;
- is correct but was retrieved or applied badly; or
- helps the model revise its own design after studying human precedent.

Finding a human defect does not make the review subject bad evidence. Human code
is a precedent with real constraints, not an answer key. A card that helps the
model identify and demonstrate a real defect has produced useful field evidence.

## Language evidence and core cards

Core ownership and verified language coverage are different facts. A core card
is intended to express one cross-language engineering decision, regardless of
whether the instruction was first learned from a C++, Java, or other
language-specific source. Its source language does not force the finished card
into that language module when the reusable decision itself is language-neutral.

Keep exactly one canonical core card. Language modules add only the syntax,
idioms, mechanisms, constraints, and exceptions needed to apply that decision in
their language. Do not copy the core library into every language module, and do
not fork a core card merely because its current field evidence comes from one
language. Releases include the shared core once plus the selected language
module or modules and their dependency closure.

Start with the authored language module. Select a language-specific card and
real code in that language; load a core card when it is a prerequisite or when
the source slice independently triggers its decision. Do not require the core
library to pass first.

A core card tested through one language has evidence **in that language only**.
That limits its verified coverage, not its intended cross-language scope. Record
the language and module in the review note and let evidence accumulate against
the same canonical card as additional languages become available. A failure may
belong to missing language specialization rather than to the core decision
itself; attribute that distinction before changing canon.

## Gate before active-project use

Schema validation proves that a card is well formed; it does not prove that the
card is useful engineering guidance. End every project-relevant field test with
one of these dispositions:

- **Ready for a project trial.** The card's `IF` condition was established from
  real context, the proof of concept compiled and exercised the claimed
  behavior, and comparison found no missing constraint that would make the
  guidance unsafe or misleading in the active project.
- **Needs card repair or language support.** The card was incomplete, too broad,
  too mechanism-specific, or missing a necessary language idiom.
- **Needs another valid review.** Tooling, incomplete context, or a faulty proof
  of concept prevented a judgment. This is not a failed card.

“Ready for a project trial” authorizes cautious application and the active
project's own review and tests; it is not a promise that the change is correct.
For a load-bearing design decision, propose a second review against a different
source and wait for approval rather than launching it automatically.

One review does not prove that PASS caused an improvement, that the human design
is universally best, or that the card works across all projects. A causal claim
requires a separately approved comparative study under
`PASS_CONSUMPTION.md`; ordinary card maintenance does not.

## Drift and stopping rules

Stop and report before continuing when:

- the model starts generating unrelated systems instead of reviewing the chosen
  source slice;
- the verdict has become a proxy count rather than an engineering comparison;
- required source context cannot be established;
- the proof of concept cannot exercise the claimed decision;
- the review subject's selection role was recorded incorrectly; or
- the work is being reframed as a treatment/control study without explicit
  approval.

A field test uses one reviewer and no automatic repetitions. It may use ordinary
tools to inspect, build, and test code, but it does not need parallel model arms.
Finish and report the review before proposing another.
