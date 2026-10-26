---
object_id: PAT_choose_cargo_dependency_source_by_release_contract
object_type: pattern
name: Choose a Cargo Dependency Source by Release Contract
library_path:
- software-engineering
- languages
- rust
- packages
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- rust
- cargo
- dependencies
- registry
- git
- path
- publishing
cross_links:
- rel: related_to
  target_object_id: PAT_keep_cargo_lock_under_cargo_and_version_control
- rel: related_to
  target_object_id: PAT_keep_cargo_workspace_members_dependency_explicit
reference:
  source_title: Practical System Programming for Rust Developers
  author: Prabhu Eshwarla
confidence: medium
references: []
variants: []
---

# Choose a Cargo Dependency Source by Release Contract

## Pattern Rule
**IF** a Cargo dependency can come from a registry, Git repository, or local path
**THEN** choose the source form that matches how the dependency is owned, reproduced, and released, and make that source contract explicit in the manifest

## Do
- Use a registry dependency when the project consumes a published release contract that downstream consumers should resolve normally.
- Use a path dependency for code developed together locally when the filesystem relationship is part of the development setup.
- Use a Git dependency only when the project intentionally depends on repository state not represented by the required registry release.
- When a package may be published, verify that its dependency declarations remain publishable and resolve outside the local checkout.

## Don't
- Do not choose a path dependency merely for convenience if publication would leave consumers without a usable external dependency contract.
- Do not depend on a moving Git branch when reproducibility requires an immutable revision or published release.
- Do not confuse the source locator with the version requirement; they answer different questions about where code comes from and which releases are acceptable.

## Checklist
- Is this dependency consumed as a published release, co-developed source, or repository snapshot?
- Can another developer reproduce the selected dependency source without relying on my private filesystem?
- If the package will be published, will Cargo accept and resolve the dependency declaration for downstream consumers?
- Does the lockfile capture the concrete resolution expected for this package shape?

## Notes
Cargo supports registry, Git, and path sources, including declarations that pair a local/Git development source with a registry version for publication. The durable decision is to align the source form with the dependency relationship and release contract, not merely to memorize manifest syntax.
