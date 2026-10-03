---
object_id: PAT_shape_a_rust_module_tree_around_domain_and_api_boundaries
object_type: pattern
name: Shape a Rust Module Tree Around Domain and API Boundaries
library_path: [software-engineering, languages, rust, modules]
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, modules, namespaces, api_design, organization]
cross_links:
- rel: related_to
  target_object_id: PAT_design_modular_interfaces
- rel: related_to
  target_object_id: PAT_design_the_physical_dependency_graph_too
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: medium
references: []
variants: []
---

# Shape a Rust Module Tree Around Domain and API Boundaries

## Pattern Rule
**IF** a Rust crate has enough items that their relationships or public surface are hard to see
**THEN** group related items into a module tree whose paths express domain ownership and whose public branches match the intended API
**ELSE** keep the smaller crate flat until a real namespace or visibility boundary appears.

## Do
- Treat the crate root as the root of one module tree and make each child represent a coherent capability or concept.
- Nest a module when its contents belong to the parent concept and callers benefit from that relationship in paths.
- Design the public paths callers should use before distributing the module bodies across files.
- Keep implementation-only modules private and expose a smaller stable surface through public items or re-exports.

## Don't
- Don't create modules merely to shorten a file or mirror every type with a namespace.
- Don't let incidental file placement dictate the conceptual API tree.
- Don't expose every internal branch just because one leaf must be callable.

## Checklist
- Does each module name describe one coherent part of the domain?
- Do public paths communicate where capabilities belong?
- Can implementation modules move without forcing callers to change?
- Is the tree simpler than leaving the items together?

## Notes
Rust modules simultaneously provide namespaces and visibility boundaries. Files can carry module bodies, but the declared module tree—not the directory tree alone—defines item paths and access.

