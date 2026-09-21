---
object_id: PAT_render_many_copies_of_a_mesh_with_an_instanced_static_mesh_component
object_type: pattern
name: Render Many Copies of a Mesh With an Instanced Static Mesh Component
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
- instanced_static_mesh
- procedural_generation
cross_links:
- rel: related_to
  target_object_id: PAT_generate_repeated_level_content_in_the_construction_script
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Render Many Copies of a Mesh With an Instanced Static Mesh Component

## Pattern Rule
**IF** a level needs many copies of the same static mesh (a field of bushes, a grid of props, repeated scenery)
**THEN** add an Instanced Static Mesh component and add each copy with the Add Instance function using an Instance Transform, because the component is optimized to render multiple copies of the same mesh in the level.

## Do
- Set the Static Mesh on the Instanced Static Mesh component before adding any instances, so every instance inherits that mesh.
- Call Add Instance once per copy, feeding each a distinct Instance Transform (location, rotation, scale) so the copies land where you want them.
- Choose the Hierarchical Instanced Static Mesh component instead when the mesh has a Level of Detail, so distant copies fall back to a cheaper LOD.
- Keep the mesh reference in an Instance Editable variable so each placed instance can swap to a different mesh in the Level Editor.

## Don't
- Don't place each identical copy as its own Static Mesh component or Actor — that defeats the instancing optimization and bloats the scene.
- Don't leave the component's mesh unset and expect Add Instance to pick one up; the mesh is set on the component, and each instance inherits it.

## Checklist
- The level shows the expected number of mesh copies coming from a single Instanced Static Mesh component.
- Each copy sits at its intended transform.
- Swapping the mesh on one placed instance (via the Instance Editable variable) changes only that instance.

## Notes
Instanced rendering batches many copies of one mesh together, which is why it is the right tool for repeated scenery rather than a pile of individual mesh components. The component holds the mesh plus a list of instance transforms; Add Instance appends to that list. Pairing it with the Construction Script lets a level designer tune the layout per placed instance without opening the Blueprint.
