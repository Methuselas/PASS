---
object_id: PAT_model_an_actors_surface_look_as_a_swappable_material_asset
object_type: pattern
name: Model an Actor's Surface Look as a Swappable Material Asset
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- materials
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Model an Actor's Surface Look as a Swappable Material Asset

## Pattern Rule
**IF** you need to change how an Actor looks — its color, reflectiveness, or depth
**THEN** treat the look as a Material asset applied to the Actor's mesh and change the Material (or its parameters), not the mesh geometry.

## Do
- Create the Material as a standalone asset in the content browser (right-click in a folder > Material) so it can be applied to the mesh and swapped later.
- Change the Actor's appearance by swapping in a different Material or by editing the parameters of the one it already uses.
- Keep the mesh geometry fixed and let the Material carry the visual change, so the same mesh can wear many looks.

## Don't
- Don't edit the mesh geometry or the Actor's transform to change the look — the surface appearance lives in the Material, not the shape.
- Don't bake a one-off color into the mesh when a Material can carry it, or you lose the ability to swap the look later.

## Checklist
- Swapping or editing the Actor's Material changes its appearance while the mesh geometry stays the same.
- The same mesh can be given different looks by applying different Materials.
- The visual change is made in the Material, not in the mesh or the Actor's transform.

## Notes
A Material behaves like a coat of paint on the mesh: it determines the color and surface response, so the look lives in the Material rather than the shape. Keeping the look in a swappable asset is what lets you change an Actor's appearance at runtime by swapping its Material.
