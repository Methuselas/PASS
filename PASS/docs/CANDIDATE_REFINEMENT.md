# PASS — Candidate Refinement & Qualification (CRQ)

status: active
owner: PASS/runtime/candidate_qualification
last_reviewed: 2026-09-26

CRQ is the bridge between *repeated valid evidence suggests a card may need to
change* and *this specific bounded change was compared against the current canon
on explicit cases, improved what it claimed to improve, broke nothing it was
asked to protect, and is ready for deliberate review*.

It is not an autonomous self-editing system. It never writes `library/`, never
writes Skillset Memory, never promotes memory into canon, never calls a model,
and never scores a skill. Its strongest outcome is
`qualified-for-synthesis-review`, and even that changes nothing until a person or
agent authorized for the task lands the approved delta through the ordinary
repository workflow.

The controller is `PASS/runtime/pass_candidate_qualification.py` (the command
line) over the `PASS/runtime/candidate_qualification/` package. Python
administers state, hashes, structure and gate logic; it does not judge
engineering, writing, art or any other domain quality. Everything the controller
checks is stated here so the method survives without the script.

---

## 1. Canon, memory, history, regression

```text
CANON        Patterns / APs / Drills in library/. Authoritative. Source-independent.
MEMORY       memory/<domain>/skill_memory.yaml. A card_candidate incubates a possible
             canon lesson. Never canon; never edited by CRQ.
HISTORY      memory/<domain>/training_history.jsonl. Valid events are the evidence.
REGRESSION   Deterministic tests that must keep passing after a change lands.
CRQ          workspace/candidate-qualification/<domain>/<run-id>/. Disposable
             administration scratch that compares one bounded candidate to canon.
```

Evidence flows one way:

```text
real use / Drill / field test -> training_history.jsonl -> card_candidate
  -> CRQ assessment -> frozen plan -> bounded candidate -> baseline vs candidate
  -> per-case deltas and the no-regression gate -> synthesis review
  -> an approved delta lands in library/ through the normal workflow, or nothing changes
```

## 2. Lifecycle

```text
prepared -> assessment-frozen -> plan-frozen -> candidate-staged -> candidate-frozen
  -> execution-open -> execution-frozen -> evaluated -> finalized
```

`invalidate` and `abandon` close any nonterminal run with a recorded reason.
Finalized, invalidated and abandoned runs are read-only except for `status`.

| Command | From | To | What it does |
|---|---|---|---|
| `prepare` | none | prepared | Resolves the memory candidate, freezes the intake and baseline |
| `prepare-synthesis` | prepared | prepared | Builds or advances evidence packets; never changes state |
| `freeze-assessment` | prepared | assessment-frozen | Validates and freezes the defect assessment |
| `freeze-plan` | assessment-frozen | plan-frozen | Validates and freezes the plan, cases and fixtures |
| `stage-candidate` | plan-frozen | candidate-staged | Copies revisable cards out of the baseline |
| `freeze-candidate` | candidate-staged | candidate-frozen | Accounts for every change, validates the overlay, freezes |
| `open-execution` | candidate-frozen | execution-open | Writes result templates, freezes both arm bundles |
| `freeze-execution` | execution-open | execution-frozen | Validates and freezes every arm result and its evidence |
| `evaluate` | execution-frozen | evaluated | Computes deltas and the gate, freezes the result |
| `finalize` | evaluated | finalized | Checks the disposition, writes the report, closes the run |
| `status` | any | unchanged | Read-only summary |
| `invalidate` / `abandon` | any nonterminal | invalidated / abandoned | Closes the run |

Every mutating command reopens `controller/run.json`, verifies its schema and the
controller fingerprint, verifies the frozen baseline and every freeze record,
performs one atomic transition, and reads the result back. A command from the
wrong state, or one whose checks fail, changes nothing.

**Nothing frozen is revised in place.** A freeze is never replaced. A different
assessment, plan or candidate is a fresh run, which may name its predecessor in
free text; there is no run graph and no re-freezing.

**The controller fingerprint** is one SHA-256 over every file of the package plus
the entry script, each LF-normalized and hashed, combined in path order. It is
recorded at `prepare`; any later lifecycle command under a different controller
stops, because administration rules must not change mid-run. `invalidate` and
`abandon` do not require a match (closing makes no evidence claim) and record the
closing fingerprint beside the original. Card and evidence hashes are always
byte-exact.

## 3. Intake: the memory candidate

A run starts from one Skillset Memory entry:

```bash
python PASS/runtime/pass_candidate_qualification.py prepare \
  --domain software-engineering --memory-entry SE_MEM_0042
```

`prepare` refuses unless:

- the domain's store passes `memory.py validate`;
- the entry is a `card_candidate` in `active` or `monitoring`;
- it cites at least one event, and every cited event is valid, a performance
  event, and not quarantined by an evidence correction;
- every likely owner written as an object id is a card in the run's domain or in
  `metaskills`, and at least one is a card in the run's domain. Card names and
  free-text labels are kept as labels and resolve nothing. A candidate for a new
  card names the nearest existing card it would join.

`confidence: strong` never implies a canon defect; confidence describes repeated
evidence, not ownership. Only the run's domain plus `metaskills` is read.

The entry and its cited events are frozen as `controller/intake.json`. The
baseline freezes, byte-exact under `baseline/cards/`, the in-domain owners
(targets), their transitive hard prerequisites (foundation, `variant_of`, and
incoming `prerequisite_for` / `foundation_of`), one hop of their other links, and
the owning `MODULE.yaml` files. A change to any of those canonical files, or to
the snapshot, stops every later command; start a fresh run against the new
canon. Changes elsewhere in the library do not.

Run ids are local and readable (`SE_CRQ_0001`), allocated by scanning only that
domain's run folder. They have no canonical meaning.

## 4. Evidence synthesis

With 1–8 cited events, direct review is fine. With 9–24, hierarchical synthesis
is recommended; above 24 it is expected before assessment unless the user
chooses direct review. These are context-management defaults, not quality
thresholds.

`prepare-synthesis` runs only before the assessment freezes. Its first call packs
every cited event exactly once, in cited order, six per leaf batch under
`synthesis/levels/0/batch-NNN/input.json`. A reviewer writes `summary.json`
beside each packet:

```json
{"schema_version": 1,
 "claims": [{"claim": "...", "supporting_event_ids": ["SE_EV_0101"], "contradicting_event_ids": []}],
 "persistent_failures": [{"note": "...", "event_ids": ["SE_EV_0114"]}],
 "stable_successes": [], "boundary_notes": [], "unresolved_conflicts": []}
```

Each later call re-derives every level from the intake and the summaries below
it, refuses a changed packet, a missing summary, or an id that is not an event
under that batch, and then merges four summaries per parent batch. A parent must
keep every contradiction its children recorded, as a contradicting event or an
unresolved conflict; failures and contradictions are listed first in each parent
packet. When one batch remains, `synthesis/input.json` holds the final summary.
The check guarantees traceability, not that the prose is faithful. Synthesis
informs the assessment; it authorizes nothing.

## 5. Defect assessment

Attribute before editing. Fill `controller/assessment.json`, then
`freeze-assessment`.

- `candidate_disposition`: `canon-candidate`, `memory-only`, `runtime-tool-repair`,
  `fixture-repair`, `source-context-review`, `fresh-retest`, `no-action`,
  `unresolved`. Only `canon-candidate` continues to candidate authoring; every
  other disposition may freeze for the record with no object actions, and the run
  is then abandoned.
- `failure_layer`: the Skillset Memory vocabulary. A canon candidate needs
  `knowledge` (a Pattern's reusable decision), `orchestration` (an AP's
  goal-directed flow) or `training` (a Drill's practice or evaluation). Retrieval,
  application, continuity, reference, tool and interface failures never justify a
  card change.
- `primary_attribution`: `skillcard`, `application`, `source-context`, `fixture`,
  `runtime-tool`, `unresolved`, `other`. A canon candidate is `skillcard`.
- `owner_object_ids`: exact baseline cards. When the cited events record which
  cards were exposed, a Pattern or AP owner must be among them.
- `proposed_object_actions`: `revise` a baseline card of the run's domain that is
  listed as an owner, or `create` a new card with its library-relative path inside
  a domain module folder. Delete, rename and move do not exist. A `metaskills`
  defect needs its own authorized maintenance run.
- A repair routed against its layer (an orchestration defect to a Pattern, a
  single decision to an AP) needs a `routing_reason` saying why that card itself
  is defective.
- `noncanon_failures_considered` records each alternative cause weighed; an
  unresolved one blocks a canon candidate, as does an unresolved question with
  `decides_ownership: true`.
- The scope ceilings apply: by default 3 revised and 2 new cards. Raising either
  at `prepare` requires a recorded reason; no setting enables delete, rename or
  move.

## 6. Qualification plan and cases

The plan freezes before any candidate is staged, so held-out cases cannot shape
the edit. Fill `controller/qualification_plan.json` and one
`cases/<CASE_ID>/case.json` per case; list fixtures under
`cases/<CASE_ID>/fixture/` with their SHA-256.

| Field | Values |
|---|---|
| `role` | `target` (the candidate must improve it), `protected` (it must not break) |
| `origin` | `empirical`, `deterministic`, `synthetic` |
| `evaluation_mode` | `deterministic`, `semantic` |
| `visibility` | `author-visible`, `held-out` |
| `evaluator_relation` | `deterministic`, `separate`, `same-reader` |

- An empirical case cites valid, uncorrected, unquarantined history events.
- A deterministic case is checked deterministically. A required semantic case is
  graded by a separate evaluator; `same-reader` is only for non-required
  diagnostics.
- Only a target can provide positive qualification.
- **Synthetic cases are stress probes only**: protected, never positively
  eligible, citing no event, and carrying an `in_scope_reason` that says why the
  case stays inside the card's intended contract. Passing one proves nothing;
  failing one blocks.
- The plan needs a required non-synthetic target eligible for positive
  qualification. Without a required non-synthetic protected case it must record
  `protected_case_gap`, and the run cannot qualify beyond that gap. "We had no
  regression set, so there were no regressions" is never a conclusion.
- `task`, `success_contract` and `constraints` are identical for both arms and
  frozen before either arm is graded.

**Held-out is a protocol boundary, not a sandbox.** The candidate author's brief
shows author-visible target cases only and counts the held-out ones. Reading a
held-out case before the candidate freezes is contamination and invalidates the
qualification it touches.

## 7. Candidate authoring and freezing

`stage-candidate` refuses any disposition other than `canon-candidate`. It copies
each revised card byte-for-byte from the baseline into `candidate/cards/<path>`,
creates only the empty folder for a new card (Python never writes card content),
and writes the candidate author brief.

The author edits ordinary Markdown cards and fills one `rationale` per change in
`controller/candidate_manifest.json`. A candidate card stays an ordinary,
source-independent PASS card: it never names the run, a memory entry, a training
event, a case, a workspace path or an evidence hash.

`freeze-candidate` accounts for everything:

- every authorized action must produce a real content change: a missing revised
  card (a deletion), a byte-identical or whitespace-only file, a changed
  `object_id` (a rename) or `object_type`, or a new card that was never written is
  unmatched;
- every file under `candidate/cards/` must belong to an action: an extra file, a
  moved card, or an edited copy of a support card is unauthorized;
- the scope ceilings hold, and a new card's path is still free in canon.

Any unmatched action blocks the freeze until the staged files are corrected. The
authorized actions come from the frozen assessment and are never revised in
place: a different set of actions is a fresh run.

The candidate is then laid over a temporary copy of the live library, and the
ordinary validators run on it: `validate.py --library <overlay>` and
`verify_references.py --library <overlay>`. There is no weaker candidate schema.
The overlay is always removed, and canon is only read. The frozen manifest
records baseline and candidate hashes, the changed sections, the rationale and
the scope; card bytes changing after the freeze stop the run.

## 8. Execution

CRQ is not an agent runner. The host, human or model runs each case with the
appropriate existing mechanism (a test command, a Drill, Code Apprenticeship, a
fresh evaluator context), and the controller administers the evidence.

`open-execution` freezes two bundles, `arms/baseline/cards/` and
`arms/candidate/cards/`, and writes `cases/<CASE_ID>/<arm>/result.json` templates
bound to the frozen case definition's hash. The execution brief now reveals every
case.

- Each arm uses a fresh context. The candidate arm never sees baseline answers;
  the baseline arm never sees candidate content. The evaluator grades the frozen
  arm artifact, never the arm's own summary of it.
- `verdict` is `pass`, `fail` or `invalid`; there is no partial result. A pass
  needs every success criterion to pass; a fail names the failing criteria. An
  arm that could not exercise the capability (tooling, fixture, missing context,
  contamination) is `invalid` with a reason, never a fail.
- Every file under the arm's `evidence/` is listed in `evidence_manifest` with its
  SHA-256; a pass or fail needs evidence.
- `contamination` is `none`, `suspected` or `confirmed`. Suspected must be
  resolved before `freeze-execution`; confirmed makes that arm invalid and, as
  PASS's contamination rule requires, invalidates the whole batch.
- **`environment` holds only comparison-relevant facts**: toolchain and runtime
  versions, the model id, and flags that change behavior. Both arms must declare
  exactly the same object; any difference invalidates that case's comparison.
  Incidental details such as timestamps, paths and hostnames belong in `notes` or
  the `executor` block, which are not compared.
- Both arms must be graded against the frozen case definition (`case_sha256`); a
  mismatch invalidates the comparison, it is not a candidate failure.

## 9. Per-case delta and final gate

```text
baseline fail + candidate pass  -> improved
baseline pass + candidate pass  -> stable
baseline pass + candidate fail  -> regressed
baseline fail + candidate fail  -> persistent-fail
any invalid arm or comparison   -> invalid
```

There is no numeric score. Non-required cases are diagnostics and never decide
the status. The gate applies these rules in order:

1. **Invalid** — a required case's comparison is invalid, or contamination was
   confirmed anywhere: `invalid`. No capability conclusion is drawn.
2. **Protected regression** — a required non-synthetic protected case regressed:
   `rejected-regression`. One regression vetoes any number of improvements.
3. **Target failure** — a required target still fails on the candidate:
   `rejected-target-failure`.
4. **Synthetic stress** — a required synthetic case fails on the candidate:
   `blocked-by-synthetic-stress`. The candidate cannot be qualified in this run. A
   stress case later judged out of scope or malformed is not removed from a frozen
   plan: revising the plan means a fresh run with a corrected or replaced case.
   Passing synthetic cases contributes nothing.
5. **Protection gap** — no required non-synthetic protected case:
   `inconclusive-protection-gap`.
6. **Positive improvement** — no required, eligible, non-synthetic target
   improved: `inconclusive-no-improvement`.
7. Otherwise `qualified-for-synthesis-review`.

`evaluate` writes and freezes `qualification_result.json`: the status and reason,
every case delta with any comparison problem, the blocking and positive cases,
the synthetic cases, the protection gap, whether contamination was confirmed,
and the change accounting (`accepted-for-synthesis-review`,
`rejected-by-qualification`, or `applied-to-candidate` when the gate reached no
qualification decision). `canon_modified` is always false.

## 10. Synthesis review and finalization

`evaluate` also writes `synthesis/disposition.json` for deliberate review:

- `synthesis_decision`: `accept-canonical-delta`, `revise-in-fresh-run`,
  `split-candidate`, `redirect-ownership`, `retain-in-memory`,
  `add-deterministic-regression`, `reject-redundant`, `reject-false`,
  `reject-too-narrow`. Only a qualified candidate may be accepted.
- `memory_action`: `keep-active`, `keep-monitoring`, `narrow-boundary`,
  `supersede-candidate`, `resolve-after-canon-fix`, `obsolete`, `no-change`.
  `resolve-after-canon-fix` needs an accepted delta or a deterministic regression.

`finalize` checks the disposition against the frozen status, writes
`synthesis/report.md`, freezes both, and closes the run. It writes neither
`library/` nor memory.

**Acceptance still changes nothing by itself.** When the user or maintainer has
authorized the integration task, the approved delta lands like any other card
change: `validate.py`, `verify_references.py`, `build_index.py`, the test suite,
and the version and changelog rules. Then apply the memory recommendation with
`memory.py entry`:

- a deterministic defect gains or keeps a regression test, and only then is the
  candidate resolved;
- a stochastic defect keeps the candidate `monitoring` until fresh evidence
  verifies the changed card;
- a candidate is never resolved merely because Markdown was edited.

Never append a positive training event because a synthetic case passed. A
synthetic failure that exposes a real deterministic contract bug may motivate a
regression test and a new card candidate; the durable evidence is the reproduced
failure.

## 11. Failure categories

| Category | Examples | Result |
|---|---|---|
| Administration error | malformed JSON, wrong state, path escape, unknown owner, scope violation, unmatched action | The command fails; state is unchanged |
| Invalid qualification | confirmed contamination, an arm that could not exercise the capability, asymmetric arms, held-out case graded same-reader | `invalid`, or `invalidate` the run; never a candidate failure |
| Candidate failure | target still fails, protected behavior regressed, a valid stress case fails | A deterministic rejection or block; the evidence stays inspectable |

## 12. Workspace and cleanup

```text
workspace/candidate-qualification/<domain>/<run-id>/
  controller/   run.json, intake, baseline manifest, assessment, plan,
                candidate manifest and every freeze record
  baseline/cards/   frozen canonical copies
  candidate/cards/  the staged overlay
  cases/<id>/       case.json, fixture/, baseline/ and candidate/ results and evidence
  arms/<arm>/cards/ the frozen bundle each arm executes
  synthesis/        evidence packets, disposition.json, report.md
  qualification_result.json
  README.md         the brief for the current phase
```

A run is administration scratch. It never ships, never enters cards or memory,
and deleting it never invalidates canon or memory. Once it is finalized,
invalidated or abandoned and its outcome is handled (an approved delta verified
in `library/`, accepted regressions in the test suite, the memory recommendation
applied), remove it. Keep it only under an explicit evidence hold or while invalid
or contaminated evidence awaits diagnosis.

## 13. Relationship to other contracts

- Software field tests (`SOFTWARE_CARD_FIELD_TESTS.md`) remain the preferred way to
  produce held-out evidence about software cards. CRQ consumes their memory
  results; it does not reinterpret a valid `application` result as a card defect
  and does not weaken their evidence rules.
- Ordinary use (`PASS_CONSUMPTION.md`) never produces a qualification claim.
- Skillset Memory (`MEMORY_SCHEMA.md`) needs no schema change for CRQ.

## 14. What CRQ must not become

No trainable monolithic skill file, no automatic or nightly canon mutation, no
promotion by score, no weighted aggregate, no keyword-density quality bonus, no
optimizer memory store, no global run ledger or candidate registry, no model
provider dependency, no loop that edits until a number rises, and no synthetic
success counted as demonstrated transfer.

The guarantee is deliberately narrow: a specific bounded candidate was compared
against a frozen canonical baseline on explicit target and protected cases;
invalid runs were excluded; protected regressions could not be hidden by
aggregate scoring; synthetic success was not treated as empirical proof; and the
proposal is blocked, rejected, inconclusive, or qualified for deliberate
synthesis review.

## 15. Implementation map

| File | Owns |
|---|---|
| `PASS/runtime/pass_candidate_qualification.py` | The command line |
| `candidate_qualification/schemas.py` | Vocabularies, hashes, atomic JSON, containment, document validation |
| `candidate_qualification/evidence.py` | Memory intake, canon reading, accounting, overlay validation, arm evidence, synthesis packets |
| `candidate_qualification/gate.py` | The per-case delta and the final gate |
| `candidate_qualification/controller.py` | Run state, freezes, drift and the lifecycle commands |
| `tests/test_candidate_qualification_*.py` | State, intake, candidate, gate, execution and synthesis contracts on synthetic fixtures |
