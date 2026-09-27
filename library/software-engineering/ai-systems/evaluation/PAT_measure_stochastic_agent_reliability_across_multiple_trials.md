---
object_id: PAT_measure_stochastic_agent_reliability_across_multiple_trials
object_type: pattern
name: Measure Stochastic Agent Reliability Across Multiple Trials
library_path:
- software-engineering
- ai-systems
- evaluation
stage_binding: 3 rough
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: PAT_decide_with_a_random_test_whose_error_shrinks_with_each_trial
tags:
- ai_agents
- evaluation
- stochastic_systems
- reliability
- testing
cross_links: []
reference:
  source_title: Demystifying evals for AI agents
  author: Mikaela Grace, Jeremy Hadfield, Rodrigo Olivares, Jiri De Jonghe, with Anthropic contributors
confidence: high
references: []
variants: []
---

# Measure Stochastic Agent Reliability Across Multiple Trials

## Pattern Rule
**IF** an AI agent can produce different outcomes from the same task across runs
**THEN** evaluate each important task over multiple independent trials and report a reliability metric that matches the product's retry semantics rather than treating one run as the task's truth
**ELSE** a single deterministic execution can be sufficient when repeated runs cannot change the result.

## Do
- Run enough independent trials to distinguish a flaky capability from a reliably repeatable one.
- Track per-task success rates instead of only a suite-wide average so localized instability remains visible.
- Use a first-try or consistency-oriented metric when users expect the same task to work every time.
- Use a multiple-attempt success metric only when the product genuinely permits retries and any successful attempt satisfies the requirement.
- Keep the interpretation of the metric attached to the product behavior: occasional success and dependable success are different qualities.

## Don't
- Don't declare a stochastic behavior fixed because one rerun happened to pass.
- Don't compare systems from a single trial per task when run-to-run variance is material.
- Don't use a retry-friendly metric for a customer-facing flow that gets only one real attempt.
- Don't hide a small set of highly unstable tasks inside a strong aggregate average.

## Checklist
- Can identical task inputs produce different outcomes across runs?
- How many attempts does the real product allow?
- Is the reported metric measuring at-least-one success, first-try success, or consistency across attempts?
- Are trials independent of one another?
- Can you see per-task variance rather than only the aggregate score?

## Notes
For nondeterministic agents, a task is better thought of as having a success distribution than a permanent pass/fail label. Metrics such as pass@k answer whether at least one of several attempts succeeds, while consistency-oriented measures such as pass^k answer whether repeated attempts all succeed. The useful metric is the one whose retry assumptions match the deployed product.
