---
object_id: PAT_keep_rust_binary_logic_in_a_library_for_integration_tests
object_type: pattern
name: Keep Rust Binary Logic in a Library for Integration Tests
library_path: [software-engineering, languages, rust, testing]
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: PAT_design_for_testability
tags: [rust, testing, binary_crates, library_crates, architecture]
cross_links:
- rel: related_to
  target_object_id: PAT_place_rust_tests_by_the_boundary_they_validate
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
references: []
variants: []
---

# Keep Rust Binary Logic in a Library for Integration Tests

## Pattern Rule
**IF** a Rust package ships an executable whose important behavior should be exercised through integration tests
**THEN** place that behavior in the package's library target and keep the binary target as a thin adapter that calls it.
**ELSE** leave truly process-entry-only wiring in the binary and test it at the process boundary when its behavior matters.

## Do
- Move parsing-independent rules, transformations, and coordination behind public library functions or types that integration tests can import.
- Keep `main` responsible for process concerns such as collecting arguments, selecting streams, mapping exit status, and invoking the library entry point.
- Exercise the library through `tests/` for crate-boundary confidence, and add a process-level test only for behavior that belongs specifically to the executable shell.
- Make the public library surface reflect useful application capabilities rather than exposing private helpers one by one.

## Don't
- Don't bury all application behavior in `src/main.rs`; a binary target is not an importable library API for ordinary integration tests.
- Don't duplicate logic in a test-only library facade while production continues to use a different implementation.
- Don't assume a tiny `main` needs no verification when argument, environment, stream, or exit-code mapping is itself important behavior.

## Checklist
- Can integration tests import and exercise every important non-process-specific behavior?
- Is the binary entry point small enough that its remaining responsibilities are explicit?
- Does production call the same library path the integration tests exercise?
- Are process-boundary behaviors tested at that boundary rather than misrepresented as library behavior?

## Notes
Cargo can build a package with both library and binary targets, but only the library supplies an API another crate can import. Moving reusable behavior into that target creates one production path that both the executable and integration tests call. The thin binary is an adapter, not a second implementation.

