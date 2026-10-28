---
object_id: PAT_generate_interop_marshalling_at_a_rich_foreign_boundary
object_type: pattern
name: Generate Interop Marshalling at a Rich Foreign Boundary
library_path:
- software-engineering
- core
- abstraction
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: general
specialization_axis: none
foundation_object_id: PAT_expose_clean_api_hide_implementation
tags:
- interop
- ffi
- bindings
- marshalling
- code-generation
- abstraction
cross_links: []
reference:
  source_title: Fullstack Rust
  author: Nate Murray
confidence: high
references: []
variants: []
---

# Generate Interop Marshalling at a Rich Foreign Boundary

## Pattern Rule
**IF** two runtimes expose a low-level foreign interface but application code needs richer strings, objects, collections, or ownership semantics across that boundary
**THEN** use a maintained binding generator or schema-driven adapter to own repetitive marshalling and cleanup, and keep the generated/raw ABI surface behind one typed boundary
**ELSE** hand-write the boundary only when the ABI is genuinely small, stable, and simple enough to audit directly.

## Do
- Define the application-facing contract in typed terms before choosing the generated binding representation.
- Use a maintained generator that owns pointer/length conversion, representation translation, and cleanup for the supported types.
- Pin and verify the generator/runtime compatibility as part of the build because generated code and its runtime helpers form one contract.
- Keep generated glue and raw ABI details at the interop edge; pass ordinary application types into the rest of the system.
- Inspect ownership, allocation, error, and lifetime behavior at the boundary even when code generation hides the mechanics.

## Don't
- Don't duplicate handwritten allocation, deallocation, encoding, and pointer arithmetic for every rich boundary value when a maintained generator already owns that protocol.
- Don't treat generated glue as magic or exempt it from version and ownership review.
- Don't leak generated transport types through unrelated domain code.
- Don't add code generation when a tiny scalar ABI is simpler and safer to audit by hand.

## Checklist
- What richer values must cross the low-level ABI?
- Who owns allocations and cleanup on each side?
- Can a maintained generator express the required types and error behavior?
- Are generator, runtime helper, and consumer versions compatible?
- Can the application interior remain unaware of raw pointers or wire representations?

## Notes
Generated bindings trade handwritten marshalling risk for a versioned toolchain dependency. That is usually favorable when the boundary carries rich values, provided the generated ABI layer stays isolated and its ownership and compatibility rules are still reviewed.
