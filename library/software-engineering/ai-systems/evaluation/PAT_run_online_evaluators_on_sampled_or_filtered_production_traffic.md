---
object_id: PAT_run_online_evaluators_on_sampled_or_filtered_production_traffic
object_type: pattern
name: Run Online Evaluators on Sampled or Filtered Production Traffic
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
- online_evals
- production
- monitoring
- sampling
cross_links:
- rel: supports
  target_object_id: PAT_combine_offline_evals_with_production_feedback
- rel: related_to
  target_object_id: PAT_choose_evaluator_economics_to_match_required_coverage
- rel: related_to
  target_object_id: PAT_calibrate_llm_judges_against_human_graders
- rel: related_to
  target_object_id: PAT_apply_data_governance_to_external_evaluation_providers
reference:
  source_title: You don’t know what your agent will do until it’s in production
  author: Harrison Chase and Sam Crowder
confidence: high
references: []
variants: []
---

# Run Online Evaluators on Sampled or Filtered Production Traffic

## Pattern Rule
**IF** an agent's production quality cannot be inferred from infrastructure metrics alone and manual review cannot cover live traffic
**THEN** run calibrated online evaluators automatically on all traffic, a sampled fraction, or a deliberately filtered subset, and use their results as continuous quality signals with explicit alert thresholds
**ELSE** keep evaluation offline when live scoring would add no operational signal or cannot meet the required privacy, cost, latency, or reliability constraints.

## Do
- Choose coverage deliberately: full traffic when feasible, representative sampling for routine monitoring, or filtered subsets for a known cohort or risk area.
- Evaluate criteria that matter to the deployed agent, such as answer quality, safety/compliance, output format, topic classification, or trajectory quality.
- Keep expensive or latency-sensitive grading asynchronous when synchronous scoring would harm the user-facing path.
- Define alert thresholds for meaningful degradation rather than merely recording scores without an operational response.
- Calibrate subjective model judges against human labels before trusting them as production quality sensors.
- Revisit sampling, rubrics, and thresholds as traffic patterns and failure modes change.

## Don't
- Don't assume every production trace must receive every evaluator regardless of cost or latency.
- Don't put slow evaluators directly on the response path when the result is only needed for asynchronous monitoring.
- Don't trust an off-the-shelf semantic judge to represent application-specific quality without calibration.
- Don't treat sampled online scores as complete coverage of rare failure modes.
- Don't let evaluator drift go unchecked as production traffic shifts.

## Checklist
- Which production traces are evaluated and why?
- Is the selected coverage affordable and fast enough for the intended monitoring loop?
- Which criteria require semantic judgment versus deterministic validation?
- Are subjective judges calibrated to representative human labels?
- What threshold or trend triggers investigation or alerting?
- Is online evaluation synchronous only where the user-facing decision genuinely requires it?

## Notes
Online evaluation can scale quality monitoring beyond what humans can review manually. Coverage can be all traffic, sampled traffic, or filtered subsets, and the resulting scores can support quality trends, topic tagging, trajectory checks, safety monitoring, and alerts. This card owns the operational deployment of evaluators on live traffic; evaluator economics and judge calibration remain separate concerns.
