---
object_id: PAT_break_rust_reference_cycles_with_weak_edges
object_type: pattern
name: Break Rust Reference Cycles With Weak Edges
library_path: [software-engineering, languages, rust, ownership]
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: PAT_give_every_acquired_resource_one_named_owner
tags: [rust, rc, weak, reference_cycles, ownership_graphs]
cross_links:
- rel: related_to
  target_object_id: PAT_choose_rust_smart_pointer_by_ownership_contract
- rel: related_to
  target_object_id: PAT_end_a_rust_resource_guard_with_scope_or_drop
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
references: []
variants: []
---

# Break Rust Reference Cycles With Weak Edges

## Pattern Rule
**IF** an `Rc&lt;T&gt;` ownership graph can follow strong links in a cycle
**THEN** decide which relationships keep nodes alive and represent every non-owning back-reference or observer edge with `Weak&lt;T&gt;`, upgrading it to `Option&lt;Rc&lt;T&gt;&gt;` only for the duration of use
**ELSE** keep strong `Rc&lt;T&gt;` links only where each edge is a genuine owner.

## Do
- Draw the ownership direction before choosing pointer types: a parent may own children while each child's parent link merely observes the parent.
- Create a weak edge with `Rc::downgrade` so it does not contribute to the strong count that controls destruction.
- Call `upgrade` at the use site and handle both `Some` and `None`; the observed allocation may already have been dropped.
- Keep interior mutability around only the edge that must be rewired, rather than making the entire node runtime-mutable.
- Test teardown by dropping the strong owner and confirming weak observers can no longer upgrade it.

## Don't
- Don't make every bidirectional link strong. Rust permits memory-safe leaks, and a strong cycle keeps every count above zero so no node is dropped.
- Don't dereference a `Weak&lt;T&gt;` as if it guaranteed liveness; it deliberately carries no ownership claim.
- Don't use `weak_count` as a reason to keep an allocation's value alive; only strong owners control that lifetime.
- Don't treat a program ending soon as proof that a cycle is harmless in a long-lived process or repeatedly constructed graph.

## Checklist
- Which edges are owners and which are observers?
- Can following only strong edges return to the starting node?
- Does every non-owning edge use `Weak&lt;T&gt;`?
- Does every upgrade handle the target already being gone?
- After strong owners leave scope, do the nodes actually drop?

## Notes
Reference counting drops the inner value only when its strong count reaches zero, so a cycle of owners is a stable leak rather than an unsafe pointer. A weak edge preserves navigation without extending the value's lifetime; the allocation's backing storage may remain until its weak pointers are also gone. The `Option` returned by `upgrade` is the executable reminder that observation and ownership are different promises.
