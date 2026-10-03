---
object_id: PAT_constrain_rust_generics_by_required_behavior
object_type: pattern
name: Constrain Rust Generics by Required Behavior
library_path: [software-engineering, languages, rust, generics]
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: PAT_use_generics_for_type_independence
tags: [rust, generics, trait_bounds, api_design, ownership]
cross_links:
- rel: related_to
  target_object_id: PAT_encode_rust_ownership_intent_in_function_signatures
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
references: []
variants: []
---

# Constrain Rust Generics by Required Behavior

## Pattern Rule
**IF** a Rust generic body uses operations that are not available to every possible type
**THEN** add only the trait bounds required by those operations and choose ownership or borrowing separately from behavioral capability.
**ELSE** leave the type parameter unconstrained so callers retain every implementation the body can actually support.

## Do
- Let the first compile error identify the missing capability: comparison requires an ordering trait, formatting requires a formatting trait, and cloning requires `Clone` only when the implementation truly clones.
- Use a `where` clause when several parameters or bounds would bury the function's inputs and result in angle-bracket syntax.
- Use argument-position `impl Trait` for a simple anonymous bounded parameter; keep a named type parameter when callers must select it explicitly or when multiple inputs must share the same concrete type.
- Put bounds on an `impl` block when the methods in that block should exist only for types with those capabilities; keep universally available methods in an unbounded block.
- Reconsider the data flow before adding `Copy` or `Clone`: returning a reference into an input may preserve the algorithm while accepting more types and avoiding duplication.

## Don't
- Don't add broad convenience bounds because the first implementation happened to use a copyable primitive.
- Don't mix the question "what operations does this algorithm need?" with "who should own the result?"; a comparison bound does not imply a copying bound.
- Don't repeat a long bound list inline when a `where` clause would make the callable interface easier to inspect.

## Checklist
- Does every declared bound enable an operation that appears in the implementation or its promised interface?
- Would changing an owned result to a borrowed result remove an otherwise unnecessary `Copy` or `Clone` requirement?
- Are unconditional methods still available for every `T`, with capability-specific methods isolated behind bounded implementations?
- Does the chosen bound syntax preserve any same-type relationship the interface needs between parameters?
- Do at least two materially different concrete types satisfy and exercise the abstraction?

## Notes
The language-agnostic foundation is to use generics when a subproblem does not depend on one concrete type. This specialization begins after that decision: Rust checks the definition against the capabilities its bounds promise, so an initially failing abstraction exposes each operation the body assumed. The design task is to encode those real assumptions without turning incidental choices about copying, formatting, or ordering into permanent restrictions on callers.
