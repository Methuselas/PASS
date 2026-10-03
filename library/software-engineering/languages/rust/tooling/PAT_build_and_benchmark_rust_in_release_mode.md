---
object_id: PAT_build_and_benchmark_rust_in_release_mode
object_type: pattern
name: Build and Benchmark Rust in Release Mode
library_path:
- software-engineering
- languages
- rust
- tooling
stage_binding: 4 final
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- rust
- cargo
- release_profile
- benchmarking
- optimization
cross_links:
- rel: related_to
  target_object_id: PAT_reproduce_the_real_context_before_believing_a_microbenchmark
reference:
  source_title: The Rust Programming Language
  author: Steve Klabnik and Carol Nichols
confidence: medium
references: []
variants: []
---

# Build and Benchmark Rust in Release Mode

## Pattern Rule
**IF** you are measuring a Rust program's runtime performance or preparing its optimized executable for delivery
**THEN** build with the release profile and run the resulting release artifact from the configured Cargo target directory
**ELSE** keep the development profile for the faster rebuild cycle used during ordinary implementation.

## Do
- Use `cargo build --release` before a runtime benchmark whose conclusion is intended to describe shipped performance.
- Execute the release artifact explicitly, and record the profile, toolchain, features, target, and input that produced the measurement. With the ordinary host build and default target directory, the profile output is under `target/release`; custom target directories and explicit compilation targets change that path.
- Keep the debug-profile executable available for quick iteration and diagnostics; the two profiles answer different needs rather than forming a quality ranking.
- Rebuild the release artifact after relevant source, dependency, feature, or toolchain changes before trusting a comparison.

## Don't
- Don't benchmark a development-profile artifact and present the result as the performance of an optimized Rust build.
- Don't assume `cargo run` selected the release profile unless the invocation explicitly requested it.
- Don't compare two measurements when one was produced by a stale release artifact or a different feature set.

## Checklist
- Was the measured executable produced by the intended release-profile command?
- Does the recorded executable path point to the configured target directory's release-profile output rather than its development-profile output?
- Are the toolchain, features, inputs, and relevant environment conditions recorded with the result?
- Was the release artifact rebuilt after the last change that could affect performance?

## Notes
Cargo separates development and release profiles because optimization trades longer compilation for different runtime behavior. The practical trap is measuring the fast-to-build profile and drawing conclusions about the profile users will receive. Profile identity is part of the benchmark context, not an incidental build detail.
