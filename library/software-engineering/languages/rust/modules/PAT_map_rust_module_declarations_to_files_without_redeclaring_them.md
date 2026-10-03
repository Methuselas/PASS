---
object_id: PAT_map_rust_module_declarations_to_files_without_redeclaring_them
object_type: pattern
name: Map Rust Module Declarations to Files Without Redeclaring Them
library_path: [software-engineering, languages, rust, modules]
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, modules, files, crate_layout, mod]
cross_links:
- rel: related_to
  target_object_id: PAT_design_the_physical_dependency_graph_too
- rel: related_to
  target_object_id: PAT_shape_a_rust_module_tree_around_domain_and_api_boundaries
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: medium
references: []
variants: []
---

# Map Rust Module Declarations to Files Without Redeclaring Them

## Pattern Rule
**IF** a declared Rust module has grown enough to deserve a separate file
**THEN** keep one `mod name;` declaration in its parent and move only that module's body to the corresponding module file
**ELSE** keep the body inline when separation would add navigation without improving ownership.

## Do
- Declare each module once in its parent, whether the body is inline or loaded from another file.
- For a child declared from a crate root or ordinary module file, place its body in either the sibling `name.rs` file or the legacy `name/mod.rs` form, never both.
- Put submodule declarations in their actual parent module and place their files beneath that parent's directory.
- Choose one file-layout style consistently within a local area when both supported forms are possible.

## Don't
- Don't repeat `mod name` inside the file that already supplies module `name`; that declares a nested module instead of identifying the current one.
- Don't assume creating a source file automatically adds it to the module tree.
- Don't place a nested module beside the crate root and expect its path relationship to be inferred from the filename.
- Don't keep both supported source locations for the same module.

## Checklist
- Where is this module declared by its parent?
- Which single file supplies its body?
- Are each submodule's declaration and file rooted under the correct parent?
- Would inline code be easier to navigate at the current size?

## Notes
The modern file layout no longer requires a parent with submodules to use `mod.rs`; a parent may live in `name.rs` while its children live under `name/`. The declaration still determines the tree, and the file supplies the declared module's contents.

