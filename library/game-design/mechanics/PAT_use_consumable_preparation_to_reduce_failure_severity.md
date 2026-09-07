---
object_id: PAT_use_consumable_preparation_to_reduce_failure_severity
object_type: pattern
name: Use Consumable Preparation to Reduce Failure Severity
library_path:
- game-design
- mechanics
stage_binding: 0 design
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- preparation
- consumables
- risk
- failure
- insurance
cross_links:
- rel: related_to
  target_object_id: PAT_match_the_cost_of_failure_to_the_players_prior_investment
- rel: related_to
  target_object_id: PAT_give_high_consequence_risks_a_learnable_information_basis
reference:
  source_title: Warhammer Fantasy Roleplay, Fourth Edition
  author: Dominic McDowall, Andy Law, and contributors
confidence: high
references: []
variants: []
---

# Use Consumable Preparation to Reduce Failure Severity

## Pattern Rule
**IF** an action should remain uncertain but players can prepare specifically against its harmful side effects
**THEN** let a consumed preparation downgrade or cancel defined failure consequences without improving the underlying chance of success
**ELSE** modify success probability directly when preparation is supposed to make the task itself easier rather than safer.

## Do
- Separate reliability from safety: the action can still fail even though the prepared character suffers a less severe backlash.
- Define the consequence tiers the preparation changes, such as catastrophic to serious, serious to minor, or minor to none.
- Consume the preparation once committed even when no harmful result occurs if the intended decision is insurance rather than a pay-only-on-failure rescue.
- Make the preparation specific enough that choosing what to protect against remains meaningful rather than becoming a universal cancel token.
- Scale cost, rarity, preparation burden, or access with the danger being insured when severe risks should require greater investment.
- Let players knowingly choose to act without the preparation when urgency, scarcity, or confidence makes accepting the full consequence rational.

## Don't
- Improve both success chance and consequence severity automatically when the design goal is specifically to sell safety without reliability.
- Refund the consumable whenever the bad result fails to occur if committing it is meant to represent buying protection in advance.
- Let one cheap generic consumable erase every serious consequence in the subsystem.
- Require the preparation for routine use so universally that it stops being a choice and becomes hidden mandatory upkeep.
- Apply the downgrade after the player already knows the adverse result unless the subsystem is explicitly about reactive protection rather than preparation.

## Checklist
- Using the preparation leaves the action's ordinary success probability unchanged.
- At least one named adverse tier is reduced or cancelled by an explicit rule.
- The player commits the consumable before knowing whether the insured consequence occurs.
- Acting without the consumable remains legal and rational in at least one representative circumstance.
- Cost or specificity prevents the protection from becoming an automatic universal default.

## Notes
Preparation does not always need to make an action more likely to work. It can instead preserve the uncertainty while changing what failure costs. This creates an insurance decision: spend a scarce, specific resource now to reduce possible backlash, or keep the resource and accept the full risk. Tiered consequence systems make the move especially clean because the preparation can downgrade severity without rewriting the resolver itself.
