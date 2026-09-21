---
object_id: PAT_use_a_validated_get_to_branch_on_a_reference_validity
object_type: pattern
name: Use a Validated Get to Branch on a Reference's Validity
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- object_reference
- null_safety
- validated_get
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

# Use a Validated Get to Branch on a Reference's Validity

## Pattern Rule
**IF** you are reading an object reference from a variable and need to branch on whether it is valid
**THEN** convert the Get node to a Validated Get and route execution through its Is Valid or Is Not Valid pins, so the read and the validity branch happen in one node.

## Do
- Right-click an Object Reference Get node and choose Convert to Validated Get.
- The node becomes a GET node with Is Valid and Is Not Valid execution pins in addition to the reference value.
- Continue on the Is Valid pin only when the reference is valid; route the Is Not Valid pin to a safe no-op or cleanup.

## Don't
- Don't read the reference and then run a separate Is Valid check when a Validated Get gives you both in one node — the extra node is redundant.
- Don't continue on the Is Not Valid pin as if the reference were usable — that branch means the reference is null.

## Checklist
- The Get node is a Validated Get with Is Valid and Is Not Valid execution pins.
- The valid work runs only on the Is Valid pin.
- The Is Not Valid pin does nothing harmful (no-op, cleanup, or re-acquisition).

## Notes
A Validated Get is a Get node that has been converted to carry execution pins for the reference's validity. It combines reading the reference and branching on its validity into a single node, which is convenient when the reference comes from a variable that may not have been assigned (for example, a spawned actor reference that is destroyed before you clean it up). It is the node-level counterpart to the standalone Is Valid check: both guard against using a null reference, but the Validated Get does it at the point where the reference is read.
