---
object_id: PAT_center_renewable_resources_on_a_safe_equilibrium
object_type: pattern
name: Center Renewable Resources on a Safe Equilibrium
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
- mechanics
- resources
- equilibrium
- overcharge
- risk
cross_links:
- rel: related_to
  target_object_id: PAT_budget_renewable_reserves_against_future_demands
- rel: related_to
  target_object_id: PAT_scale_voluntary_output_with_escalating_current_risk
- rel: related_to
  target_object_id: PAT_externalize_live_rules_state_at_the_point_of_use
- rel: related_to
  target_object_id: PAT_escalate_pressure_before_a_finite_resource_reaches_zero
reference:
  source_title: Tome of Mysteries - A Guide to Wizards & Magic; Tome of Blessings - A Guide to Priests & Religion
  author: Fantasy Flight Games
confidence: high
references: []
variants: []
---

# Center Renewable Resources on a Safe Equilibrium

## Pattern Rule
**IF** a renewable resource should naturally recover from ordinary depletion while becoming unstable or costly to stockpile above its normal operating level
**THEN** define an equilibrium that attracts the resource from both directions, a bounded overcharge region with explicit maintenance cost, and a higher safety threshold whose breach risks forced loss or backlash
**ELSE** use an ordinary cap-and-refresh pool when above-baseline storage is meant to remain stable and safe.

## Do
- Separate the **equilibrium** from the maximum amount a character can momentarily hold; the first is the natural resting level, not simply the top of the meter.
- Let values below equilibrium recover toward it and values above equilibrium decay toward it unless the user spends the action, attention, stress, or other cost required to maintain the excess.
- Define a safe overcharge band where holding extra resource is possible but imposes a recurring opportunity cost.
- Define a higher threshold where maintaining further excess becomes materially more dangerous, expensive, or unstable.
- When excess vents or purges, return the pool to a known stable state and convert the discarded excess into explicit consequences such as fatigue, stress, wounds, heat, instability, exposure, or another cost the subsystem can support.
- Give players a real reason to overcharge, such as preparing a high-cost effect or banking flexibility before choosing how to spend the resource, so risk exists in tension with useful output.
- Make equilibrium, safe excess, and dangerous excess legible enough that players can choose whether to spend, hold, or push further.
- Test characters or systems with different equilibrium ratings so increasing the underlying capability does not accidentally multiply both safe storage and output beyond the intended leverage.

## Don't
- Call a normal maximum an equilibrium when the pool only moves upward toward it and never has pressure to return from above.
- Add an overcharge zone that no rational player enters because its maintenance or backlash cost always exceeds the value of extra reserve.
- Let excess remain indefinitely stable after paying one initial cost when the intended tension comes from continued control.
- Make venting return to an ambiguous amount; the post-backlash state should be immediately computable.
- Hide the safety threshold while expecting informed push-your-luck decisions.
- Stack equilibrium size, generation rate, effect strength, and safe overcharge on one rating without checking the resulting dependency density.

## Checklist
- The resource has a defined resting level distinct from at least one possible value above it.
- Below-resting and above-resting states both have explicit movement toward equilibrium when no contrary action is taken.
- Holding excess resource imposes a recurring cost or decision before the dangerous threshold is crossed.
- The dangerous overcharge threshold and the consequence of failing or refusing to maintain it are explicit.
- At least one representative situation makes overcharging rational despite the added risk or cost.
- After a purge or vent, the resulting resource total and any converted consequences can be resolved without interpretation gaps.
- Increasing the rating that sets equilibrium has been checked for compounded effects on reserve size, generation, storage, and output.

## Notes
A homeostatic resource creates three distinct operating states: **below baseline**, where recovery is naturally favored; **controlled excess**, where the player pays to hold more flexibility than the system wants to retain; and **dangerous excess**, where the stockpile can collapse back toward safety and convert surplus into harm. This creates a resource that can be both renewable and pushable without behaving like either a simple mana bar or a purely finite depletion track. It is especially useful when users should be able to prepare more power than they normally carry, but doing so should itself become an active decision rather than free banking.
