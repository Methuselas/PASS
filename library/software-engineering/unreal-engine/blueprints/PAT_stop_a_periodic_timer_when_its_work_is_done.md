---
object_id: PAT_stop_a_periodic_timer_when_its_work_is_done
object_type: pattern
name: Stop a Periodic Timer When Its Work Is Done
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

# Stop a Periodic Timer When Its Work Is Done

## Pattern Rule
**IF** a periodic timer's work can finish — a meter reaches full, a queue empties, a target is reached
**THEN** clear the timer in the same tick that the work completes, so it stops firing instead of continuing to run with nothing to do.

## Do
- In the periodic action, test for the completion condition (for example, the meter is nearly equal to full).
- On the completion branch, call Clear Timer by Function Name with the timer's name.
- On the not-yet-complete branch, do one step of the work and let the timer fire again.

## Don't
- Don't let a finished timer keep firing — it wastes cycles and can re-trigger work that is already complete.
- Don't rely on the work being harmless once it is done; clear the timer so the periodic action stops.

## Checklist
- When the work completes, the timer is cleared in the same tick.
- After completion, the periodic action no longer fires.
- The completion test is part of the periodic action, not a separate check.

## Notes
A looping timer does not stop on its own; it keeps firing until something clears it. If the periodic work can finish — a stamina meter reaching full, a charge completing — the periodic action must detect the finished state and clear the timer in that same tick. Otherwise the timer keeps firing with nothing to do, wasting cycles and risking re-triggering work that is already complete. Clearing the timer on completion makes the loop self-terminating.
