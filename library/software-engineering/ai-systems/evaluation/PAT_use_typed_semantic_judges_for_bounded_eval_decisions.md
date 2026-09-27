---
object_id: PAT_use_typed_semantic_judges_for_bounded_eval_decisions
object_type: pattern
name: Use Typed Semantic Judges for Bounded Eval Decisions
library_path:
- software-engineering
- ai-systems
- evaluation
stage_binding: 3 rough
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: PAT_match_agent_eval_graders_to_the_evidence_type
tags:
- ai_agents
- evaluation
- semantic_judge
- structured_output
- classification
cross_links:
- rel: related_to
  target_object_id: PAT_match_agent_eval_graders_to_the_evidence_type
- rel: related_to
  target_object_id: PAT_route_bounded_ai_decisions_through_classification
reference:
  source_title: Jev is now available in LangSmith Evals
  author: Winston Huynh
confidence: high
references: []
variants: []
---

# Use Typed Semantic Judges for Bounded Eval Decisions

## Pattern Rule
**IF** an evaluator must interpret open-ended semantic evidence such as an agent trace or message, but each grading criterion can be expressed as a bounded yes/no decision, categorical choice, ordered score, or probability
**THEN** use a typed semantic judge that returns the bounded decision directly instead of generating free-form reasoning and parsing it back into structure
**ELSE** use a deterministic check when the criterion has a mechanical oracle, or a generative judge when the evaluation genuinely needs open-ended written reasoning.

## Do
- Separate the **state being evaluated** from the **questions that define the grading criteria**. The trace, message, or run data is evidence; the grading instructions belong in the evaluator questions.
- Give each criterion an explicit answer shape such as binary probability, finite choice set, or ordered score scale.
- Return typed answers directly to the evaluation system so downstream filtering, aggregation, alerting, and comparison do not depend on parsing generated prose.
- Keep criteria independently named even when the evaluator can answer several of them in one request, so each result remains an interpretable feedback signal.
- Preserve confidence or probability information when the judge provides it and define how low-confidence cases are escalated or reviewed.
- Calibrate the typed judge against representative human judgments before treating its structured output as ground truth.
- Fall back to a generative judge when the evaluator must explain nuanced reasoning, synthesize an open-ended critique, or produce evidence that cannot be represented faithfully in the bounded schema.

## Don't
- Don't use a free-form generation call merely to recover a yes/no, label, or bounded score that could have been returned directly.
- Don't assume typed output is automatically correct because it is schema-valid; semantic judgment can still be wrong.
- Don't replace a deterministic state or property check with a learned judge when the environment can establish the fact directly.
- Don't hide grading instructions inside the evaluated state; mixing evidence and rubric makes the evaluation interface harder to reason about and reuse.
- Don't force an open-ended quality judgment into an underspecified score scale just to avoid a generative evaluator.

## Checklist
- Does the evaluator need semantic interpretation rather than a purely mechanical check?
- Can every required verdict be represented as a bounded answer type?
- Are the evaluated state and the grading questions represented separately?
- Can downstream systems consume the judge output without reparsing prose?
- Has judge-human agreement been checked on representative examples?
- Is there a defined fallback for low confidence or criteria that require written reasoning?

## Notes
This pattern fills the space between deterministic code graders and generative LLM-as-a-judge evaluation. The evidence can remain open-ended while the decision interface stays narrow and typed. That keeps the semantic flexibility needed to inspect varied agent behavior without adding a second failure point where generated prose must be converted back into a machine decision.

Jev's typed `noul`, `choice`, and `score` questions provide a concrete example. The transferable engineering idea is the interface shape, not dependence on a particular evaluator product.
