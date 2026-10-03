---
object_id: PAT_open_rust_visibility_only_through_the_intended_api_path
object_type: pattern
name: Open Rust Visibility Only Through the Intended API Path
library_path: [software-engineering, languages, rust, modules]
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, visibility, pub, api_design, encapsulation]
cross_links:
- rel: related_to
  target_object_id: PAT_design_modular_interfaces
- rel: related_to
  target_object_id: PAT_guard_the_interface_abstraction_under_modification
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: medium
references: []
variants: []
---

# Open Rust Visibility Only Through the Intended API Path

## Pattern Rule
**IF** a Rust item must be used beyond its current visibility boundary
**THEN** grant the narrowest visibility that reaches the intended callers and ensure every public path segment is reachable
**ELSE** leave the item private and let its parent module own access to it.

## Do
- Start private, then choose unrestricted `pub` only for the external API and restricted visibility for crate-, parent-, or subtree-scoped collaboration.
- Check the complete path: a public leaf inside an unreachable private module is not externally callable through that path.
- Use a public re-export when callers need a stable API name without seeing the internal module layout.
- Treat dead-code warnings as evidence to investigate, not as instructions to publish an item.

## Don't
- Don't make an entire module tree public to reach one operation.
- Don't expose an item merely to silence an unused-code warning.
- Don't assume `pub` means globally reachable independently of its containing path.
- Don't leak internal organization into the public API when a deliberate re-export can hide it.

## Checklist
- Which exact callers require access?
- What is the narrowest visibility that includes them?
- Is every segment of the intended access path reachable?
- Should a re-export define a cleaner or more stable public path?

## Notes
Rust visibility is scoped and path-dependent. Privacy protects implementation by default; `pub`, restricted `pub` forms, and re-exports let the crate expose a designed surface rather than its physical layout.

