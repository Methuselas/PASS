---
object_id: PAT_add_reflected_and_in_place_operators_only_where_they_apply
object_type: pattern
name: Add Reflected and In-Place Operators Only Where They Apply
library_path:
- software-engineering
- languages
- python
- classes
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- classes
- operator-overloading
- protocols
cross_links:
- rel: related_to
  target_object_id: PAT_overload_an_operator_only_to_mimic_a_builtin_interface
- rel: related_to
  target_object_id: PAT_choose_augmented_assignment_for_single_evaluation_speed_and_in_place_effect
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Add Reflected and In-Place Operators Only Where They Apply

## Pattern Rule
**IF** a class already overloads a binary operator such as `+` and instances may appear on the right of it, or be the target of `+=`
**THEN** add `__radd__` only when the operation should work with the instance on the right of a non-instance, and `__iadd__` only when an in-place update is genuinely cheaper than building a new object — returning `NotImplemented` from any of them for operand types the class does not handle
**ELSE** when neither case arises, leave them out: `x + y` already finds `__add__` whenever the left operand is an instance, and `x += y` already falls back to `__add__` plus a rebind

## Do
- Read `__radd__(self, other)` with the operands swapped: `self` is the right-hand instance and `other` is the left-hand value, so a non-commutative operation must respect that order.
- Alias `__radd__ = __add__` in the class body for a genuinely commutative operation; it saves a forwarding call, and the shared method sees the instance as `self` either way.
- Return `NotImplemented` for operands the class cannot handle, so Python can try the other operand's reflected method and then raise a clear `TypeError` — returning `False` or raising directly short-circuits that negotiation.
- Return `self` from `__iadd__` after mutating; the statement rebinds the target to whatever the method returns, so forgetting the return silently sets the variable to `None`.
- Check the operand type in a binary method that builds a new instance of its own class, so adding two instances does not wrap one result inside another.

## Don't
- Don't add `__radd__` out of symmetry. It is called only when the left operand's type could not handle the operation, which for most application classes never happens.
- Don't make `__iadd__` mutate an object meant to be a value. `+=` on an immutable-feeling type should produce a new object, as it does for numbers, strings and tuples; silent in-place mutation surprises every holder of another reference.
- Don't assume `+=` needs `__iadd__` at all — without it, Python computes `__add__` and rebinds, which is correct, just not optimized for large mutable payloads.
- Don't let a right-side method nest results: without a type check, `instance + instance` can produce an instance whose payload is another instance, which still computes correctly while the displays and recursion depth grow.

## Checklist
- Is there a real case where a non-instance appears on the left of this operator with an instance on the right?
- Does every binary method return `NotImplemented` rather than failing for unsupported operand types?
- Does `__iadd__` return `self`?
- Does adding two instances produce a flat result rather than a nested one?

## Notes
Python resolves a binary expression by asking the left operand's type first; only if that declines — by having no such method, or by returning `NotImplemented` — does it ask the right operand's reflected method. That protocol is why `NotImplemented` is a value to return rather than an error to raise: it is the way a type says "not mine" without ending the negotiation. The in-place variants are a separate, optional optimization layer on top, which is why omitting them costs correctness nothing.
