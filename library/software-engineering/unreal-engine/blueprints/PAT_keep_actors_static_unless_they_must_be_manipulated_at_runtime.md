---
object_id: PAT_keep_actors_static_unless_they_must_be_manipulated_at_runtime
object_type: pattern
name: Keep Actors Static Unless They Must Be Manipulated at Runtime
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
- mobility
- performance
cross_links:
- rel: related_to
  target_object_id: PAT_move_an_actor_per_frame_with_a_delta_time_scaled_offset
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Keep Actors Static Unless They Must Be Manipulated at Runtime

## Pattern Rule
**IF** you are deciding an Actor's Mobility
**THEN** keep it Static — the cheaper default — and set it to Movable only when the Actor must be manipulated at runtime.

## Do
- Leave placed Actors at their Static default; Static objects are significantly less resource-intensive to render.
- Set Mobility to Movable only when the Actor must move or be manipulated during gameplay.
- Make the change on the Actor's component: the Mobility toggle under TRANSFORM in the Details panel.

## Don't
- Don't set Movable "just in case" — you pay the render cost on every frame for every Actor that does not need it.
- Don't leave an Actor that must change at runtime Static and wonder why it will not move.

## Checklist
- Actors that do not change at runtime are Static.
- Actors that must move or be manipulated at runtime are Movable.
- The Movable setting is deliberate, not a leftover from a template.

## Notes
By default, basic Actors placed in the world are Static, which means they cannot move or be manipulated during gameplay. Static objects are significantly less resource-intensive to render, so Static is the default choice for non-interactive objects to maximize frame rates. Movable is a cost you pay only when the Actor must be manipulated at runtime — for example, an Actor that moves. Set it deliberately, per Actor, rather than flipping everything to Movable.
