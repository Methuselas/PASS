---
object_id: PAT_clone_rust_values_only_for_independent_ownership
object_type: pattern
name: Clone Rust Values Only for Independent Ownership
library_path: [software-engineering, languages, rust, ownership]
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, ownership, clone, moves, performance]
cross_links:
- rel: related_to
  target_object_id: PAT_give_every_acquired_resource_one_named_owner
- rel: related_to
  target_object_id: PAT_keep_immutable_with_builder_or_copy_on_write
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: medium
references: []
variants: []
---

# Clone Rust Values Only for Independent Ownership

## Pattern Rule
**IF** two Rust values must own logically independent copies that may live or change separately
**THEN** call `clone` only after confirming that the type's implementation provides the needed independence, and accept its type-defined cost
**ELSE** move the value to its new owner or borrow it for temporary access.

## Do
- Treat an assignment or by-value call of a non-`Copy` value as an ownership transfer, not as an implicit deep copy.
- Use a shared or mutable borrow when the second user only needs access for a bounded period.
- Inspect the type's `Clone` behavior before relying on independence; some implementations duplicate data, while others increase shared ownership or perform other type-specific work.
- Keep the clone at the boundary where the need for a second owner becomes explicit.

## Don't
- Don't add `.clone()` reflexively to silence a moved-value diagnostic before deciding who should own the value.
- Don't describe every clone as a deep heap copy; `Clone` is a trait contract implemented by the type, not one universal storage operation.
- Don't treat another shared-ownership handle as an independent copy merely because it came from `clone`.
- Don't assume a move performs expensive allocation work; ownership can transfer while the underlying resource remains in place.

## Checklist
- Do both results truly need independent ownership and potentially different lifetimes?
- Would borrowing express the actual temporary relationship?
- Is the clone's cost and sharing behavior understood for this type?
- Is the original still used for a reason rather than by accident?

## Notes
Move diagnostics often expose an unresolved ownership decision. A clone is correct here when both sides genuinely need independent state and the implementation supplies it; otherwise it is a poor substitute for deciding between transfer, borrowing, or intentional shared ownership. Keeping cloning explicit also keeps potentially nontrivial work visible.
