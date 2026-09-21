---
object_id: PAT_choose_an_animation_sequence_or_blend_space_by_blending_need
object_type: pattern
name: Choose an Animation Sequence or a Blend Space by the Blending Need
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
- animation_sequence
- blend_space
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Choose an Animation Sequence or a Blend Space by the Blending Need

## Pattern Rule
**IF** you are choosing the animation asset that plays a character's motion
**THEN** use an Animation Sequence when the motion is a single fixed clip, and a Blend Space when the motion must blend between clips based on one or two parameter values such as speed.

## Do
- Author or import the Animation Sequence's keyframes (bone transformations at specific times) so the clip plays as a single animation on the Skeletal Mesh.
- Build the Blend Space by mapping each member Animation Sequence to a parameter value, so the engine blends between the members as the parameter changes.
- Drive the Blend Space parameter from a live value (for example, the character's speed) so the blend tracks the character's state.

## Don't
- Don't use a Blend Space for a motion that never blends — it adds a parameter and member clips you do not need.
- Don't fake a blend by switching between separate Animation Sequences at thresholds — the Blend Space blends continuously instead of snapping.

## Checklist
- A single fixed clip plays from an Animation Sequence.
- A parameter-driven motion plays from a Blend Space whose member clips are mapped to parameter values.
- The Blend Space parameter is fed by the live value it represents.

## Notes
An Animation Sequence is one clip: keyframes that specify bone transformations at specific times, played as a single animation on a Skeletal Mesh. A Blend Space is an asset type that blends animations based on one or two parameter values; each member Animation Sequence is mapped to a parameter value, and the engine blends between the members as the parameter moves. A one-parameter Blend Space (for example, Speed) blends idle, walk, and run into a continuous locomotion, which is why locomotion is usually a Blend Space while a one-off action is an Animation Sequence.
