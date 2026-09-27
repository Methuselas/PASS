---
object_id: PAT_grade_agent_outcomes_without_overconstraining_valid_paths
object_type: pattern
name: Grade Agent Outcomes Without Overconstraining Valid Paths
library_path:
- software-engineering
- ai-systems
- evaluation
stage_binding: 3 rough
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: PAT_test_against_a_validity_property_when_the_answer_is_not_unique
tags:
- ai_agents
- evaluation
- testing
- trajectories
- grading
cross_links: []
reference:
  source_title: Demystifying evals for AI agents
  author: Mikaela Grace, Jeremy Hadfield, Rodrigo Olivares, Jiri De Jonghe, with Anthropic contributors
confidence: high
references: []
variants: []
---

# Grade Agent Outcomes Without Overconstraining Valid Paths

## Pattern Rule
**IF** an agent can legitimately solve a task through more than one sequence of actions
**THEN** grade the required outcome and invariant constraints rather than one expected tool-call trajectory, adding path constraints only when the path itself is part of the requirement
**ELSE** enforce an exact sequence when policy, safety, protocol, or external ordering semantics genuinely make that sequence mandatory.

## Do
- Define the state, artifact, or validity properties that any acceptable solution must satisfy.
- Let different tool orders and intermediate strategies pass when they produce the same valid result.
- Enforce specific intermediate actions only when they carry independent requirements such as authorization, audit, safety, or transaction ordering.
- Award partial credit for independent task components when the score is meant to diagnose progress rather than act as a binary release gate.
- Review rejected trajectories periodically to discover valid strategies the original grader did not anticipate.

## Don't
- Don't fail a correct result merely because the agent used a different valid tool sequence.
- Don't encode implementation taste as a hidden grading requirement.
- Don't loosen constraints that exist for safety, authorization, or correctness just to accommodate model creativity.
- Don't collapse a multi-part diagnostic eval into all-or-nothing scoring when partial progress is meaningful to engineering decisions.

## Checklist
- Which properties must every correct outcome satisfy?
- Which, if any, intermediate steps are genuinely mandatory?
- Could another valid strategy reach the same state without violating a requirement?
- Does the grader distinguish mandatory constraints from one reference trajectory?
- Would partial credit reveal useful information about where a complex task failed?

## Notes
Agents can discover paths that eval authors did not predict. A grader that confuses the reference solution with the only valid solution will increasingly measure conformity to the harness rather than capability. Outcome and invariant grading preserves flexibility while retaining exact path requirements where those requirements are real.
