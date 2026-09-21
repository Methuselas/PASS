---
object_id: PAT_store_a_timer_name_in_a_variable
object_type: pattern
name: Store a Timer Name in a Variable
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

# Store a Timer Name in a Variable

## Pattern Rule
**IF** you start, check, or clear a timer by function name — Set Timer by Function Name, Does Timer Exist by Function Name, Clear Timer by Function Name
**THEN** store the timer's function name in a String variable and reference that variable at every call site, so the name is written once and a spelling error cannot silently break the timer.

## Do
- Create a String variable (for example, StaminaManagerName) and set its default value to the custom event's name.
- Wire the variable's GET node into the Function Name pin of every Set / Does-Exist / Clear Timer by Function Name node.
- Keep the variable's default value in sync with the custom event's name.

## Don't
- Don't type the function name as a literal at each timer call site — a single misspelling makes the timer silently fail to start, to report existing, or to clear.
- Don't keep the name in more than one place; the variable is the single source of the name.

## Checklist
- The timer's function name lives in one String variable.
- Every Set / Does-Exist / Clear Timer by Function Name node reads the name from that variable.
- Renaming the event means changing one variable, not several literals.

## Notes
Timers addressed by function name take the name as a string. Typing that string at every call site invites a spelling error the compiler will not catch: the timer simply never starts, never reports existing, or never clears. Storing the name in a String variable and referencing it everywhere makes the name a single value, so a rename is one edit and a typo is impossible.
