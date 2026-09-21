---
object_id: PAT_separate_the_skeleton_from_the_skeletal_mesh_to_share_animation
object_type: pattern
name: Separate the Skeleton from the Skeletal Mesh to Share Animation
library_path:
- software-engineering
- unreal-engine
- blueprints
- animation
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- animation
- skeleton
- skeletal_mesh
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Separate the Skeleton from the Skeletal Mesh to Share Animation

## Pattern Rule
**IF** you are organizing character animation assets and want several meshes to reuse the same animations
**THEN** keep the Skeleton as a separate asset from the Skeletal Mesh, because the animation is done on the Skeleton and every Skeletal Mesh linked to that Skeleton can play the same animations.

## Do
- Author the bone hierarchy in a Skeleton asset, then link each Skeletal Mesh to that Skeleton.
- Point multiple Skeletal Meshes at the same Skeleton so they all share its Animation Sequences and Blend Spaces.
- Adjust a bone's position and rotation in the Skeleton Editor to fix the rig for every mesh that uses it.

## Don't
- Don't bake the skeleton into each mesh — a per-mesh skeleton means each mesh needs its own copy of every animation.
- Don't expect a Skeletal Mesh to carry its own animation; the animation lives on the Skeleton it is linked to.

## Checklist
- The Skeleton is a standalone asset with its own bone hierarchy.
- Each Skeletal Mesh is linked to the Skeleton.
- More than one Skeletal Mesh can play the same Animation Sequence from the shared Skeleton.

## Notes
A Skeleton is a hierarchy of interconnected bones used to animate the polygon vertices of a Skeletal Mesh. In Unreal Engine the two are separate assets: the Skeleton holds the rig and the animation, and the Skeletal Mesh is the visual representation linked to it. Because the animation is done on the Skeleton, one Skeleton can drive several Skeletal Meshes, so the animation work is done once and reused across every mesh that shares the rig.
