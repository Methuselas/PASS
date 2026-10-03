---
object_id: PAT_keep_cargo_lock_under_cargo_and_version_control
object_type: pattern
name: Keep Cargo.lock Under Cargo and Version Control
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
- dependencies
- reproducibility
- version_control
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

# Keep Cargo.lock Under Cargo and Version Control

## Pattern Rule
**IF** a Rust project's dependency resolution should be repeatable across checkouts and automated builds
**THEN** let Cargo maintain `Cargo.lock` as the exact resolution and commit the lockfile so those builds begin from the same dependency set
**ELSE** when intentionally testing the newest versions allowed by `Cargo.toml`, update or omit the lockfile only as an explicit dependency-testing policy rather than by accident.

## Do
- Express the dependency ranges and package metadata you intend in `Cargo.toml`; treat `Cargo.lock` as Cargo's record of the exact versions and source revisions selected from those requirements.
- Keep the lockfile in version control by default. A fresh checkout can then start from the same resolution instead of silently selecting whatever compatible releases happen to be newest that day.
- Use Cargo commands such as `cargo update` when you intend to recalculate all or part of the resolution, then review and test the resulting lockfile change like any other dependency change.
- Make any deliberate unlocked or latest-dependency job separate and visible. It answers whether the declared ranges remain healthy, not whether the recorded project build is reproducible.

## Don't
- Don't edit package entries or checksums in `Cargo.lock` by hand; the file is generated state whose consistency Cargo owns.
- Don't mistake `Cargo.toml` for an exact resolution. Its version requirements describe acceptable dependency choices, while the lockfile records the choice Cargo actually made.
- Don't delete a lockfile merely to fix a dependency problem without first identifying which resolution changed and whether the manifest should constrain it.

## Checklist
- Is `Cargo.toml` the human-edited statement of dependency intent?
- Is `Cargo.lock` generated and updated through Cargo rather than edited directly?
- Is the lockfile committed, or is a documented testing or publication policy the reason it is absent?
- After an intentional update, did the dependency diff receive the tests and review appropriate to its risk?

## Notes
The manifest and lockfile solve different problems. A range keeps a package compatible with an evolving ecosystem; an exact resolution makes a particular checkout repeatable. Treating either file as if it did both jobs creates surprise: a manifest alone can resolve differently over time, while a hand-edited lockfile can claim a state Cargo did not produce.
