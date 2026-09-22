---
object_id: DRILL_rewire_one_niagara_sender_receiver_system_across_death_collision_and_location_events
object_type: drill
name: Rewire One Niagara Sender-Receiver System across Death, Collision, and Location
  Events
library_path:
- software-engineering
- unreal-engine
- vfx
- niagara
stage_binding: 3 rough
lane_fit: teach
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- niagara
- vfx
cross_links: []
reference:
  source_title: Build Stunning Real-time VFX with Unreal Engine 5
  author: Hrishikesh Andurlekar
confidence: high
references: []
variants: []
target_skill: Practice Niagara emitter communication by reusing one sender/receiver
  System with three event triggers.
---

# Rewire One Niagara Sender-Receiver System across Death, Collision, and Location Events

## Practice Task
Practice Niagara emitter communication by reusing one sender/receiver System with three event triggers.

## Target Skill
Practice Niagara emitter communication by reusing one sender/receiver System with three event triggers.

## Setup
Use a disposable test project or duplicate Niagara assets so the exercise can be repeated without damaging production content.

## Instructions
1. Configure the sender for the event prerequisites.
2. Wire a Death Event and verify receiver particles spawn when sender particles die.
3. Replace it with a Collision Event and verify receiver response at impact.
4. Replace it with a Location Event and verify the receiver follows sender positions as a trail.
5. For each variant, update both the sender Generate module and the receiver Event Handler source/response.

## Success Check
The same System correctly demonstrates death-, collision-, and location-driven receiver behavior.

## Common Failures
- Changing only the receiver while leaving the sender event type stale.
- Ignoring CPU/Persistent-ID event prerequisites.

## Notes
Use visible behavior and the Niagara/Blueprint interfaces named in the task as evidence; do not grade by expected theory alone.
