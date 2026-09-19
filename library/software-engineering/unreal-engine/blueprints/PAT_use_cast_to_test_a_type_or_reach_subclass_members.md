---
object_id: PAT_use_cast_to_test_a_type_or_reach_subclass_members
object_type: pattern
name: Use Cast To to Test a Type or Reach Subclass Members
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- casting
- type_safety
cross_links:
- rel: related_to
  target_object_id: PAT_guard_object_references_with_is_valid
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Use Cast To to Test a Type or Reach Subclass Members

## Pattern Rule
**IF** you hold a base-class reference and need to confirm the instance is a specific type, or to access variables and functions defined only in a subclass
**THEN** use the Cast To node to narrow the reference to the subclass, because a base-class reference only exposes the base class's members even when the instance is actually a subclass.

## Do
- Use Cast To as a safe type test: cast the reference (for example, the Other Actor from an overlap event) to the expected type and branch on success to confirm the instance is that type.
- Use Cast To to reach subclass members: a base-class reference such as the one returned by Get Game Mode (typed GameModeBase) only exposes the base class's members, so cast it to the subclass to access the subclass's variables and functions.
- Connect the Cast To node's narrowed-reference output to the nodes that use it, and route the Cast Failed branch to a safe no-op.

## Don't
- Don't assume a base-class reference exposes subclass members — it only knows the variables and functions defined in the base class.
- Don't ignore the Cast Failed branch — the instance may not be the type you expect, and the cast will not succeed.

## Checklist
- A base-class reference that needs subclass members is cast to the subclass before those members are used.
- A type test uses Cast To and branches on the success and failure outputs.
- The Cast Failed branch does nothing harmful.

## Notes
A base-class reference only knows the members defined in the base class, even when the instance it points to is actually a subclass. Cast To narrows the reference to the subclass, exposing its variables and functions, and it succeeds only if the instance is actually that type. It serves two purposes: a safe type test (is this instance the type I expect?) and member access (reach the subclass's variables and functions that the base-class reference cannot see).
