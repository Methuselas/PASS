---
object_id: PAT_switch_the_active_camera_with_set_view_target_with_blend
object_type: pattern
name: Switch the Active Camera With Set View Target with Blend
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
- camera
- view_target
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Switch the Active Camera With Set View Target with Blend

## Pattern Rule
**IF** you need to switch the game's view between different cameras
**THEN** use the Set View Target with Blend function on the Player Controller.

## Do
- Set the New View Target to the actor to view, usually a camera.
- Set the Blend Time (and optionally the Blend Func and Blend Exp) to control the transition.

## Don't
- Don't move the player or the camera actor to fake a view change — set the view target instead.

## Checklist
- The view switch uses Set View Target with Blend on the Player Controller.
- The New View Target is the camera (or actor) to view.
- The blend time controls the transition.

## Notes
The blend is what makes the camera change smooth rather than a hard cut: the view transitions over the Blend Time. Example: a Level Blueprint event that switches the game view to the camera in a treasure room when the player enters it.
