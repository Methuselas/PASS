# Changelog

PASS follows [Semantic Versioning 2.0.0](https://semver.org/). This file records
user-visible changes to the PASS factory contract. Individual SkillForge
skillsets may evolve independently.

## Unreleased

No changes yet.

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
