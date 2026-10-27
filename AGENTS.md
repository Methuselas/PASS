# PASS Agent Instructions

PASS turns studied sources into self-contained cards. `PASS/` is the portable
authoring skill; `library/` holds the finished cards; releases must be
self-contained.

## Route before reading

Do not preload `ARCHITECTURE.md`, PASS docs, master indexes, domain
cards, or memory just because the repo is open. Identify the operation first,
then use the matching skill description under `.agents/skills`:

- source study, card/module maintenance, validation, and release packaging
  use the PASS-authoring skill and only the active phase's references;
- domain practice, evaluation, or production uses the matching domain skill,
  `metaskills`, and a bounded set of relevant domain cards;
- repository code, tests, tooling, and architecture use the
  software-engineering skill and targeted files.

Skill descriptions own discovery; read `ARCHITECTURE.md` only for architectural
decisions or conflicts.

## Non-negotiable boundaries

Each rule's **bold lead sentence is shared verbatim with `CLAUDE.md`** and a
test enforces that the two files state the same set. The prose after each lead
is this file's own.

- **Source authoring runs through `PASS/pass.py`.** Start before source access,
  select the authorized domain, and finish one unit through all three passes and
  verified landing. Preflight runs once per source and waits for explicit,
  hash-bound user acceptance; unattended runs follow only `PASS/source.py drive`.
  See `PASS/docs/AUTHORING_RUNTIME.md`.
- **A card must be valid and executable after its source is gone.** No card
  carries a source id, locator, page number, hash, receipt, or attestation.
- **Author in one domain per run.** Every `library/` package other than
  `metaskills` is independent. Do not inspect, synchronize with, or modify
  another domain to author yours. Duplicate-guard against your own domain
  only;
  card IDs are unique library-wide.
- **Cards may reference their own package plus `metaskills`.** Any other
  cross-package reference fails validation.
- **Do not rebuild the retired authoring infrastructure.** Ledgers, source
  staging, provenance receipts, attestations, source projections, state
  sidecars, and a shared Teaching lane are retired; see the end of
  `ARCHITECTURE.md`.
- **Never widen the schema to accommodate a card.** A card that disagrees with
  its template is the card's bug.
- **Do not modify the Art Stages.** Art's staged-drawing material is frozen
  until the user explicitly asks to revise it.
- **`.claude/` and `.agents/` are repo discovery only.** They must never ship as
  runtime dependencies of a release.
- **Indexes are generated, never hand-edited.** Run `build_index.py`; an index
  that cannot be deleted and regenerated from the cards has become a second
  database.
- **`archive/` is retired material.** Nothing active may depend on it.
- **Workspace files have a task owner, a purpose directory, and a cleanup condition.**
  Use existing purpose buckets, never loose files. After verified integration,
  remove task-owned scratch and redundant staging copies; preserve evidence
  holds, original inputs, and other tasks; check exact deletion targets. See
  `PASS/docs/PASS_RUN.md` §Workspace lifecycle.
- **Project archives go directly in `workspace/project-releases/`; skill releases go in the SkillForge repository.**
  Resolve from the PASS root; use `PASS-project-<domain>.zip` without version
  subfolders unless asked. See `PASS/docs/MODULE_RELEASES.md` §Maintainer
  destinations.
- **Every release ships `metaskills` and its complete prerequisite closure.** A
  build that omits a referenced card is broken even when the source validates.
- **Do not add a global registry, repo-wide index, or new architectural
  convention without explicit authorization.** Nor a permanent root-level tool.
- **A hardcoded path left by an earlier agent is technical debt, not
  architecture.**
- **Front matter may not set a source's subject.** A preface, foreword, or
  introduction is orientation only; the subject is what the body teaches. A preface to instructors is metadata about the preface, not
  evidence that a craft book is pedagogy.
- **A session boundary never creates a unit boundary.** Units are set by
  instruction; context exhaustion is a separate problem. When a unit does not
  fit the remaining window, checkpoint and resume it — never split it to fit.
- **Practice history must not enter cards.** What one attempt revealed about
  application, calibration, or failure is not canonical knowledge. Attribute a
  failure before authoring: a missing reusable decision may justify a Pattern,
  a missing reusable action orchestration an AP; retrieval, application,
  continuity, reference, tool, and interface failures do not.
- **Skillset Memory separates evidence from what the skill learned; it is never canon and never overrides canon.** Current state lives in `memory/<domain>/` as **claims**, `conduct` or `reach`. A claim is current by presence; retirement is removal, `confidence` is maturity, never derived. `training_history.jsonl` preserves events. Cards stay authoritative; memory may motivate promotion review, never replace its owner.
- **An invalid run is never evidence about a capability.** If the run failed
  before the capability was exercised, record it in `training_history.jsonl`
  with a reason and the failing tool, controller, or package. It never
  counts toward a craft weakness. See `PASS/docs/MEMORY_SCHEMA.md`.
- **Contamination terminates an empirical batch.** Confirmed exposure across
  treatment and control, inherited answers, shared artifacts, or broken measurement
  stops every active and queued sibling run. Preserve artifacts for
  diagnosis, mark the batch invalid, never retry without new explicit approval.
  Suspected contamination pauses new launches until resolved.
- **Sub-agent work has a declared concurrency and run ceiling.** An ordinary
  Drill uses one taker; a comparative pilot may use one treatment/control pair,
  at most two sub-agents at once. More runs require approval naming the exact
  count, model, maximum concurrency, and stopping condition; finish and report
  each pair before launching another.
- **Candidate qualification never edits canon automatically.** Only an approved
  delta changes `library/`.
- **AI-authored merge and release commits require explanatory notes.** The body
  must state what changed, what was excluded or preserved, which validation
  ran, and known issues left behind. Never an empty or title-only
  message for integration work.
- **Every PASS commit advances the Semantic Version.** Update `VERSION`, the
  `README.md` current version, and the matching dated `CHANGELOG.md` entry in
  the same commit; in public beta, increment the numeric prerelease suffix.
  The suite checks the working tree against `HEAD` and committed work against
  its first parent; release builds reject substantive `Unreleased` notes.

## Validation

Use the tools in `PASS/tools/`. Scope routine content work to the changed
package; reserve repo-wide validation and the root suite for canonical
promotion or PASS/runtime/schema/generator/test architecture changes.

```bash
python PASS/tools/validate.py --package art --verify-references
python PASS/tools/build_index.py --package art --check

# Full boundary: source completion, release, tooling changes
python PASS/tools/validate.py --verify-references
python PASS/tools/build_index.py --check
python -m unittest discover -s tests -p "test_*.py"
```

Do **not** run the root suite after a card-only unit change, or regenerate
unrelated `SkillForge_*.yaml` recipes during card-only source runs; a recipe
changes only when module membership or release semantics changed.

Skillset Memory's tool reads `memory/` only:

```bash
python PASS/tools/memory.py validate
python PASS/tools/memory.py query --domain art --cues hand
python PASS/tools/memory.py append --domain art --task "..."
```

A release build is publishable only when schema, visual-reference,
asset-resolution, and portability gates pass. Run the root suite after
architecture/tooling/schema changes and repository-wide promotion gates,
not after routine card-only landing.
