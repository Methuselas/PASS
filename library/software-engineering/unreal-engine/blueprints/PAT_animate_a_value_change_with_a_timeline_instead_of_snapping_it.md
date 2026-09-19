---
object_id: PAT_animate_a_value_change_with_a_timeline_instead_of_snapping_it
object_type: pattern
name: Animate a Value Change with a Timeline Instead of Snapping It
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
- timeline
- animation
- camera
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Animate a Value Change with a Timeline Instead of Snapping It

## Pattern Rule
**IF** a gameplay value — a camera's field of view, a rotation, a position — should change over time rather than jump from one value to another
**THEN** drive it with a Timeline: a track with a start keyframe and an end keyframe over a short duration, played on the trigger and reversed on the release, with the track's Update pin feeding the value into the setter every frame.

## Do
- Add a Timeline node and give it a track of the value's type (a Float track for a numeric value such as a field of view).
- Place a keyframe at time 0 with the starting value and a keyframe at the end of the duration with the target value, and set the timeline's Length to the duration of the transition.
- Connect the trigger's Pressed (or the event that starts the change) to the Timeline's Play pin, and the Timeline's Update pin to the setter, with the track's value pin feeding the setter's value input.
- Connect the release event to the Timeline's Reverse pin so the value returns smoothly to the starting value.

## Don't
- Don't set the value directly on the trigger — the camera snaps from one value to the other, which is jarring for the player.
- Don't use a Timeline for complex, character-based, or cinematic animation — that is what the engine's Sequencer is for; a Timeline is for simple value changes.
- Don't forget the release path — without it the value changes in one direction and never comes back.

## Checklist
- The value changes gradually over the duration rather than snapping.
- The Timeline's Update pin drives the setter, and the track's value pin feeds the setter's value input.
- Releasing the input reverses the transition back to the starting value.

## Notes
A Timeline changes a value over a designated amount of time: a track holds keyframes (time, value) pairs, and the Update pin fires every frame with the current value, which is fed into the setter. The advantage over setting the value directly is a gradual transition instead of a jarring switch. Timelines are for simple value changes such as a camera's field of view or a door's rotation; complex, character-based, or cinematic animation belongs to the engine's built-in animation system (Sequencer).
