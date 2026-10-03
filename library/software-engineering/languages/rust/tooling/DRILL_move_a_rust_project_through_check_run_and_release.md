---
object_id: DRILL_move_a_rust_project_through_check_run_and_release
object_type: drill
name: Move a Rust Project Through Check Run and Release
library_path:
- software-engineering
- languages
- rust
- tooling
stage_binding: 2 block
lane_fit: teach
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- rust
- cargo
- build_profiles
- practice
cross_links:
- rel: teaches
  target_object_id: AP_bootstrap_a_rust_project_with_cargo
- rel: teaches
  target_object_id: PAT_use_cargo_check_during_rust_iteration
- rel: teaches
  target_object_id: PAT_build_and_benchmark_rust_in_release_mode
reference:
  source_title: The Rust Programming Language
  author: Steve Klabnik and Carol Nichols
confidence: medium
references: []
variants: []
target_skill: AP_bootstrap_a_rust_project_with_cargo
---

# Move a Rust Project Through Check Run and Release

## Practice Task

Create a small Cargo binary project and take one visible behavior through compile checking, debug execution, and an optimized release build while keeping the outputs of those stages distinct.

## Target Skill

Bootstrap a conventional Rust package and choose the Cargo command and build profile that answer the current development question.

## Setup

Use a shell with `rustc`, `cargo`, and the native linker available. Start outside any existing Cargo package so the generated project structure is unambiguous.

## Instructions

1. Record the active `rustc` and `cargo` versions.
2. Create a new Cargo binary package, then identify its manifest and executable source file.
3. Change the program so it prints a short message that was not in the generated starter.
4. Run `cargo check` and record the outcome.
5. Run the program through Cargo and record its observed output.
6. Produce an optimized release build, run that exact artifact, and record its path and observed output. If the project uses Cargo's defaults, explain why the artifact appears under `target/release`; otherwise identify the setting that relocated it.
7. State why each of the three commands was used and what claim it did not establish by itself.

## Success Check

- The submission names the active compiler and Cargo versions, the manifest, and the source file used for the attempt.
- A successful `cargo check` result and the actual output from running the changed program are both present; a prediction about what it would print does not count as execution evidence.
- The optimized artifact path is under the configured target directory's release-profile output, and the recorded output came from running that artifact rather than rerunning the development profile.
- The explanation distinguishes compile validation, behavioral execution, and optimized artifact production. Merely compiling one file with `rustc`, or only running `cargo run`, is the near-miss: it does not demonstrate command or profile selection across the Cargo lifecycle.
- The reason for each command is stated in terms of the question it answered, not just that the command appeared in the instructions.

## Common Failures

- Treating `cargo check` as a runtime test because it returned successfully.
- Forgetting which executable was run and accidentally measuring or reporting the debug artifact.
- Recreating `Cargo.toml` and `src/main.rs` manually instead of checking the conventions Cargo generated.
- Recording only commands, with no observed versions, paths, or output.

## Notes

This drill teaches the Rust-specific project bootstrap protocol by making the boundary between three Cargo operations observable. It is intentionally small: the behavior is trivial so a failure points at toolchain, layout, command choice, or profile identity rather than application logic.
