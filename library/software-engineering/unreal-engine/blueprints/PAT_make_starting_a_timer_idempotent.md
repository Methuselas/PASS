---
object_id: PAT_make_starting_a_timer_idempotent
object_type: pattern
name: Make Starting a Timer Idempotent
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
- timers
cross_links:
- rel: related_to
  target_object_id: PAT_drive_periodic_behavior_with_a_looping_timer
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Make Starting a Timer Idempotent

## Pattern Rule
**IF** an action that can be triggered repeatedly — a key press, a click — starts a periodic timer
**THEN** check whether the timer already exists before starting it, and start it only if it does not, so repeated triggers do not stack multiple timers.

## Do
- After the setup actions, add a Branch on Does Timer Exist by Function Name.
- On the True branch (the timer is already running), exit without starting another.
- On the False branch, start the timer with Set Timer by Function Name.

## Don't
- Don't start the timer unconditionally on every trigger — holding or re-pressing the input stacks timers, and the periodic action fires multiple times per interval.
- Don't assume the input fires only once; a held key or a rapid re-press re-enters the start path.

## Checklist
- Re-triggering the action while the timer is running does not start a second timer.
- The start path branches on Does Timer Exist by Function Name.
- The periodic action fires at the intended rate, not a multiple of it.

## Notes
A start path that unconditionally calls Set Timer by Function Name is not safe against re-entry: if the player holds the sprint key or presses it again, the start path runs again and a second timer is created, so the periodic action fires twice as fast. Branching on Does Timer Exist by Function Name and starting the timer only on the False branch makes the start idempotent — calling it any number of times leaves exactly one timer running.
