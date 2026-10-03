---
object_id: PAT_place_rust_tests_by_the_boundary_they_validate
object_type: pattern
name: Place Rust Tests by the Boundary They Validate
library_path: [software-engineering, languages, rust, testing]
stage_binding: 4 final
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: PAT_keep_tests_agnostic_to_implementation
tags: [rust, testing, unit_tests, integration_tests, public_api]
cross_links:
- rel: related_to
  target_object_id: PAT_dont_expose_privates_for_testing
- rel: related_to
  target_object_id: PAT_test_important_behaviors_beyond_public_api
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
references: []
variants: []
---

# Place Rust Tests by the Boundary They Validate

## Pattern Rule
**IF** a Rust test validates focused behavior inside one module and needs module-local setup
**THEN** keep it in a `#[cfg(test)]` child module beside that code.
**ELSE** put public-contract and multi-module behavior in an integration test under `tests/`, where it must use the crate as an external caller would.

## Do
- Let unit tests inherit the module's privacy boundary for focused setup and observation, while still preferring behavior-level assertions over direct checks of incidental helper functions.
- Use integration tests to prove that exported paths, visibility, types, and coordinated behavior work from outside the library crate.
- Treat each top-level Rust file under `tests/` as an independent test crate with its own imports and process entry into the library.
- Put shared integration-test helpers in a submodule such as `tests/common/mod.rs`, then declare that module from each test crate that needs it.

## Don't
- Don't widen production visibility merely so an integration test can reach an implementation detail.
- Don't use the fact that a unit-test child module can access private items as a reason to freeze every private helper with direct tests.
- Don't place a helper as a top-level file under `tests/` when Cargo would discover it as another integration-test target.
- Don't rely only on unit tests when the public API, crate boundary, or interaction among modules is the behavior that can break.

## Checklist
- Is this case validating one module's focused behavior or the crate's externally usable contract?
- Would the test still be valuable after private helpers were renamed or reorganized?
- Does every integration test compile using only the API an external crate can reach?
- Are shared helpers below a module path rather than accidentally discovered as empty test crates?

## Notes
Rust supplies two deliberately different viewpoints. An inline test child module is compiled only in test configuration and can share its parent's module context. A file under `tests/` is compiled as a separate crate, so it detects missing exports and unusable public paths that an internal test cannot see. The placement decision is therefore about the boundary being proved, not simply about keeping tests near or far from the code.

