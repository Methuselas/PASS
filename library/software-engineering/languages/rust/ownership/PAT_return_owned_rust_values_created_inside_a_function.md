---
object_id: PAT_return_owned_rust_values_created_inside_a_function
object_type: pattern
name: Return Owned Rust Values Created Inside a Function
library_path: [software-engineering, languages, rust, ownership]
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, ownership, references, return_values, lifetimes]
cross_links:
- rel: related_to
  target_object_id: PAT_give_every_acquired_resource_one_named_owner
- rel: related_to
  target_object_id: PAT_return_rust_values_with_tail_expressions
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: medium
references: []
variants: []
---

# Return Owned Rust Values Created Inside a Function

## Pattern Rule
**IF** a Rust function creates a value whose storage must remain valid after the function returns
**THEN** return the owned value so ownership moves to the caller
**ELSE** return a reference only when its lifetime is validly tied to an input, static storage, or another owner that outlives the result.

## Do
- Return `String`, an owned vector, or another owned result when the function constructs the result locally.
- Return a borrowed view when the result points into caller-provided data and the signature can express that relationship.
- Let a move return transfer responsibility without cloning the underlying resource.
- Use lifetime errors to identify which owner the proposed reference would depend on.

## Don't
- Don't return a reference to a local owned value that will be dropped as the function exits.
- Don't add a `'static` annotation to manufacture longevity for data that is not actually static.
- Don't clone a local result merely to make returning it possible; returning ownership already moves it safely.

## Checklist
- Who owns the result's storage after the call?
- If the result is borrowed, which input or longer-lived owner keeps it valid?
- Would any local owner be dropped before the returned reference is used?
- Can the owned value be returned directly without copying?

## Notes
A function may safely move a locally created owned value to its caller because the value's ownership leaves the function before the local binding ends. A reference cannot carry local storage with it; it must point into storage whose owner remains alive for the reference's entire use.
