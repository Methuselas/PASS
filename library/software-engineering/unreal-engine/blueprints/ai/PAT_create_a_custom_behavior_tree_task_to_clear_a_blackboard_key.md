---
object_id: PAT_create_a_custom_behavior_tree_task_to_clear_a_blackboard_key
object_type: pattern
name: Create a Custom Behavior Tree Task to Clear a Blackboard Key
library_path:
- software-engineering
- unreal-engine
- blueprints
- ai
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- ai
- behavior_tree
- blackboard
- task
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: low
references: []
variants: []
---

# Create a Custom Behavior Tree Task to Clear a Blackboard Key

## Pattern Rule
**IF** the built-in Behavior Tree tasks do not do what you need — for example, you need a step that clears a Blackboard key
**THEN** create a custom task: a Blueprint based on BTTask_BlueprintBase that overrides Receive Execute to perform the action and calls Finish Execute to mark the task complete.

## Do
- Create the task from the Behavior Tree editor (New Task) or as a Blueprint based on BTTask_BlueprintBase.
- Give the task a clear Node Name so it reads well in the tree.
- Override Receive Execute — the event that fires when the task is activated in the tree — and put the action there.
- Drive the action from a task parameter (for example, a Blackboard KeySelector variable, Instance Editable, so each placed task can name the key it clears).
- Call Finish Execute at the end of the action, setting its Success parameter, so the tree knows the task is done.

## Don't
- Don't leave the task without a Finish Execute call — the tree will not know the task completed and the sequence will stall.
- Don't hard-code the key the task clears when a parameter can make the same task reusable for any key.
- Don't put the decision about when to run the task inside the task; the task performs one action, and the tree (with its decorators and control flow) decides when it runs.

## Checklist
- The task is a Blueprint based on BTTask_BlueprintBase.
- Receive Execute is overridden and performs the action.
- The action is driven by a task parameter, not a hard-coded value.
- Finish Execute is called with the Success parameter set.

## Notes
A custom task is how you extend the Behavior Tree with an action the built-in tasks don't cover. The contract is small: override Receive Execute to do the work, take the specifics as parameters so the task is reusable, and call Finish Execute so the tree can move on. A common use is clearing a Blackboard key — for example, dropping the "player seen" reference after an attack so the enemy returns to patrol and the player gets a chance to escape — but the same shape works for any missing action.
