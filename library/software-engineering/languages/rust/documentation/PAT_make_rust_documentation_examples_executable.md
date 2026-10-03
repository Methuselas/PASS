---
object_id: PAT_make_rust_documentation_examples_executable
object_type: pattern
name: Make Rust Documentation Examples Executable
library_path: [software-engineering, languages, rust, documentation]
stage_binding: 4 final
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: PAT_define_your_code_contract_explicitly
tags: [rust, rustdoc, documentation, doctests, api_contract]
cross_links:
- rel: related_to
  target_object_id: PAT_place_rust_tests_by_the_boundary_they_validate
- rel: related_to
  target_object_id: PAT_build_dependency_documentation_for_the_selected_cargo_graph
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
references: []
variants: []
---

# Make Rust Documentation Examples Executable

## Pattern Rule
**IF** a public Rust API needs an example that teaches callers how to use it
**THEN** put the smallest realistic use in a rustdoc code block and run documentation tests in the normal verification path so the example must keep compiling and behaving as claimed.

## Do
- Document the caller-visible purpose, inputs, output, and important preconditions before showing code.
- Make the example exercise the public path an external caller should use, including the needed imports and ordinary error handling.
- Add `# Examples` when an example clarifies normal use, and document relevant `Panics`, `Errors`, or `Safety` contracts where they exist.
- Use hidden rustdoc setup lines only to remove distracting scaffolding; keep the essential call and assertion visible.
- Run documentation tests with the package and feature set whose public contract is being published.

## Don't
- Don't paste an example that is excluded from compilation merely because keeping it current is inconvenient.
- Don't let the example reach through private modules or rely on repository-local state a downstream caller cannot reproduce.
- Don't claim that one happy-path doctest covers edge cases, failure behavior, or unsafe invariants that need focused tests.
- Don't hide a required precondition in prose far from the call that depends on it.

## Checklist
- Does the example use the intended public path from a caller's viewpoint?
- Can rustdoc compile and run it under the supported feature configuration?
- Is the assertion strong enough to prove the behavior the prose promises?
- Are panic, error, and safety conditions documented where callers need them?
- Do broader unit or integration tests cover behavior the compact example omits?

## Notes
Rust documentation examples can serve two audiences at once: they are copyable usage guidance and executable checks against API drift. A passing doctest proves the shown path and behavior still work; it does not replace the rest of the test strategy.

