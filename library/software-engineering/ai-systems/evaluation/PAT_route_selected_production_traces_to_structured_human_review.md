---
object_id: PAT_route_selected_production_traces_to_structured_human_review
object_type: pattern
name: Route Selected Production Traces to Structured Human Review
library_path:
- software-engineering
- ai-systems
- evaluation
stage_binding: 4 final
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: none
tags:
- ai_agents
- evaluation
- production
- human_review
- annotation
cross_links:
- rel: related_to
  target_object_id: PAT_calibrate_llm_judges_against_human_graders
- rel: supports
  target_object_id: PAT_combine_offline_evals_with_production_feedback
- rel: related_to
  target_object_id: PAT_choose_evaluator_economics_to_match_required_coverage
reference:
  source_title: You don’t know what your agent will do until it’s in production
  author: Harrison Chase and Sam Crowder
confidence: high
references: []
variants: []
---

# Route Selected Production Traces to Structured Human Review

## Pattern Rule
**IF** production behavior requires expert or subjective judgment that cannot be reviewed exhaustively at traffic scale
**THEN** route selected high-value traces into a structured human-review queue with an explicit rubric, assignment/progress tracking, and a path for reviewed examples to become evaluation data
**ELSE** use automated or deterministic monitoring when the criterion is objective enough to evaluate reliably without scarce reviewer time.

## Do
- Select review candidates deliberately, such as traces with negative feedback, unusually high cost, a suspected failure mode, or a relevant time window or cohort.
- Give reviewers a predefined rubric for the dimensions they are expected to assess rather than asking for unstructured impressions.
- Use qualified subject-matter reviewers when correctness depends on specialized domain knowledge.
- Preserve reviewer labels, corrections, and comments in a form that can seed or refine evaluators and offline datasets.
- Use focused queues to investigate new failure modes and boundary cases instead of attempting to manually inspect all production traffic.
- Track queue progress and reviewer ownership so scarce review capacity is spent on the intended sample.

## Don't
- Don't ask humans to browse raw production logs hoping they notice the important traces.
- Don't spend expert review time uniformly across low-value and high-value interactions.
- Don't collect labels without a rubric that makes different reviewers' judgments comparable.
- Don't let reviewed failures remain isolated anecdotes when they can be converted into durable evaluation cases.
- Don't treat a small targeted review sample as a direct estimate of whole-traffic quality unless the sampling design supports that inference.

## Checklist
- Why was each trace selected for human review?
- Is the review rubric explicit enough that two qualified reviewers can apply the same criteria?
- Are specialist reviewers used where the domain requires them?
- Can corrections and labels flow into evaluator calibration or offline datasets?
- Is reviewer time concentrated on traces where human judgment adds material value?

## Notes
Human review can supply nuanced natural-language judgment, but available reviewer capacity rarely permits exhaustive production coverage. A structured annotation queue can concentrate that capacity on selected traces, apply a consistent rubric, and feed the resulting labels back into the evaluation loop; measure coverage and agreement before generalizing from the reviewed sample.
