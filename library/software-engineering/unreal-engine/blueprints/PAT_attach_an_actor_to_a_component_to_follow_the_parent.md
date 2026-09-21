---
object_id: PAT_attach_an_actor_to_a_component_to_follow_the_parent
object_type: pattern
name: Attach an Actor to a Component to Follow the Parent
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
- attach
- component
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Attach an Actor to a Component to Follow the Parent

## Pattern Rule
**IF** you need one actor to follow the transform of a component on another actor (for example, equip a shield on an arm)
**THEN** use the AttachActorToComponent node to attach the actor to the component.

## Do
- Set the Parent to the component to attach to.
- Optionally set the Socket Name to attach at a specific socket (for example, LeftArmSocket).
- Let the transformations of the Parent component affect the attached actor.

## Don't
- Don't manually copy the parent's transform to the actor every frame when attachment will keep them together.

## Checklist
- The actor is attached to the parent component with AttachActorToComponent.
- A socket name is used when the attachment point is a specific socket.
- The attached actor follows the parent component's transformations.

## Notes
The transformations of the Parent component affect the attached actor. Example: an Equip Shield custom event that attaches a Shield Actor to a Skeletal Mesh component at the LeftArmSocket, positioning the shield on the arm.
