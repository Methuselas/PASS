---
object_id: PAT_use_a_scene_component_as_a_reference_location_for_other_components
object_type: pattern
name: Use a Scene Component as a Reference Location for Other Components
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
- scene_component
- transform
- attach
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Use a Scene Component as a Reference Location for Other Components

## Pattern Rule
**IF** you need a movable pivot or reference location that other components can follow
**THEN** create a Scene Component — a child class of Actor Component that has a Transform — as the pivot, and attach the other components to it so they follow its movement and rotation.

## Do
- Create a Blueprint with Scene Component as the Parent class; it has a Transform structure (location, rotation, and scale) that an Actor Component lacks.
- Attach other components to it in the Components panel; the movement and rotation applied to the Scene Component affect the attached components.
- Attach the Scene Component to the Actor's root component (for example, the Capsule Component) so it follows the Actor.
- Set the Scene Component's relative location in the Details panel to position the pivot (for example, an x offset to place a shield beside the character).

## Don't
- Don't place a Scene Component directly in a Level — it must live inside an Actor.
- Don't attach components that should follow the pivot to the Actor instead of the Scene Component — they would not follow the pivot's movement.
- Don't expect the Actor's transform to come from a non-root component — the Actor's transform is obtained from its root Scene Component.

## Checklist
- The pivot is a Scene Component, not a plain Actor Component.
- The components that should follow the pivot are attached to it.
- The Scene Component is attached to the Actor's root component, and the Actor's transform comes from that root.

## Notes
A Scene Component is an Actor Component with a Transform, and the Transform is what makes it a usable pivot: because it has a location, rotation, and scale, it can be attached to another Scene Component, and components attached to it inherit its movement and rotation. You can build a hierarchy by attaching Scene Components to each other. An Actor needs a Scene Component designated as its root component, and the Actor's transform is obtained from that root. Example: a Scene Component that orbits an Actor carries a Static Mesh component that renders as a rotating shield.
