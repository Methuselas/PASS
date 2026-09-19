---
object_id: PAT_swap_an_actors_material_at_runtime
object_type: pattern
name: Swap an Actor's Material at Runtime
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
- materials
- runtime
cross_links:
- rel: related_to
  target_object_id: PAT_model_an_actors_surface_look_as_a_swappable_material_asset
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Swap an Actor's Material at Runtime

## Pattern Rule
**IF** you need to change how an Actor looks while the game is running — for example, marking a target the moment it is hit
**THEN** swap the Material on the Actor's mesh component at runtime, triggered by the event that should cause the change.

## Do
- Use the Set Material (StaticMeshComponent) node and set its Material input to the target Material asset through the asset picker.
- Wire the triggering event (such as Event Hit) to the node's execution input so the swap fires the moment the event fires.
- Leave the node's Target pointing at the mesh component that carries the look, and keep the mesh geometry untouched.

## Don't
- Don't swap the mesh or edit the geometry to change the look — the surface appearance lives in the Material, and changing the mesh loses the swap.
- Don't leave the Material input empty and expect an effect — the action fires but produces no observable change.

## Checklist
- Firing the triggering event changes the Actor's appearance to the target Material while the mesh geometry stays the same.
- The Set Material node's Material input holds the intended Material asset, not an empty slot.
- The swap happens at runtime, not only in the editor.

## Notes
Set Material replaces the Material currently applied to a mesh component at runtime, so an Actor's look can change in response to gameplay. It is the runtime half of treating the look as a swappable Material asset: the asset holds the look, and Set Material is the action that swaps it on the component when an event fires.
