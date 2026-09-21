---
object_id: PAT_track_a_held_object_in_a_reference_variable_and_clear_it_on_release
object_type: pattern
name: Track a Held Object in a Reference Variable and Clear It on Release
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
- vr
- grab
- state
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

# Track a Held Object in a Reference Variable and Clear It on Release

## Pattern Rule
**IF** you are tracking which object each hand or controller is holding
**THEN** store the held object's component reference in a per-hand variable, clear it when the object is released, and clear the other hand's reference when the object is transferred to this hand.

## Do
- Keep one reference variable per hand (for example, Held Component Left and Held Component Right).
- On grab, disable the actor's physics (if enabled) and attach the actor to the controller, then store the grabbed component reference in the grabbing hand's variable.
- On release, detach the object from the controller and clear the releasing hand's variable.
- When a hand grabs an object the other hand was holding, clear the other hand's reference to it.
- Validate the held reference before using it (a held reference can be invalid after the object is destroyed).

## Don't
- Don't leave a stale reference in a hand's variable after the object is released or destroyed — later logic will act on an object that is no longer held.
- Don't let both hands claim the same object — when one hand takes it, the other hand's reference must be cleared.

## Checklist
- Each hand's held reference is set on grab and cleared on release.
- Transferring an object between hands clears the previous hand's reference.
- The held reference is validated before it is used.

## Notes
A held object is tracked by storing a reference to its grab component in a variable owned by the hand holding it. The reference is the link between the hand's input events (grab, release, trigger) and the object being held. Clearing it on release and on hand-to-hand transfer keeps the state honest: a hand's variable always names the object that hand actually holds, and nothing else. Because the held object can be destroyed while held, the reference must be validated before use.
