---
object_id: DRILL_audit_a_suspicious_agent_eval_failure
object_type: drill
name: Audit a Suspicious Agent Eval Failure
library_path:
- software-engineering
- ai-systems
- evaluation
stage_binding: 3 rough
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: PAT_audit_the_evaluator_when_agent_scores_look_wrong
tags:
- ai_agents
- evaluation
- debugging
- testing
- eval_harness
cross_links:
- rel: teaches
  target_object_id: PAT_audit_the_evaluator_when_agent_scores_look_wrong
reference:
  source_title: Demystifying evals for AI agents
  author: Mikaela Grace, Jeremy Hadfield, Rodrigo Olivares, Jiri De Jonghe, with Anthropic contributors
confidence: high
target_skill: distinguishing genuine agent failure from defects in an eval task, grader, harness, or environment
references: []
variants: []
---

# Audit a Suspicious Agent Eval Failure

## Practice Task
Take one agent-eval failure whose score seems surprising and determine, from evidence, whether the failure belongs to the agent or to the measurement system.

## Target Skill
Auditing an agent evaluation before trusting a surprising score.

## Setup
Use one failed trial with its task text, complete transcript, grader outputs, harness configuration, environment state, and a way to run a known-valid reference solution.

## Instructions
1. Write the grader's claimed reason for failure without interpreting it.
2. Read the task as the agent saw it and list every requirement the grader checks. Mark any requirement that was not stated or logically implied.
3. Run a known-valid reference solution through the same harness and graders. If it fails, stop treating the original score as model evidence and locate the evaluator defect.
4. Inspect the failed transcript from the first divergence onward. Classify the failure as agent action, tool/environment failure, ambiguous task, grader mismatch, harness restriction, or unresolved.
5. Check numeric tolerances, stochastic assumptions, stale/shared state, hidden path requirements, and any opportunity to obtain credit without genuinely solving the task.
6. Repair one evaluator defect if present and rerun both the reference solution and original trial scenario.
7. Record the final verdict and the evidence that would falsify it.

## Success Check
- Every grader requirement is mapped to something the task actually tells the agent or to an explicitly justified invariant.
- A known-valid reference solution passes after any necessary evaluator repair.
- The failure classification cites the first observable divergence rather than the agent's retrospective explanation.
- Shared state, environment flakiness, hidden requirements, overly exact grading, and grader loopholes were each checked rather than assumed absent.
- The final verdict is one of `agent failure`, `evaluator failure`, or `insufficient evidence`, with concrete evidence for the choice.

## Common Failures
- Starting from the assumption that the benchmark is correct and searching only for model mistakes.
- Treating a plausible final answer as proof the environment was actually changed.
- Changing the grader until the preferred model passes without preserving the task's real success criteria.
- Declaring an evaluator bug without demonstrating that a known-valid solution should pass.

## Notes
The drill builds the habit of treating an eval as instrumentation. A surprising number is a reason to inspect both the system being measured and the instrument producing the number. The goal is not to excuse agent failures; it is to make sure the score is evidence of the failure it claims to measure.
