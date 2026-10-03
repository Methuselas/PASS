---
object_id: PAT_manage_rust_toolchains_with_rustup
object_type: pattern
name: Manage Rust Toolchains With rustup
library_path:
- software-engineering
- languages
- rust
- tooling
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- rust
- rustup
- toolchain
- installation
- documentation
cross_links:
- rel: related_to
  target_object_id: PAT_state_your_compatibility_promise_and_its_span
reference:
  source_title: The Rust Programming Language
  author: Steve Klabnik and Carol Nichols
confidence: medium
references: []
variants: []
---

# Manage Rust Toolchains With rustup

## Pattern Rule
**IF** you need to install, update, select, or inspect the Rust toolchain used by a project
**THEN** use rustup to manage the declared toolchain and its bundled documentation, then verify the active `rustc` and `cargo` versions before building
**ELSE** when a controlled environment supplies Rust another way, record the compiler and Cargo versions explicitly and verify that the project can reproduce them.

## Do
- Install through the current official Rust installation route for the operating system. When that route downloads and executes a script, inspect or otherwise verify it according to the environment's software-installation policy before granting it the requested authority.
- Run `rustc --version` and `cargo --version` after installation or selection. A successful installer message does not prove that the shell resolves the intended toolchain.
- Use `rustup update stable` when the project permits movement to the current stable channel, and pin or select the project's declared toolchain when reproducibility matters more than following the newest stable release.
- Use `rustup doc` for the documentation associated with the installed toolchain instead of assuming that an unrelated online version describes the local standard library.
- Treat linker and native build-tool availability as a separate prerequisite. The Rust compiler can be present while final linking or native dependencies still fail.

## Don't
- Don't copy an old platform-specific installer, PATH edit, help channel, or Visual Studio version into a current setup guide without checking the current Rust installation documentation.
- Don't infer the active compiler from what rustup last downloaded; another override, pinned toolchain, or shell PATH can select different binaries.
- Don't update a toolchain merely because a newer stable release exists when the project has an explicit compatibility target that has not been tested against it.
- Don't assume the Rust Project services old stable releases with ongoing fixes; its current support policy applies fixes and security updates to the latest stable version, so a project that supports older compilers owns the testing and support consequences.

## Checklist
- Do `rustc --version` and `cargo --version` report the intended toolchain?
- Is the project's toolchain/channel policy explicit enough to reproduce?
- Can `rustup doc` open documentation that matches the selected installation?
- If compilation reaches the link step, are the required linker and native build tools present?

## Notes
rustup manages Rust versions and associated tools as one toolchain rather than treating the compiler as an isolated executable. The important boundary is verification: installation, selection, shell resolution, and native linking are distinct stages, and each can succeed while the next one fails.
