---
object_id: PAT_match_agent_eval_graders_to_the_evidence_type
object_type: pattern
name: Match Agent Eval Graders to the Evidence Type
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
- graders
- testing
- llm_judge
cross_links: []
reference:
  source_title: Demystifying evals for AI agents
  author: Mikaela Grace, Jeremy Hadfield, Rodrigo Olivares, Jiri De Jonghe, with Anthropic contributors
confidence: high
references: []
variants: []
---

# Match Agent Eval Graders to the Evidence Type

## Pattern Rule
**IF** an agent task contains a mix of objective outcomes and subjective quality dimensions
**THEN** use the least subjective grader that can establish each claim: deterministic checks for mechanically verifiable facts, model judges for open-ended judgment, and human review for calibration or expert-only standards
**ELSE** keep the evaluator simple when one objective grader can establish the whole requirement.

## Do
- Decompose success into claims such as state changed, constraint obeyed, answer grounded, tone acceptable, or task completed within a resource bound.
- Assign deterministic tests, state checks, static analysis, or exact predicates wherever the claim has an objective oracle.
- Use model-based graders only for dimensions that genuinely require semantic or qualitative judgment.
- Use human experts to establish or periodically recalibrate the reference standard for subjective dimensions.
- Combine graders when the task spans several evidence types rather than asking one judge to infer everything from the transcript.

## Don't
- Don't use an LLM judge merely because the system under test contains an LLM.
- Don't force a brittle exact matcher onto a task with several semantically valid answers.
- Don't ask a single subjective judge to score objective facts that the harness could inspect directly.
- Don't treat a model judge as self-validating; its agreement with the intended human standard must be checked.

## Checklist
- Which success criteria have deterministic or state-based oracles?
- Which criteria are genuinely semantic or subjective?
- Is every model-judged dimension one that cannot be established more directly?
- Is there a human-calibrated reference for subjective grading?
- Does the combined score preserve the meaning of distinct success dimensions?

## Notes
Agent evaluation is often multidimensional. Correctness, groundedness, efficiency, safety constraints, and interaction quality do not all have the same kind of evidence. Treating grader choice as an evidence-matching problem avoids both extremes: brittle deterministic grading of open-ended work and expensive, noisy model judging of facts the environment already knows.
