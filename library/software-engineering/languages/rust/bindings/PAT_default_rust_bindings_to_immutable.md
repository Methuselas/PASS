---
object_id: PAT_default_rust_bindings_to_immutable
object_type: pattern
name: Default Rust Bindings to Immutable
library_path: [software-engineering, languages, rust, bindings]
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, bindings, immutability, mutability, intent]
cross_links:
- rel: related_to
  target_object_id: PAT_prefer_immutable_objects
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: medium
references: []
variants: []
---

# Default Rust Bindings to Immutable

## Pattern Rule
**IF** a Rust binding does not need reassignment or in-place mutation for its intended lifetime
**THEN** leave it immutable and add `mut` only where mutation is part of the design
**ELSE** mark it `mut` at the binding so the changing state is visible to the compiler and the reader.

## Do
- Start without `mut`; let a rejected assignment identify the exact binding whose state transition needs justification.
- Keep mutable spans narrow, completing mutation near initialization before passing the value onward when practical.
- Treat `mut` as intent, not boilerplate: it says later code may change the bound value through this name.
- Weigh in-place mutation against producing a transformed value when large allocations or a clearer state transition make one materially better.

## Don't
- Don't add `mut` preemptively to silence anticipated friction; unused mutability weakens the local guarantee for no benefit.
- Don't confuse an immutable binding with a compile-time constant. `const` has its own declaration, required type, allowed expressions, and scope.
- Don't infer deep immutability of every reachable value merely from the absence of `mut`; ownership and interior-mutability mechanisms determine what else can change.

## Checklist
- Is every `mut` followed by a real mutation through that binding?
- Could the mutable phase be shortened or expressed as a completed transformation?
- Does the code need a runtime binding or a true `const` item?
- Are claims about reachable state supported by the types rather than by the binding keyword alone?

## Notes
Rust's default turns non-mutation from a convention into a checked local fact. The value is cognitive as well as defensive: a reader can stop considering reassignment until `mut` explicitly reopens that possibility.

