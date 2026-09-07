---
object_id: PAT_bound_self_reinforcing_momentum_before_it_erases_counterplay
object_type: pattern
name: Bound Self-Reinforcing Momentum Before It Erases Counterplay
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
- momentum
- positive-feedback
- combat
- counterplay
- caps
cross_links:
- rel: related_to
  target_object_id: PAT_define_temporal_priority_by_the_advantage_it_grants
- rel: related_to
  target_object_id: PAT_budget_mechanical_operating_cost_by_decision_value_and_activation_cadence
reference:
  source_title: Warhammer Fantasy Roleplay, Fourth Edition
  author: Dominic McDowall, Andy Law, and contributors
confidence: high
references: []
variants: []
---

# Bound Self-Reinforcing Momentum Before It Erases Counterplay

## Pattern Rule
**IF** succeeding now grants a stacking benefit that directly increases the chance or impact of succeeding again
**THEN** bound the positive-feedback loop with explicit caps, decay, hard reset conditions, spend outlets, or reliable counterplay before accumulated momentum can make reversal practically impossible
**ELSE** use ordinary non-compounding bonuses when repeated success is not supposed to accelerate the contest.

## Do
- Identify every event that both benefits from current momentum and can create more momentum; these are the links that make the loop self-reinforcing.
- Calculate representative stacked states rather than testing only the first bonus. A modifier that looks modest once may dominate after several consecutive gains.
- Give opponents or changing circumstances a credible way to break the stack, such as winning a contest, inflicting harm, imposing a condition, forcing a disengagement, or exploiting another state change.
- Use a hard reset when momentum is meant to represent a fragile run of control rather than a durable resource.
- Add an upper bound when the unrestricted stack can overwhelm the ordinary uncertainty range or erase meaningful counterplay.
- Let momentum have alternate uses when spending it creates a real choice between preserving future leverage and converting present advantage into positioning, escape, or another benefit.

## Don't
- Assume a bonus is balanced because each individual step is small while ignoring that the bonus improves the same checks that earn additional steps.
- Let the leading side accumulate leverage through ordinary success while the trailing side needs an exceptional result merely to return to the baseline.
- Hide the loss conditions when players are expected to choose whether to protect, spend, or risk accumulated momentum.
- Add a nominal cap so high that representative contests are already decided before the cap matters.
- Use self-reinforcing momentum when the intended contest should remain roughly reversible from round to round.

## Checklist
- At least one representative sequence has been tested after several consecutive momentum gains, not only at zero and one stack.
- The design names which successful events create more momentum and which events break or reduce it.
- A trailing participant has at least one plausible route to interrupt the feedback loop before the contest becomes foregone.
- Any cap is low enough to affect the range where accumulated bonuses would otherwise dominate ordinary uncertainty.
- If momentum can be spent, keeping it and converting it are both rational choices in at least one representative situation.

## Notes
A momentum mechanic can deliberately make success accelerate success, which is useful when a contest should develop a sense of control, initiative, or collapse. The same structure is dangerous because the reward changes the probability of earning the next reward. Hard resets make the accumulated edge fragile; decay prevents indefinite banking; caps bound the reachable advantage; spend outlets turn the stack into a resource decision. The important test is the whole feedback loop, not the size of one increment.
