---
object_id: PAT_test_recovery_loops_for_repeatable_reset_incentives
object_type: pattern
name: Test Recovery Loops for Repeatable Reset Incentives
library_path:
- game-design
- foundations
stage_binding: 0 design
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- recovery
- resources
- incentives
- resting
- attrition
- loops
cross_links:
- rel: related_to
  target_object_id: PAT_align_repeated_and_rewarded_behavior_with_intended_outcomes
- rel: related_to
  target_object_id: PAT_separate_stabilization_from_recovery
- rel: related_to
  target_object_id: PAT_use_time_to_structure_opportunity
reference:
  source_title: Designing TTRPGs For Dummies
  author: Martin Buinicki
confidence: high
references: []
variants: []
---

# Test Recovery Loops for Repeatable Reset Incentives

## Pattern Rule
**IF** damage, fatigue, spell use, consumables, or another attrition state can be restored through resting, treatment, recharge, resupply, or a renewable support resource
**THEN** evaluate the complete reset loop and make the most profitable repeat frequency produce behavior the game actually intends to support
**ELSE** do not balance one recovery value in isolation from the resources and cadence that restore it.

## Do
- Trace the loop from loss through treatment or recharge, resource expenditure, elapsed time, location or expertise requirements, interruption risk, and restored capability.
- Identify every renewable resource that can erase or bypass the attrition, then trace how that resource itself returns.
- Calculate or execute the cheapest safe repeat cycle players can use under representative conditions.
- Compare the value of pressing forward with the value of resetting now, including deadlines, wandering threats, exposure, opportunity loss, travel, and other costs that make delay consequential.
- Treat frequent rest, recharge, or resupply as predictable behavior when the loop makes it the dominant safe choice rather than blaming players for optimizing it.
- Test partial recovery as well as full reset when the design expects players to continue while degraded.
- Keep reset friction legible enough that players can plan around it rather than discovering hidden penalties after choosing to recover.

## Don't
- Balance a healing spell, medical skill, rest duration, recharge roll, or consumable price without tracing how its enabling resource returns.
- Assume a once-per-day or once-per-rest limit creates pressure if players can trigger that refresh cheaply and safely whenever they want.
- Add arbitrary punishment for resting when the underlying loop otherwise makes repeated resets optimal.
- Make attrition meaningful only by hiding the real recovery cost from players.

## Checklist
- The complete recovery loop is mapped from loss to restored capability.
- Renewable support resources include their own refresh or resupply path.
- The cheapest safe reset frequency has been tested under representative play conditions.
- Pressing on and resetting each have at least one state where they are rational when that tradeoff is intended.
- Repeated resting or recharging produces behavior the game is willing to support as normal play.
- Recovery timing and costs are legible before players commit to the reset decision.

## Notes
Recovery mechanics create behavior as a loop, not as isolated numbers. A costly heal can be effectively free if the resource that powers it returns after a safe rest, while a modest recovery can create strong pressure when restoring it consumes scarce time, access, supplies, or exposure. If the safest profitable strategy is fight, rest, heal, repeat, frequent resting is a system output. The repair is to redesign the loop or accept that cadence, not to treat optimization as misbehavior. Persistent fictional recovery and participation recovery remain separate concerns owned by their dedicated Patterns.
