---
object_id: PAT_choose_a_rust_impl_function_by_receiver_need
object_type: pattern
name: Choose a Rust Impl Function by Receiver Need
library_path: [software-engineering, languages, rust, structs]
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, methods, associated_functions, receivers, ownership]
cross_links:
- rel: related_to
  target_object_id: PAT_define_the_operation_set_before_the_representation
- rel: related_to
  target_object_id: PAT_encode_rust_ownership_intent_in_function_signatures
- rel: related_to
  target_object_id: PAT_guard_the_interface_abstraction_under_modification
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: medium
references: []
variants: []
---

# Choose a Rust Impl Function by Receiver Need

## Pattern Rule
**IF** behavior belongs to a Rust type and operates on an existing instance
**THEN** make it a method taking `&self` to observe, `&mut self` to mutate, or `self` to consume the receiver
**ELSE** make it an associated function when the operation belongs to the type but needs no instance, such as construction from inputs.

## Do
- Put instance behavior in an `impl` block when naming it through the type keeps the operation set coherent.
- Choose the weakest receiver that supports the contract: shared observation before exclusive mutation, and consumption only when the method takes over or transforms the value.
- Use an associated function for constructors and type-scoped operations whose inputs contain everything they need.
- Return `Self` from a constructor when the result is the implementing type and spelling the concrete name adds no information.

## Don't
- Don't take `&mut self` for a calculation that only reads fields.
- Don't take `self` merely for convenient field access when callers should retain a non-`Copy` value afterward.
- Don't force a static-style associated function to accept an irrelevant instance just to use method-call syntax.
- Don't attach behavior to a type when it violates the abstraction that type presents.

## Checklist
- Does the operation require an existing instance?
- Does it observe, mutate, or consume that instance?
- Would an associated constructor be clearer than free construction logic?
- Does the operation belong to this type's abstraction rather than merely use its data?

## Notes
The receiver is part of a Rust method's ownership contract. Method-call syntax may insert ordinary references and dereferences to match it, but the declaration remains the authoritative statement of whether the instance is shared, exclusively borrowed, or consumed.

