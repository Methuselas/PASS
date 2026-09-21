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
foundation_object_id: PAT_give_knowledge_one_authoritative_home
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
**IF** several timer-by-function-name nodes must refer to the same custom event name
**THEN** store that function name in one String variable and feed the variable to every call site, reducing repeated spelling and the risk of inconsistent names.

## Do
- Create a String variable (for example, StaminaManagerName) and set its default value to the custom event's name.
- Wire the variable's GET node into the Function Name pin of every Set / Does-Exist / Clear Timer by Function Name node.
- Keep the variable's default value in sync with the custom event's name.

## Don't
- Don't retype the same function name independently at each timer call site when they are all intended to address one event.
- Don't keep competing authoritative copies of the timer name.

## Checklist
- The timer's function name lives in one String variable.
- Every Set / Does-Exist / Clear Timer by Function Name node reads the name from that variable.
- A rename is centralized to the stored name instead of repeated literals.

## Notes
Timer-by-function-name nodes identify the event through text. Centralizing that text in one variable follows `PAT_give_knowledge_one_authoritative_home`: it reduces duplicate spelling and therefore reduces the chance that one timer node silently refers to a different name.
