---
object_id: PAT_add_metallic_and_roughness_to_give_a_material_substance
object_type: pattern
name: Add Metallic and Roughness to Give a Flat Material Substance
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
cross_links:
- rel: related_to
  target_object_id: PAT_author_a_material_by_wiring_parameter_nodes_to_input_pins
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Add Metallic and Roughness to Give a Flat Material Substance

## Pattern Rule
**IF** a Material looks flat and unrealistic because it only sets a Base Color
**THEN** add values to the Metallic and Roughness inputs (via ScalarParameter nodes) to give the surface reflectiveness and depth.

## Do
- Add a ScalarParameter node, set its Default Value to a small number (0.1) so the effect stays subtle, and name it Metallic.
- Wire the Metallic node's output to the Metallic input pin on the result node.
- Duplicate the Metallic node (right-click > Duplicate) to make a second ScalarParameter, rename it Roughness, keep the same small default, and wire it to the Roughness input pin.

## Don't
- Don't ship a flat single-color Material when the surface should read as a real 3D object — Base Color alone gives no reflectiveness or depth.
- Don't crank Metallic or Roughness to large values to make the surface pop; keep them subtle so they add depth without overwhelming the color.

## Checklist
- The Material has both a Metallic and a Roughness input connected to ScalarParameter nodes.
- The surface shows reflectiveness and depth rather than a flat single color.
- The Metallic and Roughness values are small enough to stay subtle.

## Notes
Flat single-color Materials make 3D objects look unrealistic. Setting values for the Metallic and Roughness inputs adds reflectiveness and depth to the surface. Small values (around 0.1) keep the effect subtle so it adds a sense of a real surface without changing the base color.
