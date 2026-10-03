---
object_id: PAT_use_cargo_check_during_rust_iteration
object_type: pattern
name: Use cargo check During Rust Iteration
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
- compilation
- feedback
- iteration
cross_links:
- rel: related_to
  target_object_id: PAT_keep_the_build_green_with_an_automated_smoke_test
reference:
  source_title: The Rust Programming Language
  author: Steve Klabnik and Carol Nichols
confidence: medium
references: []
variants: []
---

# Use cargo check During Rust Iteration

## Pattern Rule
**IF** you need compiler and type-system feedback while changing a Rust project but do not yet need a runnable artifact
**THEN** run `cargo check` for the fast validation loop
**ELSE** use `cargo run` when execution is the check, or `cargo build` when you need the produced binary or library artifact.

## Do
- Run the command from the package or workspace whose manifest owns the code being changed, so Cargo evaluates the intended targets and dependency graph.
- Keep the fast compile-check loop separate from behavioral verification. Follow it with the tests or execution that can observe the behavior you changed.
- Remember that stopping before full code generation is both the speed advantage and a limit: some diagnostics appear only during code generation, so a successful check does not guarantee that a later build will succeed.
- Move to `cargo build` or `cargo run` deliberately when the question changes from “does this compile?” to “does the artifact link and behave correctly?”
- Read diagnostics as the output of the selected toolchain; wording and warning details may change even when the underlying program remains compatible.

## Don't
- Don't repeatedly produce an executable merely to learn whether a local edit type-checks when `cargo check` answers that question sooner.
- Don't treat a successful check as proof that the program starts, accepts its inputs, links every environment-dependent component, or produces the expected result.
- Don't use a direct `rustc` invocation as the routine project check when Cargo owns the manifest, dependencies, features, and targets.

## Checklist
- Did the command use the manifest and target set that own the changed code?
- Did `cargo check` finish without compiler errors?
- Did a separate behavioral check run when the change affected runtime behavior?
- If an executable or distributable artifact was required, was `cargo build` or the appropriate Cargo command run afterward?

## Notes
The speed advantage comes from avoiding final artifact production and much of full code generation. That makes the command a good inner-loop gate, but the same boundary explains what it cannot establish. Compile validation, artifact production, and behavioral verification are three different questions; choosing the cheapest command that answers the current one keeps feedback quick without inflating its meaning.
