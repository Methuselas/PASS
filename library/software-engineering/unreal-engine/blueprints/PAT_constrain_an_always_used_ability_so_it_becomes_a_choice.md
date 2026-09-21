---
object_id: PAT_constrain_an_always_used_ability_so_it_becomes_a_choice
object_type: pattern
name: Constrain an Always-Used Ability So It Becomes a Choice
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
- game_design
- constraints
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Constrain an Always-Used Ability So It Becomes a Choice

## Pattern Rule
**IF** you are adding a player ability that is so strong the player would use it all the time — sprinting, a powerful weapon, an always-on boost
**THEN** add a constraint that limits the ability (a resource it costs, a recharge it needs, or a waiting period between uses) so it becomes a choice the player makes, not a default the player always has.

## Do
- Give the ability a cost or a limit: a stamina meter it drains, an ammo count it spends, or a cooldown before it can be used again.
- Make the constraint visible to the player (a meter, a count) so they can plan around it.
- Tune the cost and the recovery so the ability is used sometimes, not always and not never.

## Don't
- Don't ship an ability with no constraint and expect the player to hold back — if it is always worth using, the player will always use it.
- Don't treat an always-used ability as adding a choice; from the player's perspective it is the same as raising the base value, so it adds no decision.
- Don't make the constraint so harsh the ability is never worth using; the goal is a meaningful choice, not a dead ability.

## Checklist
- The ability has a cost, limit, or cooldown that the player can feel.
- The constraint is visible (a meter or count) so the player can plan.
- Using the ability all the time is not the optimal strategy; holding back is sometimes better.

## Notes
An ability with no constraint is not a choice — it is a default. If the player is compelled to always use it, the result is the same as if you had just raised the base value, and you have added no interesting decision. A constraint (a resource it drains, a recharge it needs, a waiting period) is what turns the ability into a decision the player makes each time: use it now, or save it for later.
