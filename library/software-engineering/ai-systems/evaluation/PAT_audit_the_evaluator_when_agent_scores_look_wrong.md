---
object_id: PAT_audit_the_evaluator_when_agent_scores_look_wrong
object_type: pattern
name: Audit the Evaluator When Agent Scores Look Wrong
library_path:
- software-engineering
- ai-systems
- evaluation
stage_binding: 3 rough
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: PAT_tests_fail_only_when_code_broken
tags:
- ai_agents
- evaluation
- testing
- debugging
- eval_harness
cross_links: []
reference:
  source_title: Demystifying evals for AI agents
  author: Mikaela Grace, Jeremy Hadfield, Rodrigo Olivares, Jiri De Jonghe, with Anthropic contributors
confidence: high
references: []
variants: []
---

# Audit the Evaluator When Agent Scores Look Wrong

## Pattern Rule
**IF** an agent eval produces unexpectedly low, immovable, or contradictory scores
**THEN** inspect the task specification, reference solution, grader logic, harness constraints, environment, and representative transcripts before attributing the result to model capability
**ELSE** trust the score only after the measurement system itself has evidence of correctness.

## Do
- Confirm that the task is solvable by running or constructing a known-valid reference solution through the same graders.
- Compare every hidden grader requirement with what the task actually tells the agent.
- Read successful and failed transcripts to see whether failures look fair and diagnostic.
- Look for brittle tolerances, impossible stochastic requirements, stale fixtures, harness restrictions, and environment failures.
- Check that passing requires genuinely solving the task rather than exploiting a grader shortcut.
- Fix evaluator defects before using the score to compare models, prompts, or architectures.

## Don't
- Don't interpret a zero or unexpectedly low pass rate as proof of incapability before validating the task and grader.
- Don't hide requirements in grader code that are absent from the task specification.
- Don't preserve a benchmark defect merely to keep historical scores comparable.
- Don't let the agent receive credit through a loophole that bypasses the intended work.

## Checklist
- Does a known-valid reference solution pass every grader?
- Is every required property stated or logically implied by the task?
- Do failed transcripts show genuine agent mistakes rather than evaluator mistakes?
- Are tolerances, randomness, and environment assumptions reproducible?
- Can the agent game the grader without completing the intended task?

## Notes
An eval score is produced by a measurement system, and that system can be wrong. Agentic benchmarks are especially exposed because the harness controls tools, state, hidden checks, and often stochastic processes. Suspicious results should trigger a measurement audit before they trigger conclusions about the model.
