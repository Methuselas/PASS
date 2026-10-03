---
object_id: PAT_choose_rust_paths_by_the_relationship_to_the_target
object_type: pattern
name: Choose Rust Paths by the Relationship to the Target
library_path: [software-engineering, languages, rust, modules]
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, paths, crate, self, super, modules]
cross_links:
- rel: related_to
  target_object_id: PAT_watch_for_semantic_coupling
- rel: related_to
  target_object_id: PAT_shape_a_rust_module_tree_around_domain_and_api_boundaries
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: medium
references: []
variants: []
---

# Choose Rust Paths by the Relationship to the Target

## Pattern Rule
**IF** a Rust reference should remain anchored to a known structural relationship
**THEN** start its path with `crate` for the current crate root, `self` for the current module, or `super` for an ancestor
**ELSE** use an external crate name for dependencies and a local in-scope name only when its import makes the origin clear.

## Do
- Use `crate::...` when the target's identity is crate-wide and should not depend on the caller's depth.
- Use `super::...` when code intentionally collaborates with its parent or a sibling reached through that parent.
- Use `self::...` when explicitly distinguishing the current module's item from another name.
- Prefer a path anchor that will survive the likely refactor: moving the caller favors crate-root paths, while moving a cohesive subtree can favor `super` relationships.

## Don't
- Don't use historical leading-colon paths as the spelling for the current crate root.
- Don't make readers infer whether an unanchored first segment is local or external when an explicit anchor resolves the ambiguity.
- Don't climb through repeated `super` segments when the target is conceptually crate-global and a crate-root path is clearer.

## Checklist
- Is the target in this crate, this module, an ancestor, or an external crate?
- Which side is more likely to move during refactoring?
- Does the chosen anchor express the intended coupling?
- Is an import hiding useful origin information?

## Notes
Path spelling communicates structural dependence. The shortest path is not always the most stable or readable one; anchor it at the relationship the code actually relies on.

