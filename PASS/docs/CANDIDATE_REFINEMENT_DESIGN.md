# PASS Candidate Refinement & Qualification (CRQ)
## Implementation Design Document

**Status:** Proposed implementation contract  
**Target baseline:** PASS `1.0.0-beta.87` archive supplied 2026-09-26  
**Primary target:** `PASS-project-software-engineering` repository  
**Scope:** PASS factory/runtime architecture, Skillset Memory integration, empirical card refinement, candidate qualification, and regression protection  
**Implementation audience:** Codex, Claude, local coding agents, and human maintainers  

---

## 1. Executive summary

PASS already has the stronger architecture. It separates:

```text
CANON       Patterns / APs / Drills
MEMORY      compact retained learning and calibration
HISTORY     append-oriented empirical events
REGRESSION  deterministic checks that must keep passing
```

What PASS does not yet have as a complete subsystem is the bridge between:

> “Repeated valid evidence suggests canon may need improvement”

and:

> “This specific candidate change has been tested against the current baseline, improved the intended case, did not regress protected behavior, and is ready for deliberate synthesis review.”

This design adds that bridge as **Candidate Refinement & Qualification (CRQ)**.

CRQ is deliberately **not** an autonomous self-editing system. It does not mutate `library/`, does not promote memory into canon, does not replace PASS 1/2/3 source authoring, and does not add a second skill representation. It operates on ordinary PASS cards and ordinary Skillset Memory evidence.

The useful ideas are reimplemented natively in PASS terms:

1. **Defect attribution before repair.** A bad result must first be classified as a likely canon defect, application/retrieval lapse, tooling/fixture problem, source-context gap, or unresolved issue. Only canon-defect evidence may directly drive a card candidate.
2. **Baseline-versus-candidate qualification.** The current canonical behavior and a staged candidate are exercised against the same frozen cases.
3. **Per-case no-regression gate.** Aggregate improvement can never hide a regression. Any protected case that passes on baseline and fails on candidate blocks qualification.
4. **Bounded candidate mutation.** One candidate changes a small, explicit card set so success or failure remains attributable.
5. **Applied/rejected/unmatched accounting.** Every proposed target and candidate file is accounted for. Nothing silently disappears.
6. **Evidence synthesis at scale.** Large evidence sets are summarized hierarchically with explicit event citations rather than dumped into one prompt.
7. **Synthetic stress cases as veto-only evidence.** They may expose a defect or block a candidate, but they never count as empirical proof of demonstrated capability or transfer.
8. **Deliberate promotion boundary.** A qualified candidate becomes a proposal for synthesis/review, never an automatic library edit.

The intended lifecycle becomes:

```text
real use / Drill / field test
        ↓
training_history.jsonl
        ↓
skill_memory.yaml :: card_candidate
        ↓
CRQ defect assessment
        ↓
frozen qualification plan
        ↓
bounded candidate card overlay
        ↓
baseline vs candidate execution
        ↓
per-case delta + no-regression gate
        ↓
qualified-for-synthesis-review
        ↓
deliberate PASS review
        ↓
approved delta to library/  OR  reject / retain in memory
```

No step in that chain automatically promotes a candidate into canon.

---

## 2. Relationship to the current beta87 architecture

CRQ must extend the current contracts rather than replace them.

### 2.1 Existing contracts CRQ must preserve

From `ARCHITECTURE.md` and the current runtime/docs:

- Cards remain source-independent.
- Pattern owns reusable decisions.
- AP owns goal-directed orchestration.
- Drill owns repeatable practice/evaluation.
- Skillset Memory is not canon and not a fourth object type.
- `training_history.jsonl` remains event evidence.
- Invalid runs are not capability evidence.
- Memory never mutates canon.
- Deterministic invariants belong in canon, resolver logic, or regression tests rather than memory.
- Source authoring continues to run through `PASS/pass.py`.
- Software empirical card testing continues to use the existing Code Apprenticeship contract unless explicitly replaced later.
- Domain independence remains intact.
- Cross-domain authoring coupling remains invalid.
- Generated indexes remain generated.
- Workspace scratch remains disposable.
- Python may administer and validate methodology but must not be the only place the methodology exists.

### 2.2 Existing mechanisms CRQ should reuse

CRQ should build on, not duplicate:

- `PASS/tools/validate.py --library ...`
- `PASS/tools/memory.py`
- `PASS/docs/MEMORY_SCHEMA.md`
- `PASS/docs/SOFTWARE_CARD_FIELD_TESTS.md`
- `PASS/runtime/skillforge_code_study.py`
- canonical card object IDs and frontmatter
- library-relative card paths
- hash/manifests and frozen evidence patterns already used by field tests
- atomic JSON/text writes and path containment patterns already present in runtime code
- explicit state machines used by the authoring and Code Apprenticeship controllers

### 2.3 What CRQ must not import conceptually

Do **not** implement any of the following:

- a trainable monolithic `SKILL.md`
- automatic nightly canon mutation
- automatic promotion based on a score
- semantic-density scoring
- “more MUST/ALWAYS/NEVER words means better” heuristics
- a separate optimizer memory store
- a second canonical registry
- a hidden global skill index
- direct LLM-provider dependencies inside the PASS factory
- arbitrary self-editing loops that keep iterating until a score rises
- synthetic cases being counted as demonstrated empirical transfer

---

## 3. Design goals

CRQ must provide all of the following.

### G1 — Attribute before editing

A candidate may not be authored merely because an execution failed. The system must establish why the failure is plausibly owned by canon rather than application, retrieval, tooling, fixture, source context, or another layer.

### G2 — Preserve a frozen baseline

Every qualification run must know exactly which canonical card bytes it is comparing against. Library drift during a run must be detected and must not silently alter the baseline.

### G3 — Stage candidate changes outside canon

All candidate files must live outside `library/` until explicit deliberate approval.

### G4 — Validate candidates as real PASS cards

A candidate overlay must pass ordinary PASS schema/reference validation before it can be tested as a candidate.

### G5 — Compare per case, never by aggregate masking

For every qualification case, CRQ must record baseline and candidate outcomes and classify the delta independently.

### G6 — Fail closed on regression

A candidate that breaks any required protected case that baseline passed cannot receive qualified status.

### G7 — Separate positive proof from synthetic stress testing

Synthetic cases may challenge a candidate but cannot provide positive empirical qualification or increase Skillset Memory evidence counts.

### G8 — Keep semantic judgment outside deterministic scripts

Python may verify structure, state, evidence manifests, hashes, role separation declarations, result completeness, and gate logic. It must not pretend to judge engineering quality, writing quality, art quality, or other domain semantics.

### G9 — Produce reviewable outputs

A human or frontier/local coding agent must be able to inspect exactly:

- why the candidate exists,
- what changed,
- which cases were used,
- what baseline did,
- what candidate did,
- what regressed,
- what improved,
- what remained unresolved,
- and why the final gate produced its status.

### G10 — Remain portable

CRQ cannot depend on git, a particular agent host, a particular LLM API, or SkillOpt code. A checkout, extracted archive, clean Project, or other writable PASS environment may host a run.

---

## 4. Non-goals

CRQ v1 is **not** intended to:

- replace PASS source study;
- decide that a domain is mature;
- auto-author arbitrary new domains;
- perform RL, gradient descent, model weight updates, or fine-tuning;
- call OpenAI, Anthropic, LM Studio, llama-server, or any other model API directly;
- create a generic autonomous agent framework;
- rank cards numerically;
- assign a universal “quality score” to a skillset;
- keep permanent source snapshots in memory;
- preserve every CRQ workspace forever;
- prove causal attribution to one card from one ordinary field test;
- infer model learning or persistent learner state;
- mutate `library/` automatically;
- allow a candidate to silently delete, rename, or relocate established cards in v1.

---

## 5. Terminology

### Canon

The ordinary validated PASS library under `library/`.

### Evidence event

A valid empirical event in `memory/<domain>/training_history.jsonl`.

### Card candidate memory entry

A `type: card_candidate` entry in `memory/<domain>/skill_memory.yaml`. It is the durable, compact hypothesis that canon may need a change. It remains non-canonical.

### Candidate run

One CRQ administration run evaluating one coherent proposed change set.

### Baseline

The frozen canonical card set captured when the candidate run is prepared.

### Candidate overlay

A small set of staged PASS card files that replace or add to the baseline for validation and qualification. It is not canon.

### Target case

A case the candidate is intended to improve or newly satisfy.

### Protected case

A case that represents behavior the candidate must not break.

### Real case

A case based on actual use, evaluation, Drill execution, field-test evidence, or another non-synthetic situation.

### Deterministic case

A case whose correctness can be mechanically established by a reproducible checker/test.

### Semantic case

A case requiring domain judgment by a separate evaluator/grader rather than a mechanical assertion alone.

### Synthetic stress case

A generated variation intended to expose boundary failures. It is never positive empirical evidence.

### Delta

The per-case comparison between baseline and candidate:

```text
baseline fail + candidate pass  -> improved
baseline pass + candidate pass  -> stable
baseline pass + candidate fail  -> regressed
baseline fail + candidate fail  -> persistent-fail
any required invalid arm        -> invalid
```

### Qualified for synthesis review

The strongest status CRQ may produce. It means the candidate passed CRQ gates and is ready for deliberate canonical review. It does **not** mean the library was changed.

---

## 6. Architectural invariants

These are non-negotiable implementation rules.

### I1 — CRQ never writes `library/`

The controller may read and hash canon. It may build temporary validation overlays. It may never install the candidate itself.

### I2 — A card candidate entry is the normal durable starting point

A normal CRQ run begins from an existing Skillset Memory `card_candidate` entry with cited valid evidence events.

For a deterministic contradiction, one valid reproduction may justify creating the `card_candidate` first under the existing `deterministic_contract` threshold. CRQ still starts from that candidate entry rather than bypassing memory entirely.

### I3 — Invalid evidence cannot justify a candidate

Every event cited by the candidate entry must satisfy existing memory validation. Quarantined or invalid events cannot be counted.

### I4 — Attribution must be explicit

The run must state why the candidate is canon-eligible. “The output was bad” is insufficient.

### I5 — Candidate authoring is bounded

Default v1 ceilings:

```text
changed existing cards: 3
new cards:              2
deleted cards:          0
renamed object_ids:     0
moved existing cards:   0
```

An implementation may permit an explicit override for changed/new card ceilings, but the override must be recorded in `run.json` and must never enable deletion, renaming, or moving in v1.

### I6 — Candidate validation uses the ordinary PASS validator

Do not create a weaker “candidate schema.” A candidate card is either a valid PASS card or it is not eligible for qualification.

### I7 — Library drift invalidates the frozen comparison

If any frozen baseline/support card changes after the candidate run is prepared, continuation must stop. The user/maintainer may start a fresh run against the new baseline.

### I8 — No aggregate score can overrule a regression

There is no weighted acceptance score in CRQ v1.

### I9 — Protected regressions veto qualification

If baseline passes a required protected case and candidate fails it, the candidate is not qualified.

### I10 — Synthetic success is non-evidence

A synthetic case may never:

- increment `evidence_count`;
- be linked as positive empirical evidence to a compact memory entry;
- satisfy the mandatory positive improvement requirement;
- establish retention or transfer.

### I11 — Synthetic failure may block, not prove mastery

A synthetic stress failure may block qualification until resolved. Passing the same case provides no positive empirical credit.

### I12 — Invalid is distinct from fail

A tool failure, unresolved fixture, contamination, broken role isolation, unavailable context, or inconsistent metadata must produce `invalid`, not `fail`.

### I13 — Semantic held-out evaluation requires role isolation

A held-out semantic case used for qualification must be graded in a fresh/separate evaluator context. A same-reader semantic verdict cannot qualify a candidate.

### I14 — Deterministic checks need no fake “separate grader”

A deterministic checker may be recorded as deterministic. Do not force a human-style evaluator relation onto machine assertions.

### I15 — CRQ scratch remains disposable

Deleting `workspace/candidate-qualification/` must never invalidate canon or Skillset Memory.

### I16 — Results do not self-promote

Even `qualified-for-synthesis-review` requires deliberate PASS synthesis/review before any canonical edit.

---

## 7. High-level workflow

```text
┌─────────────────────────────────────────────┐
│ 1. Existing empirical evidence             │
│ training_history.jsonl                     │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│ 2. Existing Skillset Memory                │
│ type: card_candidate                       │
│ evidence_events + likely_owners + diagnosis│
└──────────────────┬──────────────────────────┘
                   │ prepare
                   ▼
┌─────────────────────────────────────────────┐
│ 3. CRQ defect assessment                   │
│ canon defect? owner? object role?          │
└──────────────────┬──────────────────────────┘
                   │ freeze
                   ▼
┌─────────────────────────────────────────────┐
│ 4. Qualification plan                      │
│ target cases + protected cases             │
│ held-out visibility frozen                 │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│ 5. Candidate authoring                     │
│ small overlay outside library/             │
└──────────────────┬──────────────────────────┘
                   │ validate + freeze
                   ▼
┌─────────────────────────────────────────────┐
│ 6. Execute baseline and candidate arms     │
│ same case / same frozen environment        │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│ 7. CRQ deterministic gate                  │
│ per-case deltas + no-regression            │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│ 8. Synthesis review                        │
│ qualified / rejected / inconclusive        │
└──────────────────┬──────────────────────────┘
                   │ explicit approved delta only
                   ▼
              library/ canon
```

---

## 8. State machine

The controller must use an explicit state machine.

```text
prepared
  ↓
assessment-frozen
  ↓
plan-frozen
  ↓
candidate-staged
  ↓
candidate-frozen
  ↓
execution-open
  ↓
execution-frozen
  ↓
evaluated
  ↓
finalized
```

Terminal exceptional states:

```text
invalidated
abandoned
```

### Allowed transitions

| Current | Command | Next |
|---|---|---|
| none | `prepare` | `prepared` |
| `prepared` | `freeze-assessment` | `assessment-frozen` |
| `assessment-frozen` | `freeze-plan` | `plan-frozen` |
| `plan-frozen` | `stage-candidate` | `candidate-staged` |
| `candidate-staged` | `freeze-candidate` | `candidate-frozen` |
| `candidate-frozen` | `open-execution` | `execution-open` |
| `execution-open` | `freeze-execution` | `execution-frozen` |
| `execution-frozen` | `evaluate` | `evaluated` |
| `evaluated` | `finalize` | `finalized` |
| any nonterminal | `invalidate` | `invalidated` |
| any nonterminal | `abandon` | `abandoned` |

A command invoked from the wrong state must fail without changing state.

### Resume behavior

Each command must:

1. reopen `run.json`;
2. verify schema version;
3. verify controller hash/version if CRQ follows the Code Apprenticeship controller-hash precedent;
4. verify frozen manifests relevant to the current state;
5. refuse continuation on drift;
6. perform one atomic state transition;
7. read back the written state before reporting success.

### 8.1 `run.json` schema

`controller/run.json` is the authoritative CRQ administration state for the run.

Minimum v1 shape:

```json
{
  "schema_version": 1,
  "run_id": "SE_CRQ_0001",
  "domain": "software-engineering",
  "state": "prepared",
  "created_at": "2026-09-26T20:00:00Z",
  "updated_at": "2026-09-26T20:00:00Z",
  "controller_sha256": "...",
  "memory_entry_id": "SE_MEM_0042",
  "library_root": "...",
  "memory_root": "...",
  "scope_limits": {
    "max_changed_cards": 3,
    "max_new_cards": 2
  },
  "files": {
    "baseline_manifest": "controller/baseline_manifest.json",
    "assessment": "controller/assessment.json",
    "qualification_plan": "controller/qualification_plan.json",
    "candidate_manifest": "controller/candidate_manifest.json",
    "qualification_result": "qualification_result.json"
  },
  "invalid_reason": null,
  "abandoned_reason": null
}
```

Rules:

- `schema_version` is controller-state schema, not PASS card or memory schema.
- Record the controller file SHA-256 at `prepare`.
- Every mutating command after `prepare` verifies the controller hash before continuing. A controller implementation change mid-run stops continuation; start a fresh run rather than silently changing administration semantics.
- `library_root` and `memory_root` are workspace administration metadata and may be environment-specific. They never enter cards or Skillset Memory.
- Store relative paths for run-owned files.
- `invalid_reason` is required only in `invalidated`.
- `abandoned_reason` is required only in `abandoned`.
- Finalized, invalidated, and abandoned runs are read-only except for `status`/reporting.
- New controller versions may read older schemas only when explicitly listed in `READABLE_SCHEMA_VERSIONS`; they must not silently migrate and requalify old results.

---

## 9. Workspace layout

Add one explicit workspace purpose bucket:

```text
workspace/candidate-qualification/
```

A run lives at:

```text
workspace/candidate-qualification/<domain>/<candidate-run-id>/
```

Recommended layout:

```text
<run>/
├── controller/
│   ├── run.json
│   ├── baseline_manifest.json
│   ├── assessment.json
│   ├── assessment.freeze.json
│   ├── qualification_plan.json
│   ├── plan.freeze.json
│   ├── candidate_manifest.json
│   ├── candidate.freeze.json
│   └── execution.freeze.json
│
├── baseline/
│   └── cards/<library-relative paths...>
│
├── candidate/
│   └── cards/<library-relative paths...>
│
├── cases/
│   └── <case-id>/
│       ├── case.json
│       ├── fixture/                 # optional frozen artifacts
│       ├── baseline/
│       │   ├── result.json
│       │   └── evidence/...
│       └── candidate/
│           ├── result.json
│           └── evidence/...
│
├── synthesis/
│   ├── input.json
│   ├── report.md
│   └── disposition.json
│
├── qualification_result.json
└── README.md                        # generated operator brief
```

The run directory is evidence/admin scratch. It does not ship in SkillForge releases.

---

## 10. Candidate run identity

Use a stable readable run ID, for example:

```text
SE_CRQ_0001
ART_CRQ_0001
WRITING_CRQ_0001
```

The controller may allocate the next local ID by scanning only the candidate-qualification workspace for that domain. This is not a global registry and has no canonical meaning.

`candidate-run-id` and Skillset Memory entry IDs are different identifiers.

---

## 11. Input contract: card candidate memory entry

The normal `prepare` command requires one existing memory entry:

```yaml
type: card_candidate
status: active | monitoring
```

The entry must have:

- at least one valid `evidence_event`;
- a self-contained `observation`;
- `diagnosis.failure_layer` when a failure is involved;
- at least one `likely_owners` value when an existing owner is suspected, or an explicit assessment explaining why a new card may be required.

CRQ must not infer “canon defect” solely from `confidence: strong`. Confidence describes repeated evidence, not ownership.

### Preparation checks

`prepare` must fail when:

- the memory entry does not exist;
- its type is not `card_candidate`;
- its status is resolved/superseded/obsolete;
- it cites an invalid, quarantined, or correction event;
- a named object owner does not exist in the current domain/metaskills closure;
- the requested CRQ domain does not match the memory store;
- the memory store itself fails `memory.py validate`.

---

## 12. Defect assessment

CRQ reimplements “skill defect versus execution lapse” in PASS-native terms.

Do not introduce the names `SKILL_DEFECT` or `EXECUTION_LAPSE` into canon. Use PASS terminology.

### 12.1 Required assessment fields

`controller/assessment.json`:

```json
{
  "schema_version": 1,
  "run_id": "SE_CRQ_0001",
  "memory_entry_id": "SE_MEM_0042",
  "candidate_disposition": "canon-candidate",
  "failure_layer": "knowledge",
  "primary_attribution": "skillcard",
  "owner_object_ids": ["SE_CORE_PATTERN_EXAMPLE"],
  "proposed_object_actions": [
    {
      "action": "revise",
      "object_id": "SE_CORE_PATTERN_EXAMPLE",
      "object_type": "pattern",
      "reason": "The existing rule is underspecified for the demonstrated condition."
    }
  ],
  "noncanon_failures_considered": [
    {
      "kind": "application",
      "disposition": "not-supported",
      "reason": "The exposed card lacks the required condition, so following it would not have prevented the failure."
    }
  ],
  "rationale": "...",
  "unresolved_questions": []
}
```

### 12.2 `candidate_disposition`

Allowed values:

```text
canon-candidate
memory-only
runtime-tool-repair
fixture-repair
source-context-review
fresh-retest
no-action
unresolved
```

Only `canon-candidate` may proceed to candidate authoring.

### 12.3 `failure_layer`

Reuse the existing Skillset Memory vocabulary:

```text
knowledge
orchestration
retrieval
application
continuity
reference
tool
interface
training
```

Do not create a competing global taxonomy.

### 12.4 `primary_attribution`

Reuse the field-test concepts where applicable:

```text
skillcard
application
source-context
fixture
runtime-tool
unresolved
other
```

If `primary_attribution == skillcard`, at least one exact canonical owner object ID is required unless the assessment explicitly proposes a new object because no existing owner is correct.

### 12.5 Canon eligibility rules

Typical routing:

| Finding | Normal disposition |
|---|---|
| existing Pattern missing/wrong reusable decision | `canon-candidate` |
| existing AP missing/wrong reusable orchestration | `canon-candidate` |
| Drill itself incorrectly evaluates/practises a capability | `canon-candidate` |
| card is correct but agent ignored it | `memory-only` or `fresh-retest` |
| card was never retrieved | `memory-only`, retrieval/runtime investigation |
| controller/tool failed | `runtime-tool-repair` |
| fixture changed the deciding condition | `fixture-repair` |
| required source/project context unavailable | `source-context-review` |
| evidence cannot distinguish causes | `unresolved` |

This table is guidance. The assessment must explain the actual case.

### 12.6 Freeze rule

`freeze-assessment` must reject:

- unresolved questions that decide ownership;
- `canon-candidate` with no proposed object action;
- proposed modification of a card outside the active domain. A CRQ run authors exactly one domain/package; a metaskill defect requires its own separately authorized metaskill maintenance run rather than being repaired as a side effect of another domain's CRQ run;
- a `skillcard` attribution to a card that the originating evidence did not expose when that fact is mechanically available from the evidence event/intervention;
- a repair routed to a Pattern when the identified defect is purely orchestration without an explicit reason;
- a repair routed to an AP when the identified defect is only one reusable decision already owned by a Pattern, unless the AP itself is also defective.

---

## 13. Qualification plan

The qualification plan must be frozen **before candidate content is frozen**. For semantic held-out cases, selection should occur before candidate authoring whenever practical so the candidate is not tailored to the exact hidden case.

`controller/qualification_plan.json`:

```json
{
  "schema_version": 1,
  "run_id": "SE_CRQ_0001",
  "cases": [
    {
      "case_id": "TARGET_001",
      "role": "target",
      "origin": "empirical",
      "evaluation_mode": "semantic",
      "visibility": "author-visible",
      "required": true,
      "positive_qualification_eligible": true,
      "source_event_ids": ["SE_EV_0123"],
      "purpose": "Reproduce the demonstrated missing condition under equivalent constraints."
    },
    {
      "case_id": "PROTECT_001",
      "role": "protected",
      "origin": "empirical",
      "evaluation_mode": "semantic",
      "visibility": "held-out",
      "required": true,
      "positive_qualification_eligible": false,
      "source_event_ids": ["SE_EV_0098"],
      "purpose": "Protect an established behavior of the same card."
    },
    {
      "case_id": "STRESS_001",
      "role": "protected",
      "origin": "synthetic",
      "evaluation_mode": "semantic",
      "visibility": "held-out",
      "required": true,
      "positive_qualification_eligible": false,
      "source_event_ids": [],
      "purpose": "Probe a nearby boundary without counting as empirical transfer."
    }
  ]
}
```

### 13.1 Allowed roles

```text
target
protected
```

### 13.2 Allowed origins

```text
empirical
deterministic
synthetic
```

`deterministic` means an established reproducible contract/check rather than a generated hypothetical.

### 13.3 Synthetic-role restriction

In CRQ v1, `origin: synthetic` is allowed only with:

```text
role: protected
positive_qualification_eligible: false
```

Synthetic cases are stress probes, not motivating target evidence. A synthetic case must therefore never satisfy the target-case minimum or the positive-improvement requirement.

### 13.4 Evaluation modes

```text
deterministic
semantic
```

A deterministic case may still originate from empirical discovery.

### 13.5 Visibility

```text
author-visible
held-out
```

Held-out is a procedural isolation contract. The controller must keep its detailed task/evidence outside the candidate-author brief until the candidate is frozen.

### 13.6 Minimum plan

A qualifying run requires:

- at least one required target case;
- at least one required **non-synthetic** protected case when the changed card already has demonstrated established behavior suitable for protection;
- at least one non-synthetic target case eligible to provide positive qualification.

If no appropriate non-synthetic protected case exists yet, and no deterministic regression suite supplies equivalent protection, the plan may proceed but must record:

```json
"protected_case_gap": "No established independent protected case is currently available."
```

The final status then cannot exceed `inconclusive-protection-gap` unless the candidate change is covered by deterministic regressions that provide equivalent protection.

This prevents “we had no regression set, therefore there were no regressions” from becoming a false claim.

---

## 14. Case contract

Each case gets its own `cases/<case-id>/case.json`.

Recommended schema:

```json
{
  "schema_version": 1,
  "case_id": "TARGET_001",
  "role": "target",
  "origin": "empirical",
  "evaluation_mode": "semantic",
  "visibility": "author-visible",
  "required": true,
  "positive_qualification_eligible": true,
  "task": "...",
  "success_contract": [
    "Observable criterion 1",
    "Observable criterion 2"
  ],
  "constraints": [
    "Constraint that must be preserved in both arms"
  ],
  "source_event_ids": ["SE_EV_0123"],
  "fixture_manifest": [],
  "notes": ""
}
```

### Case requirements

- `task` must be identical for baseline and candidate arms.
- `success_contract` must be frozen before either arm is graded.
- constraints must be applied equally to both arms.
- deterministic fixtures must be hashed/frozen.
- semantic held-out details must not be injected into candidate authoring.
- the case must exercise the actual changed decision/orchestration; irrelevant tasks cannot qualify a candidate.

---

## 15. Baseline snapshot

`prepare` must freeze the exact canonical files required for the candidate comparison.

At minimum:

- every proposed target card;
- every card in the bounded support/prerequisite bundle used to execute the target;
- relevant `MODULE.yaml` files needed for validation;
- metaskill prerequisites if they are part of the bounded execution bundle.

The baseline manifest records:

```json
{
  "relative_path": "software-engineering/core/example.md",
  "object_id": "SE_CORE_PATTERN_EXAMPLE",
  "sha256": "...",
  "role": "target"
}
```

The copied baseline cards live under `baseline/cards/` using their library-relative paths.

Before every state transition after `prepare`, the controller must verify that the canonical source files named in the baseline manifest still match their frozen hashes. If not, continuation stops with a baseline-drift error.

CRQ should not try to merge around that drift. Start a fresh run.

---

## 16. Candidate staging

`stage-candidate` copies the editable target cards from the baseline snapshot into `candidate/cards/`.

For a new card action, create only an empty destination directory plus an instruction entry in the generated operator brief. Do not generate fake card content in Python.

The acting human/model edits ordinary Markdown card files.

Candidate cards remain ordinary source-independent PASS objects. They must not contain CRQ run IDs, memory entry IDs, training event IDs, qualification case IDs, workspace paths, evidence hashes, or prose that depends on the empirical run remaining available. Empirical evidence justifies the authoring decision; it does not become a runtime dependency of the card.

### Candidate author brief

The generated `README.md` should expose:

- the compact `card_candidate` observation;
- its diagnosis and likely owners;
- the frozen assessment;
- author-visible target cases only;
- the baseline target cards;
- allowed object actions;
- the scope ceilings;
- the rule that held-out cases are intentionally withheld;
- the rule that library canon must not be edited directly.

It should **not** expose held-out semantic case details.

---

## 17. Candidate mutation accounting

Every candidate action must be explicit.

`controller/candidate_manifest.json`:

```json
{
  "schema_version": 1,
  "run_id": "SE_CRQ_0001",
  "changes": [
    {
      "action": "modify",
      "object_id": "SE_CORE_PATTERN_EXAMPLE",
      "relative_path": "software-engineering/core/example.md",
      "baseline_sha256": "...",
      "candidate_sha256": "...",
      "changed_sections": ["Pattern Rule", "Checklist"],
      "rationale": "..."
    }
  ],
  "unmatched_actions": [],
  "scope": {
    "changed_existing_cards": 1,
    "new_cards": 0,
    "deleted_cards": 0,
    "renamed_object_ids": 0,
    "moved_existing_cards": 0
  }
}
```

### 17.1 Applied actions

An intended object action whose expected baseline target exists and whose staged candidate produces a real byte/content change.

### 17.2 Unmatched actions

Examples:

- assessment says “revise PAT_X” but PAT_X is not in the frozen baseline;
- staged file is byte-identical despite a claimed modification;
- new-card action created no card;
- candidate file does not contain the claimed object ID;
- a file appeared that was never authorized by assessment.

Any unmatched action blocks `freeze-candidate` until corrected or the assessment is deliberately revised and re-frozen.

### 17.3 Rejected actions

CRQ itself does not partially keep/revert individual Markdown edits during authoring. Rejection occurs at the candidate/change-set level after qualification. The final report must still distinguish:

```text
applied-to-candidate
unmatched-before-qualification
rejected-by-qualification
accepted-for-synthesis-review
```

This provides the useful edit-accounting idea without importing text-anchor replacement semantics.

---

## 18. Candidate overlay validation

Before candidate freeze, CRQ must construct a temporary merged library tree:

```text
current frozen-compatible library
        +
replace target files with candidate files
        +
add candidate new files
```

Then run the ordinary validators against the overlay.

Minimum checks:

```bash
python PASS/tools/validate.py --library <overlay-library>
python PASS/tools/verify_references.py --library <overlay-library>   # add --library support if missing
```

If `verify_references.py` does not currently accept `--library`, either:

1. add the same explicit `--library` pattern used by `validate.py`, or
2. refactor its internal function to accept a library root and expose that through CRQ.

Do not special-case candidate cards around existing validation rules.

### Candidate freeze rejects

- any schema error;
- dangling relation/reference;
- domain coupling;
- object ID duplication;
- unauthorized extra changed file;
- deletion/move/rename;
- scope ceiling violation;
- placeholder/template tokens;
- changed baseline support card not authorized as a target;
- candidate bytes changing after freeze.

After successful validation, hash all candidate card files into `candidate.freeze.json`.

---

## 19. Execution model

CRQ v1 must **not** become a generic agent runner.

The controller administers evidence. The host/human/model performs the actual case using the appropriate existing mechanism:

- deterministic test/build command;
- Drill runner;
- Code Apprenticeship/field-test machinery;
- domain-specific evaluator;
- a fresh isolated model context for semantic cases.

CRQ provides result templates and validates/freeze-hashes returned evidence.

This keeps CRQ portable and avoids coupling PASS to an LLM backend.

---

## 20. Arm result schema

Each case has exactly one frozen baseline result and one frozen candidate result.

`cases/<case-id>/<arm>/result.json`:

```json
{
  "schema_version": 1,
  "case_id": "TARGET_001",
  "arm": "baseline",
  "verdict": "pass",
  "evaluation_mode": "semantic",
  "evaluator_relation": "separate",
  "executor": {
    "kind": "ai",
    "runtime": "...",
    "model": "..."
  },
  "criteria": [
    {
      "criterion": "Observable criterion 1",
      "result": "pass",
      "evidence": "artifact/output evidence reference"
    }
  ],
  "evidence_manifest": [
    {
      "path": "evidence/output.txt",
      "sha256": "...",
      "kind": "machine-output"
    }
  ],
  "invalid_reason": null,
  "notes": ""
}
```

### Allowed verdicts

```text
pass
fail
invalid
```

No `partial` result exists for candidate qualification.

### Evaluator relation

Allowed values:

```text
deterministic
separate
same-reader
```

Rules:

- deterministic cases use `deterministic`;
- semantic required qualification cases must use `separate`;
- `same-reader` may be retained only for exploratory/non-qualifying diagnostics and cannot satisfy a required semantic case.

### Arm symmetry

The controller must verify that baseline and candidate results for one case use:

- the same case definition hash;
- the same frozen fixture hash/manifest;
- compatible environment/toolchain metadata when the case depends on it;
- the same success criteria;
- the same declared constraints.

A mismatch invalidates the case comparison.

---

## 21. Contamination and isolation

Existing PASS contamination rules remain in force.

For semantic baseline/candidate execution:

- each arm should use a fresh context;
- the candidate arm must not inherit baseline answers;
- the baseline arm must not see candidate card content;
- the evaluator must grade the frozen arm artifact, not a summary written by the arm itself;
- held-out case details must remain unavailable to the candidate author until candidate freeze;
- confirmed cross-arm exposure invalidates the affected case and, when it compromises the batch, the run.

The controller should provide fields to record contamination state:

```text
none
suspected
confirmed
```

`confirmed` on a required case => invalid qualification.

### Held-out is a protocol boundary, not a security claim

CRQ does not pretend that a workspace directory is a hostile-process sandbox. “Held-out” means the candidate-author role is not given those case details and must not inspect them before candidate freeze. If an agent/human with filesystem access deliberately reads a held-out case early, record that as contamination and invalidate the affected qualification rather than claiming the controller prevented access.

A future host may add stronger process/filesystem isolation, but CRQ correctness must not depend on such a host feature existing.

---

## 22. Per-case delta algorithm

This logic must be deterministic and tested directly.

```python
if baseline == "invalid" or candidate == "invalid":
    delta = "invalid"
elif baseline == "fail" and candidate == "pass":
    delta = "improved"
elif baseline == "pass" and candidate == "pass":
    delta = "stable"
elif baseline == "pass" and candidate == "fail":
    delta = "regressed"
elif baseline == "fail" and candidate == "fail":
    delta = "persistent-fail"
```

There is no numeric score.

The result report records every case independently.

---

## 23. Final gate algorithm

CRQ must compute one of the following statuses:

```text
qualified-for-synthesis-review
rejected-regression
rejected-target-failure
invalid
inconclusive-no-improvement
inconclusive-protection-gap
blocked-by-synthetic-stress
```

### 23.1 Precedence

Evaluate in this order:

1. **Invalidity**
2. **Protected regression**
3. **Target failure**
4. **Synthetic stress block**
5. **Protection gap**
6. **Positive improvement requirement**
7. **Qualified**

### 23.2 Exact rules

#### Rule A — Invalid

If any required case has an invalid baseline or candidate arm, or the run has confirmed contamination, result is:

```text
invalid
```

No capability conclusion may be drawn from that case.

#### Rule B — Protected regression

If any required protected **non-synthetic** case is `regressed`:

```text
rejected-regression
```

This is a hard veto.

#### Rule C — Target failure

If any required target case leaves candidate at `fail`:

```text
rejected-target-failure
```

The candidate did not solve all changes it explicitly claimed as required.

#### Rule D — Synthetic stress

If any required synthetic case leaves candidate at `fail` or produces a `regressed` delta:

```text
blocked-by-synthetic-stress
```

The candidate cannot be qualified until the stress concern is resolved, replaced with a valid case, or deliberately removed by revising and re-freezing the plan before execution.

Passing synthetic cases contributes **zero** positive qualification evidence.

#### Rule E — Protection gap

If there is no required **non-synthetic** protected case and no deterministic regression suite that meaningfully protects established behavior:

```text
inconclusive-protection-gap
```

This is stronger than silently accepting an unprotected candidate.

#### Rule F — Positive improvement

At least one required target case with:

```text
origin != synthetic
positive_qualification_eligible == true
```

must have delta:

```text
improved
```

If all target cases are merely `stable`:

```text
inconclusive-no-improvement
```

A candidate can still be manually reviewed, but CRQ has not demonstrated that it improved the intended defect.

#### Rule G — Qualified

Only when all earlier rules are clear:

```text
qualified-for-synthesis-review
```

This status never edits canon.

---

## 24. Why CRQ does not use aggregate scoring

A weighted score can hide exactly the failure CRQ is meant to prevent.

Example:

```text
Case A: baseline fail -> candidate pass     (+1)
Case B: baseline pass -> candidate fail     (-1)
Case C: baseline fail -> candidate pass     (+1)
```

An aggregate optimizer may call that a net improvement.

CRQ must call it:

```text
rejected-regression
```

because established behavior in Case B was lost.

This is a deliberate architectural choice, not an implementation simplification.

---

## 25. Synthetic stress-case policy

Synthetic cases are useful for generating nearby variations such as:

- altered constraints;
- boundary values;
- paraphrased requests;
- swapped environment details;
- missing optional inputs;
- adversarial-but-valid orderings;
- equivalent representations.

But PASS must preserve the distinction:

```text
synthetic test success != demonstrated transfer
synthetic test success != empirical training result
synthetic test success != evidence_count increment
```

### 25.1 Creation

CRQ may generate a **stress-case brief**, but the controller itself should not call an LLM. The acting model/human writes the synthetic case and freezes it before execution.

### 25.2 Validation

Before a synthetic case can block qualification, its plan must state why it remains inside the card's intended condition/contract. A malformed or out-of-scope stress test should be removed by revising the plan, not “failed through.”

### 25.3 Memory

Never append a positive training-history event solely because a synthetic stress case passed.

A synthetic failure that reveals a real deterministic contract bug may motivate a deterministic regression and then a normal card candidate, but the durable evidence should be the reproduced contract failure, not “the dream said so.”

---

## 26. Evidence synthesis for large candidate histories

CRQ should support hierarchical synthesis without adding an LLM dependency.

### 26.1 Trigger

Default recommendation:

- 1–8 cited evidence events: direct review is acceptable.
- 9–24 events: hierarchical synthesis recommended.
- >24 events: hierarchical synthesis required before candidate authoring unless the user explicitly chooses direct review.

These are context-management defaults, not quality thresholds.

### 26.2 Model-neutral packetization

Add a controller command:

```text
prepare-synthesis
```

It reads the candidate entry's cited valid events and creates deterministic input batches under:

```text
synthesis/levels/0/batch-001/input.json
synthesis/levels/0/batch-002/input.json
...
```

Default leaf batch size: **6 events**.

Each leaf summary output must use:

```json
{
  "schema_version": 1,
  "claims": [
    {
      "claim": "...",
      "supporting_event_ids": ["SE_EV_001", "SE_EV_004"],
      "contradicting_event_ids": []
    }
  ],
  "persistent_failures": [],
  "stable_successes": [],
  "boundary_notes": [],
  "unresolved_conflicts": []
}
```

The validator can ensure only known input event IDs are cited; it cannot judge whether the prose is semantically faithful.

### 26.3 Recursive merge

Fan-in: **4 summaries per parent batch**.

Parent summaries cite child-summary IDs and ultimately preserve the leaf event IDs supporting each final claim.

No summary may erase a contradiction merely to produce a cleaner conclusion.

### 26.4 Failure-first visibility

When summaries contain persistent failures or contradictions, final synthesis must surface them before stable successes. This is presentation priority, not a numeric weighting system.

### 26.5 Final synthesis output

The final synthesis should answer:

- What behavior is repeatedly observed?
- What contradicts it?
- What boundaries are demonstrated?
- What is still unresolved?
- Which canonical owner(s) are plausible?
- Does the evidence suggest knowledge, orchestration, evaluation/practice, or non-canon failure?
- What minimal candidate change is justified?

This synthesis may inform `assessment.json`, but it does not itself authorize canon change.

---

## 27. Longitudinal comparison

CRQ v1 should implement longitudinal comparison at the **qualification-case level**, where the data is precise and version-bounded.

For each case, record:

```text
improved
stable
regressed
persistent-fail
invalid
```

This provides the useful “what changed across versions?” signal without inventing a permanent optimizer-version database.

### Deferred cross-run longitudinal store

Do **not** add a permanent global candidate-version ledger in v1.

If future experience shows a need to compare many accepted/rejected card revisions over months, design that separately. It must respect:

- no global registry without demonstrated need;
- memory's prohibition on hashes/session state;
- workspace disposability;
- canon remaining authoritative.

For now, durable behavior belongs in:

- training-history evidence events;
- compact `card_candidate` / learned-principle memory;
- deterministic regression tests after acceptance.

---

## 28. Interaction with Skillset Memory

CRQ should require **no memory schema change in v1**.

That is intentional.

The existing schema already contains the needed durable concepts:

- `card_candidate`
- `diagnosis.failure_layer`
- `likely_owners`
- `evidence_events`
- `evidence_count`
- `evidence_class`
- `status`
- `superseded_by`
- `last_verified`

### 28.1 Before CRQ

Evidence is compacted into a `card_candidate` entry using ordinary memory tooling.

Example:

```yaml
- id: SE_MEM_0042
  scope_type: pattern
  scope_id: SE_CORE_PATTERN_EXAMPLE
  type: card_candidate
  evidence_class: stochastic_performance
  observation: >
    The current rule appears to omit a reusable boundary condition needed when ...
  confidence: repeated
  status: active
  diagnosis:
    failure_layer: knowledge
    hypothesis: The existing Pattern condition is too narrow.
  evidence_count: 3
  evidence_events:
    - SE_EV_0101
    - SE_EV_0114
    - SE_EV_0123
  likely_owners:
    - SE_CORE_PATTERN_EXAMPLE
```

### 28.2 After rejected/inconclusive qualification

CRQ must not rewrite memory automatically.

It should emit a **memory disposition recommendation** in `synthesis/disposition.json`, for example:

```json
{
  "memory_entry_id": "SE_MEM_0042",
  "recommended_action": "keep-monitoring",
  "reason": "Candidate fixed the motivating case but regressed protected behavior."
}
```

Allowed recommendations:

```text
keep-active
keep-monitoring
narrow-boundary
supersede-candidate
resolve-after-canon-fix
obsolete
no-change
```

The human/model applies the actual memory update deliberately through `memory.py entry`.

### 28.3 After canonical acceptance

Once a reviewed candidate is deliberately integrated into `library/` and its fix holds:

- deterministic issue -> add/retain regression test, then resolve the memory candidate;
- stochastic issue -> keep candidate `monitoring` until appropriate fresh evidence verifies the changed card, then resolve or supersede;
- do not mark a memory candidate resolved merely because Markdown was edited.

---

## 29. Interaction with Code Apprenticeship field tests

`PASS/runtime/skillforge_code_study.py` remains the preferred software-domain mechanism for producing strong held-out evidence about cards.

CRQ should integrate by **consuming its memory results**, not by duplicating the field-test controller.

### 29.1 Existing field-test attribution remains authoritative for that run

Code Apprenticeship already distinguishes:

```text
skillcard
application
human-code
source-context
fixture
runtime-tool
unresolved
```

CRQ should not reinterpret an explicitly valid `application` result as a canon defect simply because a later model wants to edit the card.

### 29.2 Card repair path

Recommended software flow:

```text
held-out software field test
        ↓
valid FAIL attributed to exposed skillcard
        ↓
training_history event
        ↓
card_candidate memory entry
        ↓
CRQ candidate refinement
        ↓
fresh target + protected qualification cases
        ↓
qualified-for-synthesis-review
```

### 29.3 No causal overclaim

One Code Apprenticeship review still does not prove that PASS caused an improvement or that a card works universally. CRQ does not change that rule.

---

## 30. Pattern / AP / Drill repair routing

CRQ should require the assessment to name the intended canonical role.

### Pattern candidate

Use when the reusable **decision itself** is missing, wrong, or underspecified.

Typical actions:

- refine IF condition;
- correct THEN/ELSE action;
- add executable Do/Don't detail;
- add a boundary Variant when it remains the same decision owner.

### AP candidate

Use when the reusable **goal-directed orchestration** is missing or wrong while the underlying decisions may already exist.

Typical actions:

- reorder domain actions;
- add a missing orchestration step;
- add explicit stopping/branch behavior;
- coordinate existing Patterns that were being composed ad hoc repeatedly.

### Drill candidate

Use when the **practice/evaluation** itself is defective or a new repeatable qualification exercise is needed.

Typical actions:

- correct success checks;
- add a near-miss that excludes false success;
- repair setup so the target capability is actually exercised;
- add a repeatable Drill after a lesson has become suitable for practice.

### Do not repair canon for

- one-off executor disobedience;
- retrieval miss with correct available card;
- context continuity failure;
- broken tool/controller;
- invalid fixture;
- missing project/source context;
- unresolved attribution.

---

## 31. Proposed CLI

Implement one new controller:

```text
PASS/runtime/pass_candidate_qualification.py
```

### 31.1 `prepare`

```bash
python PASS/runtime/pass_candidate_qualification.py prepare \
  --domain software-engineering \
  --memory-entry SE_MEM_0042 \
  --out workspace/candidate-qualification/software-engineering/SE_CRQ_0001
```

Optional:

```text
--library <path>
--memory-root <path>
--max-changed-cards N
--max-new-cards N
```

`prepare`:

- validates memory store;
- resolves candidate entry and evidence;
- copies/hashes likely owner baseline cards;
- creates run structure;
- emits assessment template;
- sets state `prepared`.

### 31.2 `freeze-assessment`

```bash
python PASS/runtime/pass_candidate_qualification.py freeze-assessment \
  --run <run-dir>
```

Validates and freezes `controller/assessment.json`.

### 31.3 `prepare-synthesis` (optional before assessment freeze)

```bash
python PASS/runtime/pass_candidate_qualification.py prepare-synthesis \
  --run <run-dir>
```

Creates hierarchical evidence packets when desired/required.

### 31.4 `freeze-plan`

```bash
python PASS/runtime/pass_candidate_qualification.py freeze-plan \
  --run <run-dir>
```

Validates every case definition and freezes the qualification plan.

### 31.5 `stage-candidate`

```bash
python PASS/runtime/pass_candidate_qualification.py stage-candidate \
  --run <run-dir>
```

Copies editable baseline target cards to candidate staging and creates paths for authorized new cards.

### 31.6 `freeze-candidate`

```bash
python PASS/runtime/pass_candidate_qualification.py freeze-candidate \
  --run <run-dir>
```

- accounts for every expected change;
- builds temporary overlay;
- runs ordinary validators;
- hashes candidate files;
- rejects unmatched/unauthorized mutations;
- sets state `candidate-frozen`.

### 31.7 `open-execution`

```bash
python PASS/runtime/pass_candidate_qualification.py open-execution \
  --run <run-dir>
```

Creates result templates and reveals held-out case details to the execution/evaluation phase.

### 31.8 `freeze-execution`

```bash
python PASS/runtime/pass_candidate_qualification.py freeze-execution \
  --run <run-dir>
```

Validates all result files/evidence manifests, arm symmetry, evaluator relation, and contamination fields. Hashes results/evidence.

### 31.9 `evaluate`

```bash
python PASS/runtime/pass_candidate_qualification.py evaluate \
  --run <run-dir>
```

Computes per-case deltas and the deterministic final gate. Writes `qualification_result.json`.

### 31.10 `finalize`

```bash
python PASS/runtime/pass_candidate_qualification.py finalize \
  --run <run-dir>
```

Requires a completed synthesis/disposition review and freezes the run as `finalized`.

It still does **not** write `library/` or memory.

### 31.11 `status`

```bash
python PASS/runtime/pass_candidate_qualification.py status --run <run-dir>
```

Prints:

- state;
- baseline drift status;
- assessment status;
- candidate mutation counts;
- case counts by role/origin;
- missing results;
- current/final gate result if available.

### 31.12 `invalidate`

```bash
python PASS/runtime/pass_candidate_qualification.py invalidate \
  --run <run-dir> \
  --reason "..."
```

### 31.13 `abandon`

Marks a run intentionally stopped without making an evidence claim.

---

## 32. Controller implementation structure

Recommended functions/modules inside `pass_candidate_qualification.py` for v1:

```text
constants / schema sets
CandidateQualificationError
atomic write helpers
path containment helpers
hash helpers
load/save run
state transition checks
memory candidate resolution
baseline card resolution
baseline manifest verification
assessment validation
synthesis packet preparation / validation
plan validation
case validation
candidate staging
candidate mutation accounting
candidate overlay construction
candidate validation invocation
candidate freeze verification
result template creation
arm result validation
evidence manifest verification
contamination validation
execution freeze
per-case delta calculation
final gate calculation
qualification report generation
status rendering
CLI parser
main
```

If the file grows beyond maintainable size, split deterministic schema/manifest logic into:

```text
PASS/runtime/candidate_qualification/
    __init__.py
    controller.py
    schemas.py
    evidence.py
    gate.py
```

Do not split prematurely if one auditable controller file remains reasonable.

---

## 33. File-by-file repository changes

### New

#### `PASS/docs/CANDIDATE_REFINEMENT.md`

Canonical methodology document implementing this design in repo form.

It must include:

- canon/memory/history/regression relationship;
- defect attribution;
- candidate boundaries;
- qualification cases;
- no-regression rule;
- synthetic policy;
- final statuses;
- deliberate promotion boundary.

#### `PASS/runtime/pass_candidate_qualification.py`

Deterministic controller described above.

#### Tests

Use the repository's existing test placement convention available in the implementation checkout. If the canonical repo has a root `tests/`, use it. If not, place controller regressions in the existing workspace/runtime test location already used by PASS and ensure they are discovered by the project's actual validation command.

Suggested logical test modules:

```text
test_candidate_qualification_state.py
test_candidate_qualification_assessment.py
test_candidate_qualification_overlay.py
test_candidate_qualification_gate.py
test_candidate_qualification_synthetic.py
test_candidate_qualification_contamination.py
test_candidate_qualification_drift.py
test_candidate_qualification_synthesis.py
```

### Modify

#### `ARCHITECTURE.md`

Add CRQ as a **factory/runtime empirical refinement mechanism**, not canon and not a new object type.

Required statement:

> Candidate Refinement & Qualification stages bounded card changes outside canon, compares them against a frozen baseline, and may qualify a proposal for deliberate synthesis review. It never promotes memory or edits `library/` automatically.

#### `PASS/docs/MEMORY_SCHEMA.md`

No schema change required for v1.

Add a short cross-reference under card-candidate incubation explaining that a `card_candidate` may enter CRQ and that CRQ results still require deliberate memory disposition.

#### `PASS/docs/SOFTWARE_CARD_FIELD_TESTS.md`

Add the post-field-test repair path:

```text
valid skillcard-attributed evidence -> card_candidate -> CRQ -> fresh qualification -> synthesis review
```

Clarify that CRQ does not weaken held-out field-test evidence rules.

#### `PASS/docs/PASS_CONSUMPTION.md`

Add a brief note distinguishing ordinary use from CRQ qualification. Ordinary use should not accidentally create candidate qualification claims.

#### `README.md`

Add a concise “Refine a candidate card from empirical evidence” section with the CRQ command sequence.

#### `AGENTS.md` and `CLAUDE.md`

Add the same non-negotiable bold lead sentence to both if a new shared architecture rule is introduced. Example:

> **Candidate qualification never edits canon automatically.** A memory candidate may stage a bounded overlay and earn qualification for synthesis review, but only an explicitly approved delta changes `library/`.

Keep the shared lead sentence byte-identical if the repo's existing consistency test requires it.

#### `CHANGELOG.md`, `VERSION`, README version marker

Follow the repository's existing SemVer rule. Increment from the **then-current** beta version at implementation time; do not assume `beta.88` if the repo has advanced before integration.

---

## 34. Validator library-root support

Beta87 already exposes `--library <path>` on both `PASS/tools/validate.py` and `PASS/tools/verify_references.py`. CRQ should use those existing public CLI boundaries when validating a temporary candidate overlay rather than adding a candidate-specific validation path.

If later repository revisions refactor either validator, preserve the same capability: both validators must be callable against an explicit library root, and their default canonical-library behavior must remain unchanged.

---

## 35. Failure semantics

Every controller failure must belong to one of three categories.

### Administration error

Examples:

- malformed JSON;
- missing required file;
- wrong state transition;
- path escape;
- unknown object ID;
- candidate scope violation.

Result: command fails; run state unchanged.

### Invalid qualification

Examples:

- confirmed contamination;
- required case execution could not exercise the capability;
- arm fixture mismatch;
- semantic held-out grading not separate;
- environment mismatch that decides the result;
- unresolved required context.

Result: run may transition to `invalidated` or `qualification_result.status = invalid` depending on when discovered. It is not a candidate failure.

### Candidate failure

Examples:

- target still fails;
- protected behavior regresses;
- valid synthetic stress case fails.

Result: deterministic rejection/block status. Evidence remains inspectable.

---

## 36. Security and robustness requirements

### Path containment

All run paths, evidence paths, candidate paths, and case fixture paths must be resolved and verified inside their declared roots.

### Symlinks

Do not permit a candidate/evidence file to escape the run directory through symlink traversal. Reuse existing containment patterns where possible.

### Atomic writes

Write JSON/state atomically and read it back before claiming persistence.

### Hashes

Use SHA-256 for frozen workspace manifests, consistent with current PASS field-test patterns.

These hashes are workspace administration, not card/memory content.

### No arbitrary command runner

CRQ v1 must not accept arbitrary shell strings and execute them as a generic service. Execution stays with the caller/domain harness.

### No provider secrets

CRQ must never read `.env` LLM credentials or embed model-provider configuration.

### Stable JSON

Where hashes depend on generated controller JSON, serialize deterministically:

- UTF-8;
- sorted keys where appropriate;
- explicit indentation/newline convention.

Do not hash model-authored Markdown by reserializing it; hash file bytes.

---

## 37. Test plan

The implementation is incomplete until all of the following behavior is covered.

### 37.1 Preparation

- accepts a valid active `card_candidate`;
- rejects non-candidate memory entry;
- rejects resolved/superseded candidate;
- rejects missing evidence event;
- rejects invalid event;
- rejects quarantined event;
- rejects bad owner ID;
- refuses cross-domain owner coupling;
- freezes exact baseline bytes.

### 37.2 Assessment

- only `canon-candidate` can continue to candidate authoring;
- unresolved deciding question blocks freeze;
- canon candidate requires object action;
- skillcard owner must exist;
- invalid action type rejected;
- knowledge/orchestration routing guidance is preserved in generated brief.

### 37.3 Qualification plan

- requires target case;
- identifies protection gap;
- rejects synthetic case marked positive-qualification eligible;
- rejects held-out semantic case configured with same-reader qualification;
- freezes case hashes;
- hidden case details not included in author brief before candidate freeze.

### 37.4 Candidate mutation accounting

- expected modification detected;
- byte-identical “modification” is unmatched;
- missing expected file is unmatched;
- unauthorized added file rejected;
- delete rejected;
- move rejected;
- object ID rename rejected;
- default changed-card ceiling enforced;
- default new-card ceiling enforced;
- explicit recorded ceiling override works only for those two counts.

### 37.5 Overlay validation

- valid candidate overlay passes ordinary validator;
- invalid frontmatter fails;
- dangling reference fails;
- cross-domain relation fails;
- duplicate object ID fails;
- canonical library remains unchanged after validation;
- temporary overlay is removed after command, success or failure.

### 37.6 Drift

- changing a baseline target after prepare blocks continuation;
- changing a frozen support card blocks continuation;
- changing unrelated out-of-closure card does not falsely invalidate the run unless the candidate overlay depends on it;
- candidate modification after freeze blocks execution.

### 37.7 Arm results

- pass/fail/invalid accepted;
- partial rejected;
- missing evidence manifest rejected when required;
- evidence hash mismatch rejected;
- semantic required case with same-reader rejected;
- deterministic relation accepted for deterministic case;
- baseline/candidate case hash mismatch invalidates comparison;
- fixture mismatch invalidates comparison;
- confirmed contamination invalidates.

### 37.8 Delta table

Test all pairs:

| Baseline | Candidate | Expected |
|---|---|---|
| fail | pass | improved |
| pass | pass | stable |
| pass | fail | regressed |
| fail | fail | persistent-fail |
| invalid | pass | invalid |
| pass | invalid | invalid |
| invalid | invalid | invalid |

### 37.9 Final gate

- invalid beats every other status;
- one protected regression vetoes multiple target improvements;
- target failure rejects;
- synthetic stress failure blocks;
- no protected cases produces protection-gap status;
- all stable targets but no improved target produces no-improvement status;
- one eligible real/deterministic improved target + all protections stable -> qualified;
- synthetic improved target cannot satisfy positive requirement;
- aggregate “net win” can never hide a protected regression.

### 37.10 Synthesis

- packetization includes every cited valid event exactly once at leaf level;
- no unknown event ID accepted in summary support lists;
- recursive fan-in terminates for 1, 2, 3, 4, 5+ batches;
- contradictions remain representable;
- synthetic case results are never added to positive empirical evidence lists.

### 37.11 Persistence/state

- wrong-state command is no-op;
- interrupted atomic write leaves previous valid state;
- readback mismatch fails loudly;
- finalized run is read-only except status/reporting;
- invalidated/abandoned runs cannot resume.

---

## 38. Required end-to-end fixture tests

Create at least three end-to-end fixtures.

### Fixture A — clean Pattern repair

Baseline Pattern misses a deterministic boundary.

Expected:

```text
TARGET: baseline fail -> candidate pass
PROTECT: baseline pass -> candidate pass
FINAL: qualified-for-synthesis-review
```

Verify canon untouched.

### Fixture B — candidate fixes target but regresses existing behavior

Expected:

```text
TARGET_1: fail -> pass
TARGET_2: fail -> pass
PROTECT_1: pass -> fail
FINAL: rejected-regression
```

This is the critical no-aggregate-masking test.

### Fixture C — application lapse, not canon defect

Memory candidate/assessment evidence reveals existing exposed card already contains the correct guidance.

Expected:

```text
assessment candidate_disposition != canon-candidate
freeze-assessment may succeed as memory-only/fresh-retest
stage-candidate is refused
```

This demonstrates that CRQ protects canon from one-off execution mistakes.

---

## 39. Reporting

`qualification_result.json` should be machine-readable.

Example:

```json
{
  "schema_version": 1,
  "run_id": "SE_CRQ_0001",
  "status": "rejected-regression",
  "candidate_memory_entry": "SE_MEM_0042",
  "changed_objects": ["SE_CORE_PATTERN_EXAMPLE"],
  "case_deltas": [
    {
      "case_id": "TARGET_001",
      "role": "target",
      "origin": "empirical",
      "baseline": "fail",
      "candidate": "pass",
      "delta": "improved"
    },
    {
      "case_id": "PROTECT_001",
      "role": "protected",
      "origin": "empirical",
      "baseline": "pass",
      "candidate": "fail",
      "delta": "regressed"
    }
  ],
  "blocking_cases": ["PROTECT_001"],
  "positive_qualification_cases": ["TARGET_001"],
  "synthetic_cases": [],
  "canon_modified": false
}
```

Generate a human-readable `synthesis/report.md` from the deterministic result plus semantic reviewer comments.

Recommended report headings:

```markdown
# Candidate Qualification Report

## Candidate
## Why it was proposed
## Canon ownership assessment
## Changed cards
## Target cases
## Protected cases
## Synthetic stress cases
## Baseline vs candidate deltas
## Regressions
## Invalid or unresolved evidence
## Qualification status
## Recommended synthesis disposition
## Memory disposition recommendation
```

---

## 40. Deliberate synthesis review

CRQ stops at proposal qualification.

The final semantic reviewer decides among:

```text
accept candidate as canonical delta
revise candidate and run a fresh qualification
split candidate into smaller changes
redirect ownership to another Pattern/AP/Drill
retain lesson only in memory
add deterministic regression without card edit
reject as redundant
reject as false
reject as too narrow
```

### Acceptance rule

Even a `qualified-for-synthesis-review` result does not authorize copying files into `library/` by the controller.

The implementing agent may perform the ordinary approved library edit only when the user/maintainer has authorized that integration task under normal PASS repository rules.

After landing:

```bash
python PASS/tools/validate.py
python PASS/tools/verify_references.py
python PASS/tools/build_index.py
<repo test suite>
```

and perform the repository's normal version/changelog requirements.

---

## 41. Candidate retry policy

A rejected candidate must not be silently edited in place and re-evaluated under the same frozen candidate identity.

Recommended rule:

- assessment and plan may remain conceptually reusable;
- each materially revised candidate gets a new run ID or explicit `revision` child run referencing the predecessor;
- do not overwrite the old qualification result.

For v1, simplest implementation:

> **Every material candidate revision starts a new CRQ run.**

The new run may reference the prior run ID in free/admin metadata, but no permanent global run graph is required.

This keeps evidence easy to audit and avoids state ambiguity.

---

## 42. Cleanup policy

After a candidate is integrated or rejected and its durable lessons are handled:

- CRQ workspace may be deleted;
- accepted deterministic regressions live in the normal test suite;
- empirical evidence lives in training history;
- compact lesson/candidate status lives in Skillset Memory;
- canon lives in `library/`.

Do not retain CRQ scratch merely because it once existed.

If the user explicitly wants an evidence hold, preserve that run directory until released.

---

## 43. Compatibility

### Existing library

No card migration required.

### Existing memory schema

No migration required in v1.

### Existing training history

No rewrite required.

### Existing Code Apprenticeship studies

Remain valid/readable under their existing schema contracts.

### Existing releases

Unaffected. CRQ is authoring/factory infrastructure and does not ship in SkillForge runtime releases unless a future explicit decision says otherwise.

### Existing repo without `workspace/candidate-qualification/`

Directory is created lazily by the first run or by setup. No committed empty directory is required.

---

## 44. Versioning

This feature changes documented PASS factory/runtime behavior, so implementation must advance the root PASS Semantic Version according to the current repository policy.

Do not hardcode the design document's beta87 baseline as the release number. At integration time:

1. read current `VERSION`;
2. increment the beta prerelease suffix according to repository rules;
3. update README's current version marker;
4. add a dated changelog entry;
5. ensure `Unreleased` handling remains compliant.

---

## 45. Recommended implementation milestones

### Milestone 0 — Contract/documentation skeleton

Implement:

- `PASS/docs/CANDIDATE_REFINEMENT.md`;
- architecture cross-reference;
- no-auto-canon rule in AGENTS/CLAUDE if adopted;
- controller shell with state machine and `status`;
- run directory creation and atomic state writes.

Acceptance:

- no behavior beyond scaffolding;
- repo tests green;
- architecture wording unambiguous.

### Milestone 1 — Candidate intake and attribution

Implement:

- memory candidate lookup;
- valid-event verification;
- baseline owner resolution;
- `assessment.json` schema;
- `freeze-assessment`;
- candidate disposition routing.

Acceptance:

- application/tool/fixture cases cannot reach candidate staging;
- canon-eligible case can.

### Milestone 2 — Plan, staging, and overlay validation

Implement:

- qualification-plan schema;
- case schema;
- hidden/visible case handling in generated brief;
- candidate staging;
- mutation accounting;
- bounded scope;
- overlay library build;
- ordinary PASS validation against overlay;
- candidate freeze/drift checks.

Acceptance:

- invalid candidate cannot be frozen;
- library remains untouched.

### Milestone 3 — Execution evidence and no-regression gate

Implement:

- arm result schema;
- evidence manifests;
- semantic/deterministic evaluator rules;
- contamination fields;
- arm symmetry checks;
- per-case deltas;
- final gate statuses;
- machine/human reports.

Acceptance:

- protected regression always vetoes qualification;
- aggregate masking is impossible.

### Milestone 4 — Evidence synthesis

Implement:

- `prepare-synthesis`;
- leaf packetization;
- summary validation;
- recursive fan-in;
- contradiction preservation;
- final synthesis packet.

Acceptance:

- large evidence sets are reviewable without one giant prompt;
- every final claim remains traceable to valid event IDs.

### Milestone 5 — Field-test integration and polish

Implement:

- docs link from software field tests;
- README workflow;
- convenience reporting from Code Apprenticeship candidate results;
- end-to-end fixtures;
- cleanup guidance;
- final version/changelog release hygiene.

Acceptance:

- a real held-out card failure can flow cleanly from field test -> memory candidate -> CRQ -> synthesis review.

---

## 46. Definition of done

CRQ is complete only when all of the following are true:

1. A valid `card_candidate` can initialize a run.
2. Non-canon failures are prevented from entering candidate staging.
3. Baseline card bytes are frozen and drift-checked.
4. Candidate changes occur only outside `library/`.
5. Candidate scope is mechanically bounded.
6. Candidate overlays pass the ordinary PASS validators.
7. Held-out semantic cases remain hidden from candidate authoring until freeze.
8. Baseline and candidate results are independently frozen.
9. Every required case gets a per-case delta.
10. A single protected regression vetoes qualification.
11. Synthetic success never provides positive empirical qualification.
12. Invalid execution never becomes a candidate fail.
13. CRQ produces no automatic memory mutation.
14. CRQ produces no automatic canon mutation.
15. `qualified-for-synthesis-review` is the strongest controller outcome.
16. End-to-end regression fixtures cover qualified, regression-rejected, and non-canon-attribution paths.
17. Repository version/changelog/docs are updated under current PASS rules.
18. Full repository validation/test suite passes.

---

## 47. Rejected alternatives

### A. Import SkillOpt as a dependency

Rejected. PASS already has stronger object/evidence boundaries, and importing the package would bring incompatible assumptions about monolithic skill text, optimizer memory, model backends, and autonomous adoption.

### B. Copy SkillOpt source and rename it

Rejected. Reimplement the useful concepts in PASS-native code and contracts.

### C. Automatic edit of canonical cards after a winning gate

Rejected. Empirical evidence may qualify a proposal, not silently change canon.

### D. Weighted aggregate acceptance score

Rejected. It can hide regressions.

### E. Semantic-density quality bonus

Rejected. Keyword density is not instructional quality.

### F. Store every candidate revision permanently in Skillset Memory

Rejected. Memory is compact current learning/calibration, not a version-control ledger.

### G. Make synthetic tasks ordinary training evidence

Rejected. Synthetic success does not demonstrate real transfer.

### H. Build a generic LLM runner into CRQ

Rejected for v1. PASS should remain host/model neutral.

### I. Extend memory schema immediately with optimizer-specific fields

Rejected for v1. Existing `card_candidate`, `diagnosis`, `likely_owners`, and evidence linkage are sufficient.

---

## 48. Clean-room implementation note

SkillOpt was used only as an external source of design ideas to evaluate. The PASS implementation should be written against this document and the existing PASS contracts.

Do not:

- import SkillOpt modules;
- copy SkillOpt implementation code;
- reproduce its config surface for compatibility;
- use its file formats as PASS formats;
- preserve its “sleep/dream/gradient” terminology merely because the reference project used it.

PASS-native terms in this design are intentional:

```text
Candidate Refinement & Qualification
Defect assessment
Qualification plan
Target case
Protected case
Synthetic stress case
Per-case delta
No-regression gate
Synthesis review
```

---

## 49. Handoff instructions for Codex / Claude / local agents

When implementing this design against a repository newer than beta87:

1. Treat the current repo as canonical for paths and already-landed architecture changes.
2. Read targeted files before editing:
   - `ARCHITECTURE.md`
   - `AGENTS.md`
   - `CLAUDE.md`
   - `PASS/docs/MEMORY_SCHEMA.md`
   - `PASS/docs/SOFTWARE_CARD_FIELD_TESTS.md`
   - `PASS/docs/PASS_CONSUMPTION.md`
   - `PASS/tools/memory.py`
   - `PASS/tools/validate.py`
   - `PASS/tools/verify_references.py`
   - `PASS/runtime/skillforge_code_study.py`
3. Do not redesign PASS around this subsystem.
4. Preserve current closed schemas unless this design explicitly calls for a change.
5. Implement milestone by milestone; do not land a giant untested rewrite.
6. Keep deterministic controller logic separate from semantic model judgment.
7. Add tests before or with each gate/state transition.
8. Run targeted tests after each milestone and the full repository validation before integration.
9. Do not edit canonical library cards merely to demonstrate the controller.
10. Use synthetic test fixtures under tests/workspace for controller regression coverage.
11. Preserve all existing user-authored domain knowledge.
12. Follow the current repo's version/changelog/commit-note rules at integration time.

If the current repo conflicts with a path/name proposed here because later beta work moved a component, preserve the **behavioral contract** in this document and adapt the file location minimally. Do not create duplicate parallel infrastructure merely to keep the old proposed path.

---

## 50. Example end-to-end run

### Starting memory

```yaml
- id: SE_MEM_0042
  scope_type: pattern
  scope_id: SE_CORE_PATTERN_EXAMPLE
  type: card_candidate
  evidence_class: deterministic_contract
  observation: >
    The current Pattern omits a boundary condition that causes an unsafe fallback
    when the resource owner outlives the temporary view.
  confidence: provisional
  status: active
  diagnosis:
    failure_layer: knowledge
    hypothesis: The Pattern condition does not distinguish owning from non-owning lifetime.
  evidence_count: 1
  evidence_events:
    - SE_EV_0123
  likely_owners:
    - SE_CORE_PATTERN_EXAMPLE
```

### Prepare

```bash
python PASS/runtime/pass_candidate_qualification.py prepare \
  --domain software-engineering \
  --memory-entry SE_MEM_0042 \
  --out workspace/candidate-qualification/software-engineering/SE_CRQ_0001
```

### Assessment

Reviewer fills:

```json
{
  "candidate_disposition": "canon-candidate",
  "failure_layer": "knowledge",
  "primary_attribution": "skillcard",
  "owner_object_ids": ["SE_CORE_PATTERN_EXAMPLE"],
  "proposed_object_actions": [
    {
      "action": "revise",
      "object_id": "SE_CORE_PATTERN_EXAMPLE",
      "object_type": "pattern",
      "reason": "The missing lifetime distinction belongs to the reusable decision."
    }
  ],
  "unresolved_questions": []
}
```

Freeze it.

### Plan

Target:

```text
TARGET_001
real deterministic reproduction
baseline expected to expose the defect
```

Protection:

```text
PROTECT_001
existing ordinary owned-lifetime case
```

Stress:

```text
STRESS_001
synthetic nearby lifetime variation
```

Freeze plan.

### Candidate

Agent edits the staged Pattern only.

Candidate freeze:

- changed cards = 1;
- new cards = 0;
- no unauthorized files;
- overlay validates.

### Execute

Results:

```text
TARGET_001   baseline fail   candidate pass
PROTECT_001  baseline pass   candidate pass
STRESS_001   baseline pass   candidate pass
```

### Evaluate

Deltas:

```text
TARGET_001   improved
PROTECT_001  stable
STRESS_001   stable (synthetic, no positive credit)
```

Final:

```text
qualified-for-synthesis-review
```

### Synthesis review

Reviewer confirms the Pattern remains the correct owner and approves ordinary canonical integration.

Only **then** is `library/software-engineering/...` edited through the normal repository workflow.

The deterministic failure becomes a regression test. The memory candidate remains monitoring until the fix is verified as appropriate, then is resolved deliberately.

---

## 51. Example regression rejection

Results:

```text
TARGET_001   fail -> pass
TARGET_002   fail -> pass
PROTECT_001  pass -> fail
```

No score is calculated.

Final:

```text
rejected-regression
```

The report states that the candidate improved both motivating cases but broke established behavior protected by `PROTECT_001`.

The candidate may be redesigned in a fresh CRQ run. Canon remains unchanged.

---

## 52. Example execution-lapse routing

Evidence shows:

- the relevant Pattern was exposed;
- its existing rule directly covers the case;
- the executor ignored the rule and used the prohibited fallback.

Assessment:

```json
{
  "candidate_disposition": "memory-only",
  "failure_layer": "application",
  "primary_attribution": "application",
  "owner_object_ids": ["SE_CORE_PATTERN_EXAMPLE"],
  "proposed_object_actions": [],
  "rationale": "The canonical rule is already correct and sufficient; this run does not justify changing it."
}
```

`freeze-assessment` may freeze that diagnosis for recordkeeping, but `stage-candidate` refuses because the disposition is not `canon-candidate`.

That refusal is a feature. It prevents empirical noise from eroding correct canon.

---

## 53. Reference-idea translation matrix

This appendix exists only to make implementation intent obvious. It is not a compatibility requirement with the reference project.

| External idea reviewed | PASS-native CRQ implementation |
|---|---|
| distinguish skill defect from executor lapse | defect assessment + `candidate_disposition` before staging |
| optimize an existing skill artifact | bounded candidate overlay of ordinary Pattern/AP/Drill objects |
| train/validation split | motivating target cases separated from protected/held-out qualification cases |
| per-task no-regression option | mandatory protected-case veto in the final gate |
| bounded edit budget | explicit changed/new card ceilings and mutation accounting |
| applied/rejected/unmatched text edits | applied candidate actions, unmatched authorized actions, candidate-level qualification rejection |
| hierarchical patch merge | hierarchical evidence synthesis with event-ID traceability |
| synthetic/dream tasks | synthetic protected stress cases with zero positive empirical credit |
| slow/longitudinal update comparison | per-case baseline→candidate deltas (`improved`, `stable`, `regressed`, `persistent-fail`) |
| optimizer memory | existing PASS Skillset Memory + training history; no new store |
| automatic best-skill adoption | deliberately rejected; strongest result is `qualified-for-synthesis-review` |
| semantic-density bonus | deliberately rejected |

---

# Final architectural decision

Implement **Candidate Refinement & Qualification** as a PASS-native, model-neutral empirical refinement controller.

Its strongest guarantee is not “the optimizer found a better skill.”

Its guarantee is narrower and more defensible:

> A specific bounded candidate was compared against a frozen canonical baseline on explicit target and protected cases; invalid runs were excluded, protected regressions could not be hidden by aggregate scoring, synthetic success was not treated as empirical proof, and the resulting proposal is either blocked, rejected, inconclusive, or qualified for deliberate synthesis review.

That is the bridge PASS currently needs between evidence accumulation and safe canonical improvement.
