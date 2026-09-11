# Changelog

PASS follows [Semantic Versioning 2.0.0](https://semver.org/). This file records
user-visible changes to the PASS factory contract. Individual SkillForge
skillsets may evolve independently.

## Unreleased

### Added

- Added `learned_principle` as a first-class Skillset Memory type, separating a
  durable transferable lesson from the empirical result or event that supported
  it.
- Added domain-prefixed `workspace/handoffs/` documents to project snapshot and
  import scope while keeping them outside consumer releases.

### Changed

- Project snapshots now include canonical release recipes by default, and the
  importer carries the selected domain's matching recipe automatically.
- The Writing recipe now includes `writing/adventure-modules`.
- Limited the repository's public `workspace/` surface to reusable tools,
  canonical release recipes, and project handoffs. Existing local authoring
  material remains on disk but is no longer tracked.

### Validation

- Validated 1,771 canonical objects, all visual references, 197 generated
  indexes, and all four Skillset Memory stores (96 entries and 226 events).
- Passed all 168 repository tests, including every canonical release build and
  check.

## 1.0.0-beta.5 - 2026-09-08

### Added

- Added bounded cross-skill auxiliary fallback groups to release recipes. The
  builder resolves card-level relationship closure, preserves canonical card and
  asset bytes, regenerates release-local indexes, and excludes foreign-domain
  Skillset Memory.
- Added deterministic authority resolution for active release manifests: one
  complete owner provider wins, identical fallbacks coalesce, and differing
  fallbacks or multiple owners fail closed.

### Changed

- Advanced `RELEASE_MANIFEST.json` to schema 2 with owned domains, complete
  packaged object IDs, and explicit auxiliary group membership and paths.
- Made release checks validate auxiliary ownership, object and file membership,
  hashes, generated routing instructions, and owned-only memory.

### Validation

- Passed all 166 repository tests, including five new auxiliary packaging and
  authority-resolution tests plus every canonical release build and check.

## 1.0.0-beta.4 - 2026-09-07

### Added

- Added one generic, model-neutral Drill administrator for every current and
  future skillset. It discovers canonical Drill cards, prepares either blind
  cut, supports same-domain Drill chains, freezes produced answers before
  revealing grading material, validates complete criterion accounting, and
  exports Skillset Memory-compatible candidate events.
- Added fail-closed lifecycle checks for premature grader material, missing or
  empty answers, symbolic-link escapes, answer mutation after freeze,
  incomplete grades, invalid-run attribution, and cross-domain chains.
- Added shared lifecycle coverage for Game Design and Software Engineering,
  including a clean extracted-release run through prepare, freeze, reveal, and
  finalize.

### Changed

- Made Drill support capability-derived during release construction. A release
  containing canonical Drill objects now vendors `scripts/skillforge_drill.py`,
  declares that fact in `RELEASE_MANIFEST.json`, and receives portable and
  manual administration instructions in its generated `SKILL.md`; releases
  without Drills carry no unnecessary runner.
- Clarified that Drill administration standardizes evidence boundaries and
  stopping behavior without selecting a model or constraining how the taker
  reasons, solves, or uses its capabilities.
- Kept release-mode training append-free: finalization creates a reviewable
  candidate event inside disposable run state and never mutates packaged,
  read-only Skillset Memory.
- Required AI-authored merge and release commits to record what changed, what
  was intentionally excluded or preserved, validation performed, and any known
  issue left behind.

### Validation

- Validated 1,625 canonical objects and all reviewed visual references.
- Passed all 161 repository tests, including all four SkillForge release builds
  and checks and 15 focused Drill-administration tests.
- Confirmed discovery of 119 Art, 14 Game Design, 71 Software Engineering, and
  89 Writing Drills without a domain registry.

### Preserved boundaries

- The runner launches no models, sub-agents, repetitions, or comparative arms;
  model execution and any batch-wide sibling cancellation remain the host
  controller's responsibility.

## 1.0.0-beta.3 - 2026-09-07

### Added

- Added 27 Game Design Patterns from the completed D&D Basic source project:
  one Adventure Pattern, nine Character Patterns, five Foundation Patterns, and
  twelve Mechanics Patterns. They cover hybrid procedural construction,
  advancement and succession, mechanically causal identity, onboarding,
  persistent rules state, pressure and resource systems, causal randomness,
  injury, time, resolution scale, and extended processes.
- Added a Software Engineering card field-test protocol for reviewing one card
  against one real human-code slice, building a proof of concept, comparing the
  engineering decisions, gating active-project use, and stopping before another
  review.
- Distinguished neutral catalog-selected corpora, project-relevant references,
  and interest-led investigations, with a blank local-context template so one
  user's source choices cannot become public defaults or control data.
- Made field-test setup model-guided: code plus a practical goal is sufficient,
  catalogs are optional, and the model maintains any local context record.
- Separated maintainer card qualification from ordinary project use, recognized
  demonstrated defects in human review subjects as useful evidence, and scoped
  single-language results instead of treating them as proof that a core card is
  language-agnostic.
- Clarified that verified language coverage does not change ownership: reusable
  decisions remain in one shared core while language modules contain only their
  language-specific realization and exceptions.
- Added a dedicated Software Engineering Drill protocol that separates
  portability probes, blind sittings, deterministic regressions, and comparative
  studies.
- Added contamination stop conditions, single-pair checkpoints, and explicit
  sub-agent concurrency and run ceilings for empirical work.
- Added a derived SE Drill inventory command and a self-testing C++ Drill packet
  that exercises compile-success and expected-compile-failure evidence.

### Changed

- Revised 26 existing Game Design objects—five Adventure Patterns, one Character
  AP, one Character Drill, five Character Patterns, five Foundation Patterns,
  one Mechanics Drill, and eight Mechanics Patterns—to integrate the new
  decisions into existing design, calibration, onboarding, progression,
  resolution, and action-economy guidance.
- Regenerated the affected Game Design indexes. The package now contains 159
  validated objects.

### Safety and evidence

- Imported the returned Game Design project through the domain-only project
  boundary. Shared documentation, tools, root instructions, runtime code, and
  Python cache artifacts present in the archive were deliberately excluded as
  stale or out of scope.
- Reviewed the imported card delta after the archive passed card, reference,
  index, and Skillset Memory validation. No repository files were deleted by the
  import.

## 1.0.0-beta.2 - 2026-09-06

### Changed

- Generalized code-corpus measurement from hardcoded C and C++ handling to
  explicit C, C++, Go, Python, and Rust language profiles.
- Excluded conventional test files, Rust inline test modules, and testing
  frameworks' own assertion macros from production-code measurements while
  retaining qualified production assertion macros.
- Retired the obsolete Art pressure harness after blind Drills replaced its
  evaluation role.

### Evidence

- Reproduced the recorded C, C++, and Rust density baselines with the current
  instrument and named the corpora behind those figures.
- Recorded a new blind agent-authored corpus measurement, including the result
  that assertion density alone could not distinguish the compared samples.

## 1.0.0-beta.1 - 2026-09-06

First formal public beta. Earlier development was not assigned public SemVer
releases.

### Added

- Portable PASS authoring, schema, validation, memory, project-snapshot, import,
  runtime, and release-building workflows.
- Python-capable chat project snapshots for Art, Game Design, Software
  Engineering, and Writing.
- Self-contained SkillForge releases for all four current domains.
- Split AGPL-3.0-or-later and CC BY-SA 4.0 licensing, contribution guidance,
  attribution, project-name protection, and community support links.
- A documented Drill model for AI training and evaluation, with future
  AI-guided human teaching identified as a separate maturity target.

### Beta compatibility notice

The intended `1.0.0` public surface is now documented. Incompatible corrections
may still occur during beta, but they must receive a new prerelease version and
release notes. Published version contents are not replaced silently.
