---
object_id: PAT_build_dependency_documentation_for_the_selected_cargo_graph
object_type: pattern
name: Build Dependency Documentation for the Selected Cargo Graph
library_path:
- software-engineering
- languages
- rust
- tooling
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- rust
- cargo
- documentation
- dependencies
- api
cross_links:
- rel: related_to
  target_object_id: PAT_keep_cargo_lock_under_cargo_and_version_control
reference:
  source_title: The Rust Programming Language
  author: Steve Klabnik and Carol Nichols
confidence: medium
references: []
variants: []
---

# Build Dependency Documentation for the Selected Cargo Graph

## Pattern Rule
**IF** you need API guidance for the dependency versions selected by a Rust project
**THEN** build and open the project's local dependency documentation with `cargo doc --open`
**ELSE** use online documentation for discovery, but verify its crate version before applying signatures or examples to the local graph.

## Do
- Run the command from the package or workspace whose manifest and lockfile select the dependencies you are using.
- Navigate to the dependency crate in the generated documentation rather than assuming that an API remembered from another release is present.
- Rebuild the documentation after changing dependency versions when the API question depends on that change.
- Use the trait and type documentation to identify required imports, method providers, bounds, and return types before changing code by trial and error.

## Don't
- Don't copy an example from the newest hosted documentation into a project pinned to an older incompatible crate without checking the selected version.
- Don't treat documentation generation as proof that your target builds; follow it with the Cargo check, test, or build that exercises your code and configuration.
- Don't infer a method belongs directly to a type when its documentation says a trait supplies it; the trait may need to be in scope.

## Checklist
- Did Cargo generate documentation from the intended manifest and dependency graph?
- Does the displayed crate version match the version selected for the project?
- Did the API page identify the trait, type, and return value needed by the call?
- Did the project pass the appropriate compiler or behavior gate after the documentation-guided change?

## Notes
Dependency APIs move independently of remembered examples and of whatever a documentation website currently shows by default. Building documentation through the project converts the lockfile's selected graph into a browsable reference, tightening the link between the API being read and the code Cargo will compile.

