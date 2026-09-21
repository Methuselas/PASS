---
object_id: PAT_build_an_ai_enemy_from_character_controller_behavior_tree_and_blackboard
object_type: pattern
name: Build an AI Enemy from Character, Controller, Behavior Tree, and Blackboard
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
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: low
references: []
variants: []
---

# Build an AI Enemy from Character, Controller, Behavior Tree, and Blackboard

## Pattern Rule
**IF** you want an actor to have AI behavior in Unreal Engine — to sense the world and make decisions about what to do
**THEN** compose it from four assets that work together: a Character Blueprint (the enemy in the level), an AIController Blueprint (the connection that routes the tree's decisions and actions to the character), a Behavior Tree asset (the decision-making logic), and a Blackboard asset (the shared data container between the controller and the tree) — and wire them so the Character's AI Controller Class points at the controller, the controller runs the Behavior Tree, and the Behavior Tree uses the Blackboard.

## Do
- Create the four assets in one place (a dedicated folder) so the enemy's AI is self-contained.
- Point the Character's AI Controller Class (in the PAWN category of Class Defaults) at your AIController Blueprint.
- Run the Behavior Tree from the AIController (Run Behavior Tree in BeginPlay), passing the Behavior Tree asset.
- Set the Behavior Tree's Blackboard Asset to your Blackboard so the tree and the controller share the same data.
- Keep the Blackboard as the single shared store: the controller writes sensed data into it, and the tree reads it to decide.

## Don't
- Don't put the decision logic in the Character or the controller's event graph when it belongs in the Behavior Tree — the tree is where conditions map to actions.
- Don't scatter the shared AI state across variables in different Blueprints; the Blackboard is the container the controller and tree both read and write.
- Don't skip the wiring: an unwired controller or tree means the enemy has no brain even though all four assets exist.

## Checklist
- The Character's AI Controller Class is set to your AIController Blueprint.
- The AIController runs the Behavior Tree on BeginPlay.
- The Behavior Tree's Blackboard Asset is set to your Blackboard.
- Data flows one way: sensing writes to the Blackboard, the tree reads it and acts.

## Notes
The four assets are the standard Unreal Engine AI stack. The Character is the body, the AIController is the connection, the Behavior Tree is the decision logic, and the Blackboard is the shared memory. Getting the wiring right is what turns four separate assets into one enemy that can sense and decide. This is the skeleton the rest of the AI work (navigation, sensing, chasing) hangs on.
