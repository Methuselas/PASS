---
object_id: PAT_compose_blueprint_behavior_from_ready_components
object_type: pattern
name: Compose Blueprint Behavior from Ready Components
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: PAT_reuse_before_reinventing
tags:
- unreal_engine
- blueprints
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Compose Blueprint Behavior from Ready Components

## Pattern Rule
**IF** the behavior you need is already implemented by a ready-made component (rotation, movement, camera, collision, light, sound, particles)
**THEN** add and configure that component in the Components panel instead of writing event graph logic for it.

## Do
- Build the first version of a Blueprint from components alone before scripting anything — a Static Mesh component plus a Rotating Movement component yields a fully working rotating object with no events and no actions.
- Edit the selected component's properties in the Details panel and check its visual representation in the Viewport panel.
- Add scripted behavior only where no component expresses the behavior.

## Don't
- Don't write node logic for behavior a component already provides.
- Don't assume a component's default settings match your intent — read them; the Rotating Movement component, for instance, rotates the Blueprint around the z axis by default.

## Checklist
- The object exhibits the intended behavior in a play-in of the level while its Event Graph contains no nodes.
- After compile and save, dragging the Blueprint from the Content Browser into the level and pressing Play shows the component-driven behavior.

## Notes
Components are ready-to-use objects that can be added to a Blueprint; a Blueprint can gain real functionality purely from composing components. The Components panel exposes Static Mesh, Skeletal Mesh, lights, sounds, box collisions, particle systems, and cameras. The My Blueprint panel, where scripted elements (Variables, Macros, Functions, Graphs) live, is entered once a component does not cover the needed behavior.
