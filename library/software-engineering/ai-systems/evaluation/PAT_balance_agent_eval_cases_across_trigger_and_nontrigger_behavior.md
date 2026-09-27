---
object_id: PAT_balance_agent_eval_cases_across_trigger_and_nontrigger_behavior
object_type: pattern
name: Balance Agent Eval Cases Across Trigger and Nontrigger Behavior
library_path:
- software-engineering
- ai-systems
- evaluation
stage_binding: 3 rough
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: AP_choose_test_cases_systematically
tags:
- ai_agents
- evaluation
- testing
- routing
- class_balance
cross_links: []
reference:
  source_title: Demystifying evals for AI agents
  author: Mikaela Grace, Jeremy Hadfield, Rodrigo Olivares, Jiri De Jonghe, with Anthropic contributors
confidence: high
references: []
variants: []
---

# Balance Agent Eval Cases Across Trigger and Nontrigger Behavior

## Pattern Rule
**IF** an agent must decide whether to invoke a behavior, tool, route, escalation, or other conditional action
**THEN** include representative cases where the behavior should occur and where it should not, so optimization cannot improve recall by simply firing the behavior more often
**ELSE** one-sided coverage may be acceptable only when there is no meaningful false-positive or false-negative decision boundary.

## Do
- Represent both sides of every important trigger boundary in the eval set.
- Track under-triggering and over-triggering separately when both failure modes matter.
- Source negative cases from realistic requests that are easy to confuse with positive ones rather than from obviously unrelated inputs.
- Rebalance the suite when production data reveals that one side of the decision is underrepresented.
- Preserve hard boundary cases after prompt or routing changes so improvements on one side cannot erase the other.

## Don't
- Don't test only that the agent uses a capability when requested and ignore whether it uses that capability unnecessarily.
- Don't treat a higher trigger rate as an improvement unless the false-positive rate remains acceptable.
- Don't populate the negative set with trivial examples that no plausible system would misclassify.
- Don't let a class-imbalanced suite turn one failure mode into invisible noise.

## Checklist
- What is the false-positive failure for this behavior?
- What is the false-negative failure?
- Does the suite contain realistic examples of both?
- Are near-boundary cases represented on both sides?
- Are the two error directions reported separately enough to see the tradeoff?

## Notes
Conditional agent behavior is easy to optimize in one direction. A search agent tested only on requests that need search can learn to search almost everything and still look better. Balanced trigger/nontrigger coverage turns the decision boundary itself into the thing being tested.
