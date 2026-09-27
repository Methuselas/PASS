---
object_id: PAT_verify_agent_success_from_resulting_state
object_type: pattern
name: Verify Agent Success from Resulting State
library_path:
- software-engineering
- ai-systems
- evaluation
stage_binding: 3 rough
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: PAT_test_behaviors_not_functions
tags:
- ai_agents
- evaluation
- testing
- state
- outcomes
cross_links: []
reference:
  source_title: Demystifying evals for AI agents
  author: Mikaela Grace, Jeremy Hadfield, Rodrigo Olivares, Jiri De Jonghe, with Anthropic contributors
confidence: high
references: []
variants: []
---

# Verify Agent Success from Resulting State

## Pattern Rule
**IF** an AI agent is supposed to change software, data, an external system, or another observable environment
**THEN** grade success from the resulting state or artifact whenever that state can be inspected, using the agent's transcript and final message only as supporting evidence
**ELSE** use a well-defined output grader when no independent environment state exists to verify.

## Do
- Identify the state change that would make the task genuinely complete before writing the evaluator.
- Check the database row, file, test result, ticket state, configuration, application state, or other durable outcome directly when possible.
- Keep transcript-level checks for secondary properties such as policy compliance, efficiency, communication quality, or required intermediate safeguards.
- Make the outcome check independent of the model's claim that it succeeded.
- Prefer a deterministic state check over a model judge when the same fact can be established mechanically.

## Don't
- Don't award success merely because the agent says the action was completed.
- Don't substitute a plausible confirmation message for evidence that the requested change exists.
- Don't overfit to one exact transcript when several valid execution paths can produce the same correct end state.
- Don't use a subjective judge for facts that can be checked directly from the environment.

## Checklist
- What externally observable state proves the task was completed?
- Can that state be checked deterministically after each trial?
- Does the evaluator remain correct if the agent uses a different valid sequence of actions?
- Are transcript checks limited to properties that outcome state alone cannot establish?
- Would an agent that falsely claims success still fail this evaluator?

## Notes
Agentic systems can produce convincing completion messages even when a tool failed, a transaction never committed, or the wrong object was modified. Outcome-based grading puts the authority on the environment the agent was asked to change. The transcript remains useful for diagnosing how the system behaved, but it should not replace direct evidence when direct evidence exists.
