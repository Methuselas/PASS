---
object_id: PAT_drive_periodic_behavior_with_a_looping_timer
object_type: pattern
name: Drive Periodic Behavior with a Looping Timer
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
- periodic_behavior
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

# Drive Periodic Behavior with a Looping Timer

## Pattern Rule
**IF** you need an Actor to do something on a fixed schedule — reverse direction every few seconds, pulse, re-target
**THEN** use a looping timer that fires a custom event on each interval, set up once in BeginPlay.

## Do
- Create a custom event for the periodic action (for example, ChangeDirection) and wire its body to the action you want repeated.
- Add a Set Timer by Event node, check its Looping parameter, and connect the custom event to its Event input.
- Set the timer's Time input to the interval (a variable such as TimeToChange) and call the timer from Event BeginPlay so it starts when the game begins.
- To reverse a direction on each tick, multiply the direction vector by -1 and write the result back to the direction variable.

## Don't
- Don't count frames in Event Tick to schedule the action — a timer decouples the schedule from the frame rate and keeps the Tick graph clean.
- Don't forget the Looping parameter — without it the timer fires once and the periodic behavior stops.
- Don't start the timer in the Event Graph's default flow — call it from BeginPlay so it begins when the Actor is in play.

## Checklist
- The periodic action fires at the intended interval for the whole time the game runs, not just once.
- The timer is set up in BeginPlay and its Looping parameter is checked.
- The interval is a variable, so the schedule can be tuned without rewiring the graph.

## Notes
A looping timer (Set Timer by Event with Looping checked) fires its event on a fixed schedule independent of the frame rate, which is the clean way to do periodic behavior. The custom event holds the action to repeat, so the timer only schedules and the event only acts. For a back-and-forth patrol, the periodic action inverts the direction vector (multiply by -1), so the Actor alternates between the two directions on each interval.
