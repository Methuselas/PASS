---
object_id: PAT_check_the_goal_condition_when_the_tracked_counter_changes
object_type: pattern
name: Check the Goal Condition When the Tracked Counter Changes
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 0 design
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- win_condition
- goal
- counter
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Check the Goal Condition When the Tracked Counter Changes

## Pattern Rule
**IF** the player wins (or reaches a goal) when a tracked count reaches a target — destroy N targets, collect M items
**THEN** evaluate the goal (count >= target) at the moment the count changes, not by polling on a timer or tick: increment the count first, then check the goal.

## Do
- Store the goal as a value (e.g., an Integer variable for the target count) and track progress in a counter.
- At the point where the counter is incremented (the event that destroys a target, collects an item), call a check that compares the counter to the goal.
- Increment the counter before the check, so the check sees the updated value.
- On a true result, trigger the end state (show the win screen, end the game).

## Don't
- Don't poll the goal on Event Tick or a timer; check it when the count actually changes, so it is evaluated exactly when it can become true.
- Don't check the goal before incrementing the counter; the check would see the old value and miss the win.
- Don't hard-code the goal into the check; store it as a value so it can be tuned.

## Checklist
- The goal is stored as a value and progress is tracked in a counter.
- The check runs at the point where the counter is incremented.
- The counter is incremented before the check.
- A true result triggers the end state.

## Notes
A win condition is a comparison between a tracked count and a target. Evaluating it at the moment the count changes — rather than polling — means it is checked exactly when it can become true, and no more often. The order matters: increment first, then check, so the comparison sees the new value. A short delay before the end state (a beat for the last effect to play) is a tuning choice, not part of the condition itself.
