# PASS — Skillset Memory Schema (closed contract)

status: active
owner: docs/domains/spec
last_reviewed: 2026-09-11

Skillset Memory is the portable **compact current state of the skill**. It keeps
durable learned principles distinct from empirical training results, strengths,
weaknesses, boundaries, and other self-calibration. `training_history.jsonl` is
the event record showing what happened in specific attempts. Skillset Memory is
not canon, not a runtime, not a transcript, and not a fourth object type.

**Every rule in this file that can be checked mechanically is checked by
`PASS/tools/memory.py validate`.** Rules are written here once so the tool has a
specification; they are not enforced by asking a model to remember them.

Memory reads the memory tree and, when linkage is present, the history beside
it. It never looks for a source document, a page, a chat transcript, or any
record of the conversation that produced an entry.

---

## 1. The firewall

```text
CANON        what decision to make, how to orchestrate it, how to practise it
             Patterns / APs / Drills. Source-independent. Stable.

MEMORY       what the skill currently carries forward
             Learned principles and calibrated empirical results, kept distinct.
             Compact. Provisional. Allowed to be revised or superseded.

HISTORY      what happened in specific attempts and evaluations
             Empirical. Append-oriented. Includes runs that proved nothing.

REGRESSION   what must never happen again under deterministic conditions
             Tests. Not memory's job.
```

Four rules follow, and the tool enforces the ones that can be checked:

1. **Memory never mutates canon.** A memory entry may nominate owners. Only a
   reviewed, approved delta changes a card.
2. **Memory is never inlined into canon.** If an entry seems important enough to
   apply on every turn, that is evidence it has earned promotion review — not a
   reason to copy it into a card or an entrypoint. Copying it there creates a
   second write site and lets the real owner atrophy. Checked by
   `tests/test_memory.py`.
3. **Memory never substitutes for a regression test.** Once a behavior is a
   deterministic invariant, enforce it in canon, the resolver, or a test. An
   entry that exists so the runtime will behave correctly when it is retrieved
   is a workaround, because retrieval is not guaranteed (§3).
4. **Memory is not a ledger.** No source ids, page numbers, hashes, receipts,
   attestations, reading progress, or session state. See §8.

## 2. Admissibility — the gate that matters most

A **training result or other performance claim** is evidence about a capability
only if the run that produced it was a valid test of that capability. A
`learned_principle` records the durable lesson retained from evidence; it does
not turn that lesson into a claim of demonstrated execution or transfer.

```text
execution
    ↓
VALIDITY CHECK        was this a valid test of the thing it appears to measure?
    ↓
observation           what was seen
    ↓
diagnosis             why it may have happened; may change later
    ↓
consolidation         only valid evidence reaches compact memory
```

A run is **invalid** when it failed before the target capability was exercised.
Recorded causes so far include an unreachable edit source, a controller that
bypassed its own mode, a package intentionally absent from the distribution, a
reference declared but never routed, a request blocked at a tool guardrail, an
underspecified prompt, and a missing prerequisite foundation.

The vocabulary of causes is **open**. Record what happened; do not force it into
a taxonomy. What is closed is the gate itself:

```yaml
validity: valid | invalid
invalid_reason: <short free-text label, required when invalid>
```

**The invariant:**

> An event marked `invalid` may remain in raw history. It must never increment
> `evidence_count` on a compact entry, and must never be cited for or against a
> craft capability.

`memory.py compact` refuses to count invalid events. `memory.py validate`
rejects a compact entry whose cited evidence includes one.

Invalid runs are worth keeping. They are the evidence that a controller, tool,
package, or prompt needs work — attributed to that owner, not to craft.

## 3. Presence is not consultation

The retrieval order in the doctrine describes an **intended** sequence, not an
enforced one. No runtime can guarantee that memory is read. An entry may be
correct, current, well-scoped, and never loaded, with no error and no signal.

```text
memory exists  ≠  memory validates  ≠  memory was retrieved  ≠  memory influenced execution
```

Two consequences:

- Do not claim an entry influenced behavior because it existed. `memory.py
  query` emits the ids it returned so a run can record what was actually
  consulted; absent that record, consultation is unproven.
- Do not compensate by inlining (§1 rule 2). The compensation destroys the path
  it protects: once the content is in an always-loaded file, the retrieval path
  stops being exercised and its decay becomes invisible.

## 4. Persistence

**The authoritative writable working state is the persistence target.** A git
checkout, an extracted skill package, or a domain authoring bundle may each
serve. Git is one implementation and is never required — this matches
`ARCHITECTURE.md` contract 4, where a clean chat or Project is a first-class
environment and a repo is optional.

The invariants are the same in every environment:

```text
approved            ≠  written
reported written    ≠  verified written
verified written    =  the target reopens and contains the expected state
```

**Post-write readback is a contract, not a courtesy.** After any writeback,
reopen the target and confirm the expected state is present before claiming
persistence. `memory.py append`, `memory.py compact` and `memory.py entry` read their target back
and fail loudly if it does not contain what they just wrote.

**Entries change through `memory.py entry`.** `add`, `update` (a null value
removes an optional key) and `supersede` (which can add the replacement in the
same write) validate the whole resulting store before writing, so a refused
write changes nothing. Writes are atomic, serialized per domain by a lock under
`memory/.locks/`, and splice only the changed entries, so untouched entries keep
their exact text. There is deliberately no delete (§7). Editing the YAML by hand
is a recovery action, followed by `memory.py validate`.

Session observations are not memory until writeback occurs. Until then the
honest phrasing is *observed in the current session*.

## 5. `skill_memory.yaml` — compact current state

One file per domain, at `memory/<domain>/skill_memory.yaml`.

Schema version 2 adds `specialization_profile` and `card_candidate`. The tooling
continues to read and validate version-1 stores so separately maintained domain
archives can merge without a synchronized migration. A version-1 store may not
use the two version-2 entry types; migrate that store to version 2 when either is
needed.

```yaml
memory_schema_version: 2
skillset: art
memory_version: 3
entries:
  - id: ART_MEM_001
    scope_type: topic
    scope_id: hands_and_object_contact
    type: recurring_failure
    evidence_class: stochastic_performance
    observation: >
      Compact lesson or self-knowledge the skill now carries forward.
      It should remain useful after the specific evidence is forgotten.
    confidence: provisional
    status: active
```

### Required keys

```yaml
id:              stable id, unique within the file
scope_type:      skillset | ap | pattern | drill | training | topic | runtime
scope_id:        object_id for canonical scopes; readable slug for topic/runtime
type:            learned_principle | recurring_failure | successful_tendency | known_boundary | training_result | specialization_profile | card_candidate
evidence_class:  stochastic_performance | deterministic_contract
observation:     compact retained lesson or self-observation; factual, self-contained, and not a transcript
confidence:      provisional | repeated | strong
status:          active | monitoring | resolved | superseded | obsolete
```

`evidence_class` is required because the promotion threshold depends on it
(§7). Every other key below is optional.

`learned_principle` records a durable craft or design lesson that should be
remembered and applied later. It is the transferable conclusion retained from
evidence, not the evidence itself. `training_result` records the compact outcome
of an actual exercise, evaluation, comparison, grade, detector run, playtest, or
other observed use. It answers what happened when something was tested.
`successful_tendency`, `recurring_failure`, and `known_boundary` record other
forms of empirical self-calibration. `specialization_profile` records how far a
general skill has actually transferred into a named subcategory or specialization
without assuming that broad competence propagates automatically. `card_candidate`
records a provisional reusable principle that appears important enough to watch
but does not yet have enough independent evidence, execution proof, or ownership
clarity to justify canon change. The supporting event trail remains in
`training_history.jsonl`.

### Optional keys

```yaml
diagnosis:
  failure_layer:  knowledge | orchestration | retrieval | application | continuity |
                  reference | tool | interface | training
  hypothesis:     current explanation; may change without rewriting observation
boundary:         where the observation was verified and where it was not
evidence_count:   integer ≥ 1
evidence_events:  list of event_id from training_history.jsonl
evidence_origin:  list of runtime_self_audit | user_feedback | human_teaching |
                  training_benchmark | regression_failure | book_close_training |
                  cross_model_test
likely_owners:    list of object_id or free-text owner labels
interventions:    list of { training | drill, isolation_result, retention_result,
                  transfer_result } — each result: improved | partial | unchanged |
                  failed | untested
retrieval_cues:   list of strings used by `memory.py query`
runtime_scope:    generic | free-text label for one execution environment
superseded_by:    id of the entry that replaced this one
last_verified:    YYYY-MM-DD
```

### Evidence origins

`human_teaching` means direct technical instruction or clarification supplied by
the human during study or training. It is distinct from `user_feedback`, which
is the user's assessment of a produced result. Human teaching may support a
provisional learned principle, but it is not automatically a user preference,
is not canonical doctrine, and is not by itself proof of execution, retention,
or transfer.

### Self-containment

> An entry must be valid and applicable after the conversation that produced it
> is gone.

This is `CLAUDE.md` rule 1 — a card must execute after its source is gone —
applied to memory. An observation reading *"see the earlier project chat for
details"* is incomplete. Conversation references may survive as optional
authoring provenance; never as a runtime dependency.

## 6. `training_history.jsonl` — event evidence

One JSON object per line, at `memory/<domain>/training_history.jsonl`.
Append-oriented: correct by adding a superseding event, not by rewriting a line.

```json
{"event_id": "ART_EV_0001", "date": "2026-08-22", "task": "…", "validity": "valid",
 "scope_id": "hands_and_object_contact", "delivery": "unknown",
 "observations": ["…"], "baseline": "…", "isolation": "improved",
 "retention": "untested", "transfer": "untested", "notes": "…"}
```

### Required keys

```json
event_id   stable id, unique within the file
date       YYYY-MM-DD
task       what was attempted
validity   valid | invalid
```

`invalid_reason` is required when `validity` is `invalid`.

### Optional keys

```json
scope_id        what the event is about
event_kind      performance (default) | metadata_correction | evidence_correction
delivery        how the skill reached the runtime; "unknown" recorded honestly
                beats the field omitted
run_type        portability-probe | blind-drill-sitting |
                deterministic-regression | comparative-study |
                software-card-field-test
program_purpose skillset-improvement; current Drill evidence qualifies and
                repairs PASS rather than claiming persistent learner-memory or
                model-weight changes
training_stage  qualification | baseline | practice | isolation | retention |
                transfer; records the one stage this event actually measured
taker           optional structured learner profile copied from the run:
                learner_id, learner.kind (human | ai), and runtime.name are
                required; an AI taker may record model.name; revision,
                capabilities, accommodations, generation settings, and other
                learner-specific fields remain nested data
intervention    the named teaching intervention and its declared components:
                Drill Instructions, exact Pattern/AP card IDs, and/or external
                material
lessons         transferable non-pass lessons; each names the Drill criterion,
                application or exposed-skillcard cause, mistake, correction, and
                prevention; it never names the current taker as the weakness
observations    list — one run may yield several independent observations
                rather than one global verdict
baseline / isolation / retention / transfer
                improved | partial | unchanged | failed | untested
                Record a stage only if it actually ran. "untested" is the
                honest default and the tool will not infer otherwise. These are
                learner-progress measurements, never card-qualification verdicts.
artifact_quality / process_validity / skill_attribution
                strong | adequate | weak | failed | unproven — scored
                independently, because a run can produce a strong artifact
                through an invalid process with no proof the skill contributed
notes           free text
```

### Append-only corrections

When a landed event names the wrong model, runtime, setting, date detail, or
other factual metadata, append a non-evidence correction instead of editing the
old line or pretending the correction exercised a capability:

```json
{"event_id":"SE_EV_9999","date":"2026-09-15","task":"Correct model metadata for an earlier sitting","validity":"valid","event_kind":"metadata_correction","supersedes_events":["SE_EV_9998"],"corrections":{"taker.model.revision":"Q4_K_M"}}
```

`supersedes_events` must name earlier events, and `corrections` records the
replacement facts. A metadata correction may not carry observations, training
stage or run-type labels, a taker profile, lessons, quality scores, or
attribution; those replacement facts belong inside `corrections`. It cannot be
cited by compact memory and is omitted from the uncited-performance review queue.

When a later audit finds that an event was not valid evidence for the capability
it claimed, append an `evidence_correction` instead of deleting or silently
rewriting history:

```json
{"event_id":"SE_EV_9999","date":"2026-09-15","task":"Correct the evidence classification of an earlier batch","validity":"valid","event_kind":"evidence_correction","supersedes_events":["SE_EV_9997","SE_EV_9998"],"corrections":{"disposition":"quarantined","reason":"The skillcards under test were not exposed.","replacement_outcomes":{"SE_EV_9997":"fail","SE_EV_9998":"invalid"}}}
```

Its `disposition` is `quarantined`; its reason is explicit; and any
`replacement_outcomes` map only superseded events to `pass`, `fail`, `invalid`,
or `not-applicable`. A quarantined event remains in raw history but cannot be
cited, compacted, or returned as uncited evidence. The correction itself is also
non-evidence.

### What an event is not

An authoring action is not a training event. `memory.py append` refuses events
whose task describes card authoring, commits, validation runs, index generation,
or archive creation.

```text
Drill authored  ≠  Drill executed  ≠  isolation success  ≠  retention  ≠  transfer
```

A training-stage name is not a result. A qualification or practice event leaves
all four measurement fields untested. A baseline event records only `baseline`;
an isolation, retention, or transfer event records only its matching field. The
model-neutral Drill runner enforces this for events it exports. Historical or
manually authored events remain the repository owner's responsibility.

Training evidence improves two things without merging them. Run metadata may
name the human or model so the conditions can be reproduced, but compact memory
does not preserve a weakness profile for that taker. A valid application miss is
rewritten as a transferable lesson: the mistake, the correction, and how to
prevent it. That lesson can help every later agent or person using the skillset.

A Pattern or AP may be named as the likely cause only after that exact card was
exposed in the declared intervention; a blind sitting cannot diagnose unseen
teaching material. Promote a card repair only when the frozen evidence shows the
card was defective, then requalify it on a fresh case. When the card was sound
and the application was not, preserve the general correction lesson in Skillset
Memory rather than writing that a named model failed.

Skillset Memory is PASS's evidence-informed memory about the domain skillset. It
is not a private memory store for the human or AI taker. `program_purpose` remains
`skillset-improvement` during this stabilization phase; future model-owned memory
requires its own explicit design and must not be inferred from these events.

Never record a stage that did not run.

Card qualification is stricter than learner-progress measurement. Every required
criterion is graded `pass` or `fail`, and the whole card or bundle passes only
when every criterion passes. If setup, tooling, contamination, or missing
evidence prevents that judgment, the sitting is `invalid`. `partial` is never a
qualification result.

## 7. Promotion, lifecycle, compaction

### Two thresholds

```text
stochastic_performance    repeated evidence, then retention, then transfer
deterministic_contract    one clear reproduction may justify a candidate fix
```

After a deterministic contradiction is fixed, the rule belongs in canon, the
resolver, or a test. The entry moves to `resolved` and stops being retrieved.

### Lifecycle

```text
active      currently believed and retrieved
monitoring  believed but under retest, or the owning card changed
resolved    the underlying issue was fixed and the fix held
superseded  replaced by another entry; set superseded_by
obsolete    the environment changed and the observation no longer applies
```

Only `active` and `monitoring` entries are returned by `memory.py query`.
Resolved history stays in the file; it stops biasing the runtime.

### Specialization profiles

A `specialization_profile` answers **where has this skill actually demonstrated
transfer?** It is not a separate score system and must not infer mastery from the
parent skillset. Scope it to a readable specialization such as fiction, poetry,
encounter design, environment art, backend engineering, or another meaningful
subcategory. Strengthen or narrow it as valid exercises, evaluations, field tests,
or mentor-to-production transfer accumulate.

### Card-candidate incubation

A `card_candidate` answers **what possible canonical lesson is accumulating
evidence but is not ready yet?** It preserves a reusable hypothesis without
forcing premature Pattern/AP/Drill creation. Keep the observation generalized,
source-independent, and self-contained; record supporting events rather than
source locators. Use `likely_owners` to name plausible existing owners when known.

A candidate may accumulate evidence and move from `provisional` to `repeated` or
`strong`, but **evidence never promotes it automatically**. Sufficient evidence
triggers deliberate synthesis review. That review may: (1) create a new card,
(2) add a Variant or refinement to an existing owner, (3) conclude that existing
canon already covers the lesson, (4) retain the lesson only inside a specialization,
or (5) reject it as false, redundant, or too narrow. After disposition, mark the
candidate `resolved`, `superseded`, or `obsolete` as appropriate and point to a
replacement with `superseded_by` when one exists.

A `card_candidate` whose likely owners are exact object ids may enter Candidate
Refinement & Qualification (`CANDIDATE_REFINEMENT.md`), which compares a bounded
card change against the current canon on frozen target and protected cases. CRQ
needs no schema change and never writes memory: its result is only a memory
disposition recommendation, which is applied deliberately through `memory.py
entry`. A qualified candidate is not resolved until the approved change has landed
and its fix holds; synthetic stress results never become evidence here.

### Compaction

```text
raw events  →  periodic synthesis  →  one compact entry
```

Raw history is preserved. Compact entries may be merged, strengthened,
narrowed, resolved, superseded, or re-scoped. Evidence is never deleted to make
a conclusion look cleaner.

### Retrieval

Canon resolves first; memory is retrieved second and bounded. Memory never
chooses the AP.

```text
request → canonical routing → owners → bounded memory → execute
```

When several entries match, prefer exact AP/Pattern/Training scope over
topic scope over skillset scope; then `active` over `monitoring`; then stronger
confidence; then more recent `last_verified`.

## 8. What memory must not store

```text
source ids, page numbers, locators, hashes, receipts, attestations
reading progress, unit maps, next-unit pointers, authoring checkpoints
current workflow or stage position, temporary artifact candidate/branch status
temporary activation left by a recent operation
recently produced artifacts, ambient conversation context
transcripts, full conversations, every user comment
book summaries, verbatim or full canonical text already in cards
generic advice copied wholesale from a Pattern, workflow order copied wholesale
from an AP, or practice procedure copied wholesale from a Drill
user-specific preferences — those belong to a future User Memory layer
```

Nothing becomes Skillset Memory except by explicit writeback of a **compact,
generalized current state**. A learned principle captures what should transfer
forward from evidence; an empirical result captures what testing actually
showed. Temporary state is not memory however durable it feels. The generalized
lesson such state reveals may become memory; the state itself never does.

Memory may overlap conceptually with canon when it records **how this skill has
learned, internalized, struggled with, or calibrated** a principle. It must not
duplicate full card text or become the authoritative instruction source. Canon
says what to do; Skillset Memory says what the skillset has learned about doing
it across retained evidence.

```text
NOT memory:  rejected thumbnail #6; candidate status; current stage
IS  memory:  broad Stage 0 rejection repeatedly causes the runtime to polish
             the rejected geometry instead of reopening search
```

Where a host provides its own memory facility, that facility occupies the
handoff and user-preference layer. Skillset Memory stays repo-backed and travels
with the skill. Do not write craft-performance observations into a host-provided
user-scoped store.

The validator rejects entries carrying keys from the retired authoring
vocabulary (`source_id`, `session_id`, `current_stage`, `unit`, `next_unit`,
`parent_gen_id`, and similar).

## 9. Seeding

An empty valid memory system is better than a populated contaminated one. There
is no requirement to populate on day one.

When seeding from retained history:

- prefer execution, Drill, failure-test, critique, and repair evidence;
- reject invalid craft attribution (§2);
- keep deterministic defects that were fixed in tests and history, not in active
  memory;
- normalize every seed into this schema rather than copying it verbatim from
  wherever it was recovered;
- never infer an event that was not recorded.

---

## 10. Schema version 3 — the claim

status: validation shipped; runtime dispatch is not wired yet. The sections
above remain the live contract for the four v1/v2 stores until each domain
migrates independently and the legacy path is retired. A v3 store is accepted
by `validate_v3_contents` / `validate_v3_store` in `PASS/tools/memory.py`;
`memory.py validate` will route to them when dispatch lands, and a live v1/v2
store is never routed here early.

The unit of a v3 store is the **claim**: one learned proposition that changes
what the next relevant task does. There is no status, no liveness field, and no
non-retrievable state — a claim that is no longer current is removed from the
store, and `memory_version` counts store revisions only; it is never read to
allocate or order a claim id.

### Store shape

```yaml
memory_schema_version: 3
skillset: <domain>
memory_version: <positive integer>
claims:
  - <claim>
```

No other top-level key is permitted. `skillset` must equal the containing
directory name and must be one of the four claim-domain tokens (`art`,
`game-design`, `software-engineering`, `writing`); an unmapped domain is an
error naming the token table, never a guessed token.

### Claim schema

```yaml
- id: <DOMAIN_TOKEN>_MEM_<26-char Crockford base32>   # required, generated once, opaque
  claim: <string>                         # required, ≤75 words
  claim_class: conduct | reach            # required
  claim_kind: deterministic | stochastic  # required
  confidence: provisional | repeated | strong   # required
  delta:                                  # required
    kinds: [<delta_kind>, ...]            #   required, 1..3
    statement: <string>                   #   required, ≤50 words
  envelope:                               # required
    holds_in: [<string>, ...]             #   required, ≥1, each ≤40 words
    not_shown_in: [<string>, ...]         #   required, ≥1, each ≤40 words
    conditions: [<string>, ...]           #   optional, each ≤40 words
  provenance: [<provenance>, ...]         # required, ≥1
  scope: <snake_case slug>                # required, matches [a-z][a-z0-9_]*
  retrieval_cues: [<string>, ...]         # required, ≥1
  last_verified: <YYYY-MM-DD>             # required
  canon: [<object_id>, ...]               # optional, 1..5 when present
  evidence: [<event_id>, ...]             # optional, 1..3 when present
  revalidate_after: <YYYY-MM-DD>          # optional, not earlier than last_verified
  contradicts: [<claim_id>, ...]          # optional, ≥1 when present
```

No other key is permitted on a claim. Closed vocabularies:

```text
claim_class   conduct | reach
claim_kind    deterministic | stochastic
confidence    provisional | repeated | strong
delta.kinds   action | judgment | verification | posture | application_limit
provenance    human_teaching | user_feedback | runtime_self_audit
              | training_benchmark | source_study | regression_failure
```

`provenance` is **required and valid** on a v3 claim. The legacy
`FORBIDDEN_KEYS` list rejects `provenance` for v1/v2 entries and History
events; the v3 path has its own `CLAIM_FORBIDDEN_KEYS` list, which carries the
retired authoring vocabulary plus the migration-lineage keys (`legacy_id`,
`migrated_from`, `source_entry`, `previous_id`) and deliberately excludes
`provenance`. The two rejection lists are never merged.

`book_close_training` is renamed `source_study`; `cross_model_test` is dropped
(its one use migrates to `training_benchmark`). Neither legacy value is a v3
member.

### The rule table

Two channels. **ERROR** makes the store invalid; **FLAG** leaves it valid and
marks it for review — `review` surfaces flags, and a flags-only result exits
zero. Every error message ends with its rule id in parentheses, e.g. `(C1)`.

| # | Rule | Type |
|---|---|---|
| S1 | `memory_schema_version` is exactly `3` | ERROR |
| S2 | no unknown top-level key; no unknown claim key (a legacy-only key such as `type`, `status`, `evidence_count`, `runtime_scope`, or `superseded_by` is unknown here) | ERROR |
| S3 | every required key present and non-empty | ERROR |
| S4 | every closed-vocabulary value is a member of its vocabulary | ERROR |
| S5 | `id` matches `<DOMAIN_TOKEN>_MEM_<26 Crockford base32 chars>` with this store's token; an unmapped `skillset` is an error naming `CLAIM_DOMAIN_TOKENS` | ERROR |
| S5a | `id` unique within the store | ERROR |
| S5b | across the stores a caller supplies, no `id` appears in two of them | ERROR |
| S6 | `skillset` equals the containing directory name | ERROR |
| S7 | `memory_version` is a positive integer (+1 per successful write is the writer's contract) | ERROR |
| S8 | `last_verified` and `revalidate_after` are ISO `YYYY-MM-DD`; `revalidate_after` is not earlier than `last_verified` | ERROR |
| S9 | `evidence` 1..3 when present; `canon` 1..5; `delta.kinds` 1..3; `contradicts` ≥1 | ERROR |
| S10 | `scope` matches `[a-z][a-z0-9_]*` | ERROR |
| C1 | `claim` at most 75 words | ERROR |
| C2 | `claim` 50 words or more | FLAG (fusion smell) |
| C3 | each envelope item at most 40 words | ERROR |
| C4 | `delta.statement` at most 50 words | ERROR |
| C5 | `delta.kinds` has 3 members | FLAG (fusion smell) |
| C6 | `claim` contains an accretion connective (`further showed`, `also showed`, `then showed`, `additionally demonstrated`) | ERROR |
| E1 | `holds_in` and `not_shown_in` both present with ≥1 member | ERROR |
| E2 | no `not_shown_in` member is a sentinel evasion (`n/a`, `none`, `unknown`, `everywhere`, `no limits`) | ERROR |
| R1 | when `claim_class: reach`, `delta.kinds` is a subset of `{posture, verification}`; a reach claim may still carry `canon` | ERROR |
| L1 | retired authoring vocabulary and migration lineage rejected as keys anywhere on a claim | ERROR |
| L2 | claim and envelope prose contain no conversation deference | ERROR |
| L3 | claim and envelope prose contain no model or agent identity token | ERROR |
| L4 | claim and envelope prose contain no learner/evaluator identity or bare specimen grade | ERROR |
| L5 | no field carries machine-, host-, session-, or toolchain-local state | FLAG |

The word caps are closed: a cap reopens only on contradictory evidence from a
real migration, not on a repeat of the completed sample study.

Referential integrity — canon resolution (`I1`/`I2`), evidence admissibility
against History (`I3`/`I4`/`I5`), and contradiction symmetry (`I6`) — is
validated when that work lands; a v3 store must validate standing alone with
no History and no library present.

### What v3 validation deliberately cannot check

Stated so no future implementer mistakes silence for permission:

- whether the stated delta is **real** against this skill + Canon + no Memory;
- whether the claim merely confirms that Canon worked;
- whether the claim is portable or craft-scoped;
- whether `confidence` is honest;
- whether the claim is genuinely one claim;
- whether a contradiction should resolve, and how.

All six are semantic judgment. Scripts own structure, accounting, and (once
wired) referential integrity. Nothing else.
