---
object_id: PAT_dont_implement_one_copying_function_via_the_other
object_type: pattern
name: Don't Implement One Copying Function in Terms of the Other
library_path:
- software-engineering
- languages
- cpp
- copy-control
stage_binding: 3 rough
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- copy_control
- code_duplication
- class_design
cross_links:
- rel: related_to
  target_object_id: PAT_copy_all_members_and_base_parts
- rel: related_to
  target_object_id: AP_write_copy_control_for_a_resource_owning_class
reference:
  source_title: 'Effective C++, Third Edition: 55 Specific Ways to Improve Your Programs and Designs'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Don't Implement One Copying Function in Terms of the Other

## Pattern Rule
**IF** a class must define both copy construction and copy assignment and their implementations appear duplicated
**THEN** share value-level operations or representation helpers while preserving each lifecycle contract; do not force one member through the other unless the object first reaches a valid state and the cost and guarantee are intentional.

## Do
- Prefer the Rule of Zero: let value-like members perform copying so both special members can be defaulted or omitted.
- When custom deep copying is required, extract a helper that *produces a value or owned representation* rather than one that mutates a partly formed object. Construction can initialize from that result; assignment can prepare a replacement before committing it.
- Recognize copy-and-swap as deliberate reuse of copy construction by copy assignment: construct a complete temporary from the source, then non-throwingly swap it with the target. The temporary, not the already-existing target, is what is copy-constructed.
- A delegating copy constructor may initialize the object through another constructor and then assign, but use it only when that initialized state is a valid and acceptably efficient starting point. It is not a substitute for direct member initialization by default.

## Don't
- Don't try to reconstruct the target object in place by directly invoking a constructor. Create a separate value and commit it, or assign its members under the normal lifetime rules.
- Don't run assignment logic against members whose lifetimes or invariants have not been established. A delegating constructor makes assignment technically possible by completing another constructor first; it does not make the extra initialization or weaker exception behavior free.
- Don't extract a mutation helper that assumes both construction-time and assignment-time invariants without stating which state is valid on entry.

## Checklist
- Can the special members be defaulted by moving ownership into value-like members?
- Does shared logic create a complete representation, or does it depend on a partially initialized object?
- If copy-and-swap or constructor delegation is used, are its extra work and exception guarantee appropriate?
- Have I avoided reconstructing an already-existing object or mutating one whose invariant is not established?

## Notes
The original warning protects two different lifetime phases, but “never reuse one from the other” is too absolute for modern C++. Copy-and-swap correctly lets assignment reuse copy construction by creating a separate complete object. Delegating constructors can also establish a valid object before a constructor body assigns to it. The durable rule is to preserve invariants and lifetime: default value-like members where possible, otherwise share representation-producing work, and use a complete temporary when assignment should have commit-or-rollback behavior.
