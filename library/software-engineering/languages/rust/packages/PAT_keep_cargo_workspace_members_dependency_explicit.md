---
object_id: PAT_keep_cargo_workspace_members_dependency_explicit
object_type: pattern
name: Keep Cargo Workspace Membership and Dependencies Explicit
library_path: [software-engineering, languages, rust, packages]
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: PAT_design_the_physical_dependency_graph_too
tags: [rust, cargo, workspace, dependencies, packages]
cross_links:
- rel: related_to
  target_object_id: PAT_keep_cargo_lock_under_cargo_and_version_control
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
references: []
variants: []
---

# Keep Cargo Workspace Membership and Dependencies Explicit

## Pattern Rule
**IF** related Rust packages are developed and verified together
**THEN** place them in a Cargo workspace for shared resolution and orchestration, while making every package declare each dependency it actually uses, including dependencies on sibling members.

## Do
- Use workspace membership to define the packages Cargo should coordinate and choose default members deliberately when root commands should target a subset.
- Add an explicit path dependency when one member consumes another; membership alone does not create a dependency edge.
- Centralize shared package fields or dependency requirements in the workspace manifest only when each member opts into that inheritance and the shared policy is real.
- Keep one workspace lockfile under Cargo and version control so coordinated builds begin from one selected dependency graph.
- Run workspace-wide checks for integration confidence and package-selected checks when isolating a member-specific failure.

## Don't
- Don't assume a crate can import a dependency merely because another workspace member declares it.
- Don't split packages only to make files shorter; require a meaningful ownership, publication, build, or dependency boundary.
- Don't infer that one shared lockfile makes every member use one semver-compatible release in every circumstance; inspect the resolved graph when version unification matters.
- Don't make a path-only sibling dependency unpublishable by accident when the package is intended for a registry release.

## Checklist
- Does each member represent a coherent package boundary?
- Is every actual dependency edge present in the consuming member's manifest?
- Are workspace inheritance and resolver settings explicit for the workspace shape and edition policy?
- Do root commands operate on the intended default members or the whole workspace?
- Can every publishable member resolve its sibling dependencies under the registry contract?

## Notes
A workspace coordinates packages; it does not merge their namespaces or dependency declarations. Shared output and resolution reduce redundant work, while explicit member manifests preserve the physical graph that Cargo, reviewers, and downstream publishers must understand.

