---
object_id: PAT_select_rust_test_runs_by_scope_and_cost
object_type: pattern
name: Select Which Rust Tests to Run by Scope and Cost
library_path:
- software-engineering
- languages
- rust
- testing
stage_binding: 4 final
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- rust
- cargo
- testing
- filters
- ignored_tests
cross_links:
- rel: related_to
  target_object_id: PAT_isolate_rust_tests_for_parallel_execution
- rel: related_to
  target_object_id: PAT_place_rust_tests_by_the_boundary_they_validate
reference:
  source_title: Practical System Programming for Rust Developers
  author: Prabhu Eshwarla
confidence: medium
references: []
variants: []
---

# Select Which Rust Tests to Run by Scope and Cost

## Pattern Rule
**IF** a full `cargo test` run is slower than the feedback you need while iterating
**THEN** narrow a single invocation with a test-name filter, and keep the whole suite as the default verification step; reserve `#[ignore]` plus a separate `cargo test -- --ignored` invocation for cases that are routinely too expensive or too environment-restricted for the default loop.

## Do
- Treat the name filter as a substring match: one short argument re-runs every test whose name contains it, which is how one filter covers a whole related group.
- Pass harness flags after `--` so Cargo forwards them to the compiled test binary instead of consuming them itself.
- When several names must be matched at once, pass them as multiple filter arguments after `--`; Cargo itself takes at most one positional test name before the separator.
- Use `cargo test --no-run` to prove tests still compile after API changes without paying execution time.
- Schedule the `--ignored` run (for example in CI) so slow or environment-restricted cases still execute regularly.

## Don't
- Don't assume a filter is an exact test name; a substring silently runs more cases than one, and a typo silently runs none.
- Don't use `#[ignore]` to quarantine failing or flaky tests: it removes the case from the default run, so the regression sits unobserved until someone runs the ignored set.
- Don't lean on manual filtering as a permanent substitute for a fast default suite; filtering is iteration relief, not CI design.

## Checklist
- Does the default suite still run every non-ignored test, with narrowing used only for iteration?
- Is each `#[ignore]` justified by cost or environment rather than by current failure?
- Does some scheduled run execute the ignored cases?
- Are harness flags separated from Cargo's own flags by `--`?

## Notes
The two narrowing mechanisms change different things. A name filter narrows one invocation and leaves the suite's composition alone. `#[ignore]` rewrites the default composition itself, so it should be reserved for what a case costs or requires, not for its health.
