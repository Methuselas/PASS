---
object_id: PAT_import_rust_names_at_the_level_that_preserves_context
object_type: pattern
name: Import Rust Names at the Level That Preserves Context
library_path: [software-engineering, languages, rust, modules]
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, use, imports, aliases, glob_imports]
cross_links:
- rel: related_to
  target_object_id: PAT_convey_usage_through_names_and_types
- rel: related_to
  target_object_id: PAT_watch_for_semantic_coupling
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: medium
references: []
variants: []
---

# Import Rust Names at the Level That Preserves Context

## Pattern Rule
**IF** repeated Rust paths obscure the operation more than they explain its origin
**THEN** use an import that shortens references while retaining enough namespace context to identify the item
**ELSE** keep the qualified path when its origin prevents ambiguity or improves comprehension.

## Do
- Commonly import a module and call free functions through it when the module name supplies useful context.
- Import types and traits directly when their names remain clear at use sites.
- Use `as` aliases to resolve same-name imports without discarding their origin.
- Keep glob imports within tightly controlled contexts, such as a prelude or tests, where the imported set and collision risk are understood.

## Don't
- Don't import every free function directly when bare calls hide which subsystem performs the work.
- Don't use a glob merely to avoid maintaining an explicit import list.
- Don't rely on an import to make a private item reachable; `use` changes naming scope, not visibility.
- Don't confuse `use` with declaring or loading a module.

## Checklist
- Does the shortened name remain unambiguous at each call site?
- Would the module qualifier add valuable context?
- Could an alias resolve a collision more clearly than a longer path?
- Will a glob silently change meaning when the source namespace grows?

## Notes
Imports create local naming conveniences and may re-export names when public, but they do not change where an item is defined. Choose the import boundary for reader context, not minimum character count.

