---
object_id: PAT_validate_class_references_and_containers_before_use
object_type: pattern
name: Validate Class References and Containers Before Use
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
- class_reference
- containers
- null_safety
- defensive_programming
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

# Validate Class References and Containers Before Use

## Pattern Rule
**IF** you are about to use a class reference variable or a container variable that may not have been assigned
**THEN** validate the assumption that the next operation actually requires — use Is Valid Class for a class reference that may be unassigned, and check a container for emptiness before an operation that requires at least one element.
**ELSE** where the reference assignment or the container precondition is already guaranteed, do not add a redundant guard.

## Do
- Run Is Valid Class on a class reference before spawning from it or calling through it.
- Run IS NOT EMPTY on an array, set, or map before an operation that assumes at least one element, such as choosing or indexing an element.
- Combine multiple checks with an AND node and route the combined result through a Branch, so the action happens only when every input is valid.

## Don't
- Don't spawn from a class reference that may be None — validate it first.
- Don't perform an element-dependent container operation when the container may be empty.
- Don't assume a variable set in the Level Editor was set — an unassigned reference is None and an unassigned container is empty.

## Checklist
- Every class reference use is behind an Is Valid Class branch.
- Every container operation that requires an element is protected by an emptiness precondition unless non-emptiness is already guaranteed.
- Multiple prerequisites are combined with AND before the Branch.

## Notes
This extends defensive validation to class references and container preconditions. Class references are validated with Is Valid Class when they may be unassigned. Containers are different: emptiness is not inherently an error, so IS NOT EMPTY belongs only in front of operations whose contract requires at least one element.
