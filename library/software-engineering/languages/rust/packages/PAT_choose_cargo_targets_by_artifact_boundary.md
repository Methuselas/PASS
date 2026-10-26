---
object_id: PAT_choose_cargo_targets_by_artifact_boundary
object_type: pattern
name: Choose Cargo Targets by Artifact Boundary
library_path:
- software-engineering
- languages
- rust
- packages
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- rust
- cargo
- targets
- packages
- libraries
- binaries
- examples
- tests
- benchmarks
cross_links:
- rel: related_to
  target_object_id: PAT_keep_rust_binary_logic_in_a_library_for_integration_tests
- rel: related_to
  target_object_id: PAT_keep_cargo_workspace_members_dependency_explicit
reference:
  source_title: Practical System Programming for Rust Developers
  author: Prabhu Eshwarla
confidence: medium
references: []
variants: []
---

# Choose Cargo Targets by Artifact Boundary

## Pattern Rule
**IF** one Rust package must produce or exercise artifacts with different caller or execution boundaries
**THEN** model those boundaries as Cargo targets—library, binary, example, integration test, or benchmark—and rely on Cargo conventions unless an explicit target declaration is needed

## Do
- Use a library target for code intended to be called by other Rust code and binary targets for executable entry points.
- Let one package contain multiple binary targets when they share one package identity and dependency contract but need distinct executables.
- Use example, integration-test, and benchmark targets for artifacts whose purpose is demonstration, verification, or measurement rather than product delivery.
- Move to multiple packages and a workspace only when ownership, publication, dependency, or independent-build boundaries become real.

## Don't
- Do not force unrelated executable purposes through one main target simply to avoid multiple targets.
- Do not duplicate target configuration in Cargo.toml when conventional target discovery already expresses the intended artifact.
- Do not split one coherent package into workspace members solely because its source tree grew.

## Checklist
- What artifact or caller boundary does each target represent?
- Can Cargo discover the target conventionally, or is an explicit name, path, or target-specific setting actually required?
- Does reusable logic live in a library surface when other targets need to call it?
- If the package was split, is there a real ownership, publication, dependency, or independent-build reason?

## Notes
Cargo target kinds are build-and-execution contracts, not just directory labels. A package can contain a library, multiple binaries, examples, integration tests, and benchmarks; package and workspace boundaries solve broader ownership and dependency problems.
