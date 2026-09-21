---
object_id: PAT_deform_a_static_mesh_along_a_two_point_spline_with_a_spline_mesh_component
object_type: pattern
name: Deform a Static Mesh Along a Two-Point Spline With a Spline Mesh Component
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
- spline_mesh
- procedural_generation
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Deform a Static Mesh Along a Two-Point Spline With a Spline Mesh Component

## Pattern Rule
**IF** a static mesh needs to be bent or stretched along a curve (a curved pipe, a ribbon following an arc)
**THEN** use a Spline Mesh component, which deforms the mesh along a two-point spline, and set the spline's start and end (positions and tangents) either in the Level Editor or with the Set Start and End function in the Construction Script.

## Do
- Assign the static mesh to deform on the Spline Mesh component, so the component knows which mesh to bend.
- Set the two spline points (start and end positions and tangents) in the Level Editor for a designer-tuned curve, or drive them from the Construction Script with Set Start and End for a scripted curve.
- Leave Update Mesh enabled so the component rebuilds the deformed mesh when the spline changes.

## Don't
- Don't reach for a Spline Mesh component to place many copies along a path — that is the Spline component's job; Spline Mesh deforms a single mesh between two points.
- Don't hand-compute the tangents for a multi-segment curved pipe; the two-point Spline Mesh handles a single arc, and chaining many segments needs tangent math beyond this component.

## Checklist
- The mesh visibly bends between the two spline points.
- Moving a spline point in the Level Editor re-deforms the mesh.
- The deformed mesh is a single component, not a row of separate instances.

## Notes
A Spline Mesh component is different from a Spline component: it does not place copies along a path, it deforms one mesh to span the two points of a short spline. The Set Start and End function exposes the start/end positions and tangents so the curve can be defined from Blueprint (for example in the Construction Script) instead of only by hand in the editor. It is the tool for a single curved piece such as a pipe elbow; building a long curved pipe from many segments requires computing the tangents between segments, which is a separate, more mathematical task.
