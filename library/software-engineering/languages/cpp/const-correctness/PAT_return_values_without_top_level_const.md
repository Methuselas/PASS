---
object_id: PAT_return_values_without_top_level_const
object_type: pattern
name: Return Values Without Top-Level const
library_path:
- software-engineering
- languages
- cpp
- const-correctness
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- const
- operator_overloading
- value_semantics
cross_links:
- rel: related_to
  target_object_id: PAT_apply_const_to_lock_invariants
- rel: related_to
  target_object_id: AP_make_a_class_const_correct
reference:
  source_title: PASS software-engineering canonical synthesis
  author: Modern C++ correction of accepted const-correctness guidance
confidence: high
references: []
variants: []
---

# Return Values Without Top-Level const

## Pattern Rule
**IF** a function produces a new value
**THEN** return a non-const value, and express any forbidden operation through the value type's ref-qualified or constrained interface instead of making the prvalue `const`.

## Do
- Return `T`, not `const T`, from arithmetic operators and other value-producing functions so callers can move from the result and use rvalue-qualified operations.
- Ref-qualify assignment as `T& operator=(const T&) &` when assignment is meaningful only for named, persistent objects. Then `(a * b) = c` is rejected because the left operand is a prvalue, without poisoning the returned value with top-level `const`.
- Apply the same design to other mutating operations: use `&`, `const &`, `&&`, constraints, or deletion to state which value categories may call them.

## Don't
- Don't return `const T` by value to block assignment to a temporary. Top-level `const` on the result can suppress moves and reject otherwise valid rvalue use.
- Don't treat a suspicious expression such as `if (a * b = c)` as only a return-type problem. Make assignment unavailable on rvalues and enable warnings that diagnose assignment used as a condition.

## Checklist
- Does every value-producing function return an unqualified value type?
- Are mutating members callable only on the value categories for which mutation has a durable meaning?
- Does deliberate misuse fail at the interface boundary without disabling moves from ordinary results?

## Notes
Older C++ guidance returned arithmetic results as `const` values so a second mutating operation would not compile. In modern C++, that top-level qualification travels into overload resolution and can prevent a move or an intended rvalue-qualified call. Ref-qualified members put the restriction on the operation that owns it: a named object can be assigned, while a disposable result cannot. The result remains an ordinary movable value.
