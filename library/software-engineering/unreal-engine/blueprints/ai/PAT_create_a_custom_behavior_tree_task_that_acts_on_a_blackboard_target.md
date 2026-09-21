---
object_id: PAT_create_a_custom_behavior_tree_task_that_acts_on_a_blackboard_target
object_type: pattern
name: Create a Custom Behavior Tree Task That Acts on a Blackboard Target
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
- task
- damage
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: low
references: []
variants: []
---

# Create a Custom Behavior Tree Task That Acts on a Blackboard Target

## Pattern Rule
**IF** you want a Behavior Tree AI to perform an action on the target it is tracking — such as a melee attack that damages the player — and the built-in tasks do not cover it
**THEN** create a custom task (a Blueprint based on BTTask_BlueprintBase) that reads the target from a Blackboard key at execution time, validates the reference, performs the action, and calls Finish Execute; drive the specifics (which key, how much effect) from Instance Editable task parameters so each placed node can be configured in the tree.

## Do
- Give the task a BlackboardKeySelector variable (Instance Editable) for the target key and a value variable (such as a Float damage amount, Instance Editable) for the effect's magnitude.
- In Receive Execute, read the target from the Blackboard (Get Blackboard Value as Actor with the key), check Is Valid, and only then perform the action (Apply Damage with the task's damage value).
- Call Finish Execute with Success checked so the sequence can continue.
- Place the task in the attack sequence after the Move To task so the attack fires only after the AI has reached the target.
- Set the key and a descriptive Node Name on the placed node (such as PlayerCharacter / "Damage Player") so the tree reads as a description of the behavior.

## Don't
- Don't act on the Blackboard reference without an Is Valid check — the key may be unset or stale when the task runs.
- Don't hard-code the target key or the effect magnitude in the task when Instance Editable parameters let each placed node choose them.
- Don't put the attack before the Move To in the sequence — a melee attack only works at range, so the move must succeed first.
- Don't forget the Finish Execute call — without it the sequence stalls.

## Checklist
- The task is a Blueprint based on BTTask_BlueprintBase with a BlackboardKeySelector target variable and an effect-magnitude variable, both Instance Editable.
- Receive Execute reads the target from the Blackboard, validates it, applies the effect, and finishes with success.
- The task sits in the attack sequence after the move, so the effect lands only on arrival.
- The placed node's key and Node Name describe how the task is used in this tree.

## Notes
The task is the "act" half of the AI loop: the tree decides when to attack (the decorator gates on sight), and the task performs the attack on whatever the Blackboard currently holds as the target. Reading the target from the Blackboard at execution time — rather than capturing it when the task was created — keeps the task correct even if the target changes between decisions. Parameterizing the key and the effect magnitude makes one task reusable for any target key and any damage value, and the placement after the Move To is what makes the attack a melee: the sequence guarantees the AI has arrived before it strikes.
