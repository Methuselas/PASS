---
object_id: AP_bootstrap_a_rust_project_with_cargo
object_type: ap
name: Bootstrap a Rust Project With Cargo
library_path:
- software-engineering
- languages
- rust
- tooling
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- rust
- cargo
- rustup
- project_setup
- build
cross_links:
- rel: supports
  target_object_id: PAT_manage_rust_toolchains_with_rustup
- rel: supports
  target_object_id: PAT_use_cargo_check_during_rust_iteration
- rel: supports
  target_object_id: PAT_build_and_benchmark_rust_in_release_mode
- rel: supports
  target_object_id: PAT_keep_cargo_lock_under_cargo_and_version_control
- rel: related_to
  target_object_id: AP_grow_a_system_from_a_running_skeleton
reference:
  source_title: The Rust Programming Language
  author: Steve Klabnik and Carol Nichols
confidence: medium
references: []
variants: []
---

# Bootstrap a Rust Project With Cargo

## Objective

Move from an unverified Rust environment to a conventional Cargo project that has passed compiler validation, executed its first program, and produced an optimized release artifact. Success means the toolchain and each output are identifiable and reproducible rather than merely that one `Hello, world!` happened to print.

## Steps / Flow

1. **Name the toolchain policy before installing.** Decide whether the project follows the current stable channel or a pinned toolchain. `PAT_manage_rust_toolchains_with_rustup` owns installation, selection, updates, matching local documentation, and the native linker prerequisite.

2. **Gate on the actual shell environment.** Run `rustc --version` and `cargo --version`. If either command is missing or reports the wrong selection, fix rustup selection or PATH resolution before creating project files; proceeding would bind the project to an environment you have not identified.

3. **Create the Cargo package.** Use a command such as `cargo new hello-rust` for the default binary package, or select `--lib` when the package is a library. Use `--bin` only when making that intent explicit helps a script or reader; binary is already the current default. Enter the generated directory rather than recreating its layout by hand.

4. **Inspect the generated skeleton before extending it.** Confirm that `Cargo.toml` owns package configuration, declares the intended Rust edition, and that Rust source lives under `src/` with the requested target kind. Do not copy an old generated manifest: current Cargo selects the newest stable edition for new packages, and generated fields change over time. `PAT_keep_cargo_lock_under_cargo_and_version_control` owns the exact dependency resolution.

5. **Run the fast compiler gate.** Invoke `cargo check` before adding more behavior. `PAT_use_cargo_check_during_rust_iteration` owns the choice between check, build, and run; a successful check proves compile validation, not program behavior.

6. **Run the skeleton end to end.** Use Cargo to build and execute the program, and compare the observed output with the starter program's expected output. If execution fails after the check passed, diagnose the link, launch, or runtime boundary rather than repeating the compile-only gate.

7. **Produce the delivery profile separately.** Invoke the release build and locate its artifact under the configured target directory's release profile output. The ordinary default is `target/release`, but configuration, environment, cross-compilation, and explicit command options can relocate it. `PAT_build_and_benchmark_rust_in_release_mode` owns the profile boundary and any performance measurement made from it.

8. **Completion check.** Record the selected Rust and Cargo versions, the manifest and source locations, the successful check and run, and the exact release artifact path. The project is ready to grow only when another practitioner could repeat those gates and identify which profile each artifact came from.

## Notes

The sequence matters because each gate isolates a different class of failure: installation and shell resolution, generated project structure, compiler/type validation, linking and execution, then optimized artifact production. Running all of them as one opaque setup command loses that diagnostic separation.

Direct `rustc` compilation remains useful for a truly isolated file or for understanding the compiler boundary. Cargo becomes the normal owner once a project has a manifest, dependencies, multiple targets, or a need for reproducible commands across operating systems. The general practice of growing a running skeleton remains in `AP_grow_a_system_from_a_running_skeleton`; this protocol supplies the Rust-specific bootstrapping route.
