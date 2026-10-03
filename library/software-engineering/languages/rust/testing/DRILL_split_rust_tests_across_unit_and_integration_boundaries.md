---
object_id: DRILL_split_rust_tests_across_unit_and_integration_boundaries
object_type: drill
name: Split Rust Tests Across Unit and Integration Boundaries
library_path: [software-engineering, languages, rust, testing]
stage_binding: 4 final
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, testing, unit_tests, integration_tests, cargo]
cross_links:
- rel: teaches
  target_object_id: PAT_place_rust_tests_by_the_boundary_they_validate
- rel: teaches
  target_object_id: PAT_keep_rust_binary_logic_in_a_library_for_integration_tests
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
target_skill: assigning Rust tests to module-local, crate-external, and process boundaries
references: []
variants: []
---

# Split Rust Tests Across Unit and Integration Boundaries

## Practice Task
Restructure a small Rust binary package so focused module tests, public-library integration tests, shared test helpers, and process-entry behavior each run at the boundary they claim to validate.

## Target Skill
Assigning Rust tests to module-local, crate-external, and executable-process boundaries without widening production visibility.

## Setup
Start with a Cargo binary package whose `main` contains reusable logic, two inline tests, and one top-level integration-test helper file that Cargo discovers as an empty test target.

## Instructions
1. List the behaviors under test and classify each as module-local, public library contract, or process-entry behavior, recording the reason for every classification.
2. Move reusable production logic into `src/lib.rs` behind a coherent public capability, then keep `src/main.rs` as a thin caller of that library path.
3. Keep focused module cases in a `#[cfg(test)]` child module without making a private helper public solely for the test.
4. Move public-contract cases into one or more files under `tests/`, importing the package library exactly as an external crate does.
5. Move shared integration-test setup below a module path such as `tests/common/mod.rs`, declare it from the test crates that use it, and record the discovered test targets before and after the move.
6. Run the complete suite, then run one integration-test target by name and record both commands and summaries.
7. Break one exported behavior and capture the integration-test failure; restore it, rename a private helper, and confirm the behavior-level tests pass unchanged.

## Success Check
- Every case has a recorded boundary classification and a reason tied to what it proves; sorting by preferred file location without a boundary reason is the plausible near-miss.
- The binary calls the same library capability exercised by integration tests, and the reusable behavior is not duplicated between targets.
- No production item is made public solely so a test can call it, demonstrated by renaming a private helper without editing behavior-level tests.
- The shared helper no longer appears as its own empty integration-test target, while the test crates that declare it still compile and use it.
- The complete suite and a named integration-test target both run, and the intentionally broken exported behavior is observed failing before restoration.
- Any process-entry behavior left in `main` is named explicitly with either a process-level check or a reason it is only inert wiring.

## Common Failures
- Moving files without changing the boundary the tests actually exercise.
- Exposing private helpers instead of shaping a useful library capability.
- Creating `tests/common.rs` and accepting the extra empty test target as harmless noise.
- Testing the library while leaving a second copy of the real logic in the binary.

## Notes
This exercise teaches Rust test placement and the library-target seam together. A green suite is not sufficient: the discovered targets, import boundary, intentional failure, and helper rename show whether the tests actually occupy the boundaries their filenames imply.

