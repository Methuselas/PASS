---
object_id: PAT_choose_a_grab_attach_mode_by_how_the_object_is_held
object_type: pattern
name: Choose a Grab Attach Mode by How the Object Is Held
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
- motion_controller
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Choose a Grab Attach Mode by How the Object Is Held

## Pattern Rule
**IF** you are making an object grabbable so it attaches to a motion controller
**THEN** choose the grab type by how the object must be held: Free when it can be held any way, Snap when it has a clear grip position, Custom when you need bespoke logic, and None to disable grabbing without removing the component.

## Do
- Set the Grab Type on the grab component in the Details panel.
- Use Free for objects that do not need to be held in a certain way — the object attaches while keeping its relative location and orientation to the controller.
- Use Snap for objects with a clear grip location — the object snaps to a predefined location and rotation relative to the controller that grabbed it.
- Use Custom when you need your own grab behavior — the component exposes a bIsHeld boolean and OnGrabbed and OnDropped event dispatchers to build custom logic.
- Use None to disable grabbing on an actor without removing its grab component.

## Don't
- Don't use Snap for objects with no natural grip position — the object will snap to a place that feels wrong to hold.
- Don't remove the grab component to disable grabbing when None will do — None keeps the component so grabbing can be re-enabled.

## Checklist
- Each grabbable actor's grab component has a Grab Type set in the Details panel.
- Free objects keep their relative pose to the controller while held.
- Snap objects land on a predefined grip pose when picked up.
- Custom objects drive their behavior from bIsHeld and the OnGrabbed/OnDropped dispatchers.

## Notes
The grab type is an enumeration on the grab component that defines how the object attaches to the motion controller. The choice is driven by the object's grip: a cube that can be held any way is Free; a weapon with a handle is Snap; an object whose grab needs special handling (for example, a two-handed item or a tool that changes state on grab) is Custom. None is a soft off-switch that leaves the component in place.
