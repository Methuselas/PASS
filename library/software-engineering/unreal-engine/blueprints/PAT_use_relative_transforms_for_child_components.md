---
object_id: PAT_use_relative_transforms_for_child_components
object_type: pattern
name: Use Relative Transforms for Child Components
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
- transforms
- components
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Use Relative Transforms for Child Components

## Pattern Rule
**IF** you are positioning a component that should follow its parent — a weapon on a character, a statue on a table, a light on a sconce
**THEN** set its transform relative to the parent, so moving the parent moves the child with it, and reach for world transforms only when you need an absolute position in the level.

## Do
- Use the component's relative location and rotation for children that should follow their parent; the child's transform is relative to its parent's transform.
- Use the world location (GetWorldLocation / SetActorLocation) when you need an absolute position in the level, independent of any parent.
- Remember the hierarchy: the root scene component stores the actor's world position, and each child's transform is relative to the one above it.

## Don't
- Don't drive a child that should follow its parent with a world transform; it will stop tracking the parent when the parent moves.
- Don't assume that changing a child's relative transform moves the parent; it only moves the child (and anything below it).
- Don't confuse the actor's world transform with a component's relative transform; they live in different frames.

## Checklist
- A child that should follow its parent uses a relative transform.
- An absolute position uses a world transform.
- Moving the parent moves the child; changing the child's relative transform does not move the parent.

## Notes
An actor's Transform structure holds Location, Rotation, and Scale in world space. When the actor has components, each component's transform is relative to its parent: the root scene component holds the actor's world position, and each child is positioned relative to the one above it. So a statue parented to a table moves when the table moves, but adjusting the statue's relative transform leaves the table where it is. Use relative transforms for children that should track their parent, and world transforms when you need an absolute level position.
