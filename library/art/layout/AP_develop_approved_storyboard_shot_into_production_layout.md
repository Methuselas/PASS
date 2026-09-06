---
object_id: AP_develop_approved_storyboard_shot_into_production_layout
object_type: ap
name: Develop Approved Storyboard Shot Into Production Layout
library_path:
- art
- layout
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: none
tags:
- layout
- animation
- storyboard
- scene_planning
- perspective
- handoff
cross_links:
- rel: supports
  target_object_id: PAT_pose_out_approved_storyboard_action_into_layout_without_reauthoring_scene
- rel: supports
  target_object_id: PAT_preserve_established_scene_geography_while_cheating_minor_details_for_clarity
- rel: supports
  target_object_id: PAT_use_3d_spatial_proxy_to_preserve_complex_environment_design_across_views
- rel: supports
  target_object_id: PAT_translate_reference_prop_into_project_shape_language_without_losing_identity
- rel: supports
  target_object_id: PAT_decompose_animation_scene_into_registered_level_stack_for_independent_control
- rel: supports
  target_object_id: PAT_separate_animating_environment_elements_from_static_background_for_independent_motion
- rel: supports
  target_object_id: PAT_register_character_occlusion_with_shared_matchline_or_overlay
- rel: supports
  target_object_id: PAT_create_motion_parallax_by_separating_panning_layers_by_depth_and_speed
- rel: supports
  target_object_id: PAT_build_repeat_pan_from_seamless_cycle_and_nonrevealing_landmarks
- rel: supports
  target_object_id: PAT_treat_layout_as_annotated_working_drawing_for_downstream_departments
- rel: related_to
  target_object_id: AP_develop_storyboard_sequence_in_progressive_directing_passes
- rel: related_to
  target_object_id: AP_construct_a_shared_scene_perspective_field
- rel: related_to
  target_object_id: AP_package_approved_layout_into_executable_scene_plan
reference:
  source_title: The Art of Layout and Storyboarding
  author: Mark T. Byrne
confidence: high
references: []
variants: []
---

# Develop Approved Storyboard Shot Into Production Layout

## Objective
Turn an approved storyboard shot into a production layout whose action, camera, geography, perspective, separations, and technical annotations are specific enough for downstream departments to execute without silently re-directing the scene.

## Steps / Flow
1. **Enter from approved story intent.** Begin with an approved storyboard shot or sequence decision, known camera intent, approved character/environment design authority, and any continuity constraints. If the action, shot purpose, or camera idea is still being authored, return to the storyboard/directing action instead of hiding story changes inside Layout.
2. **Preserve the audience's spatial map.** Use `PAT_preserve_established_scene_geography_while_cheating_minor_details_for_clarity` when the location has already been established. Keep major anchors and relationships stable; allow only local cheats that improve the shot without changing the audience's mental map.
3. **Establish trustworthy shot space before detail.** Use the approved perspective field when one exists; when the shot requires a new coherent perspective construction, route that sub-action to `AP_construct_a_shared_scene_perspective_field` before later placement depends on it. For complex recurring environments whose consistency is difficult to maintain across views, use `PAT_use_3d_spatial_proxy_to_preserve_complex_environment_design_across_views` as a spatial aid without letting the proxy redesign the approved shot.
4. **Pose the approved action into the final space.** Use `PAT_pose_out_approved_storyboard_action_into_layout_without_reauthoring_scene` to fit character scale, pose, contact, attitude, and staging to the production geometry while preserving the storyboard's intended action and dramatic function. If the layout can only work by changing that intent, stop and return the conflict to Storyboarding rather than solving it locally.
5. **Translate reference-bound props only where needed.** When literal or photographic objects must belong to the project's designed world, use `PAT_translate_reference_prop_into_project_shape_language_without_losing_identity`; preserve recognizability and function while fitting the established shape language.
6. **Plan independent scene control.** Use `PAT_decompose_animation_scene_into_registered_level_stack_for_independent_control` to decide which approved elements require independent motion, hold, occlusion, reuse, exposure, effects, or compositing control. When an environmental element itself animates independently, use `PAT_separate_animating_environment_elements_from_static_background_for_independent_motion` rather than burying it in the static background.
7. **Resolve occlusion at the shared boundary.** Use `PAT_register_character_occlusion_with_shared_matchline_or_overlay` whenever separately produced character, effects, or background art must pass behind or in front of the same environmental edge. Do not leave hide/reveal geometry for departments to guess independently.
8. **Branch for moving-background depth.** If the shot needs temporal depth from separately moving environment layers, use `PAT_create_motion_parallax_by_separating_panning_layers_by_depth_and_speed`. If sustained travel also requires a cycling background, use `PAT_build_repeat_pan_from_seamless_cycle_and_nonrevealing_landmarks` and test the loop in motion rather than approving a seam from a still frame alone.
9. **Make the layout usable as production information.** Use `PAT_treat_layout_as_annotated_working_drawing_for_downstream_departments` to record the construction, registrations, paths, camera states, effect directions, and concise notes that must survive handoff. Keep final rendering subordinate to readability and do not make downstream design decisions that Layout does not own.
10. **Run the approval gate and recover to the owner.** Check the developed layout against the approved storyboard action, camera intent, scene geography, perspective, character contacts, separations, occlusions, and moving-background behavior. Route any failure back to the step and Pattern or subordinate AP that owns it instead of compensating downstream.
11. **Complete on approved executable layout.** Stop when the shot preserves its approved story/directing intent, all spatial and production relationships are trustworthy, and the layout is ready to be passed to `AP_package_approved_layout_into_executable_scene_plan` without requiring new craft decisions during packaging.

## Notes
This AP owns the order, gates, branch points, recovery, and stopping condition of animation layout development. The individual craft decisions remain in their Pattern owners. Storyboard development and perspective-field construction remain separate actions because Layout should consume their approved results rather than silently becoming a second owner of directing or general perspective construction.
