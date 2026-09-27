---
object_id: AP_build_and_maintain_an_agent_evaluation_suite
object_type: ap
name: Build and Maintain an Agent Evaluation Suite
library_path:
- software-engineering
- ai-systems
- evaluation
stage_binding: 3 rough
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: none
tags:
- ai_agents
- evaluation
- testing
- reliability
- observability
cross_links:
- rel: supports
  target_object_id: PAT_verify_agent_success_from_resulting_state
- rel: supports
  target_object_id: PAT_match_agent_eval_graders_to_the_evidence_type
- rel: supports
  target_object_id: PAT_keep_capability_and_regression_evals_separate
- rel: supports
  target_object_id: PAT_measure_stochastic_agent_reliability_across_multiple_trials
- rel: supports
  target_object_id: PAT_balance_agent_eval_cases_across_trigger_and_nontrigger_behavior
- rel: supports
  target_object_id: PAT_isolate_agent_eval_trials_from_shared_state
- rel: supports
  target_object_id: PAT_grade_agent_outcomes_without_overconstraining_valid_paths
- rel: supports
  target_object_id: PAT_calibrate_llm_judges_against_human_graders
- rel: supports
  target_object_id: PAT_audit_the_evaluator_when_agent_scores_look_wrong
- rel: supports
  target_object_id: PAT_refresh_capability_evals_before_they_saturate
- rel: supports
  target_object_id: PAT_combine_offline_evals_with_production_feedback
reference:
  source_title: Demystifying evals for AI agents
  author: Mikaela Grace, Jeremy Hadfield, Rodrigo Olivares, Jiri De Jonghe, with Anthropic contributors
confidence: high
references: []
variants: []
---

# Build and Maintain an Agent Evaluation Suite

## Objective
Create an evaluation system that measures agent capability and reliability without confusing model behavior with grader defects, and keep that system useful as the agent and production distribution evolve.

## Steps / Flow
1. **Separate the questions the suite must answer.** Establish a capability set with real headroom and a regression set for behavior already expected to remain reliable using `PAT_keep_capability_and_regression_evals_separate`. *Gate:* each task has a stated purpose; improvement tasks and preservation tasks are not mixed into one uninterpretable score.
2. **Build realistic, balanced tasks.** Start from actual workflows, manual checks, and observed failures. Where a behavior conditionally triggers, use `PAT_balance_agent_eval_cases_across_trigger_and_nontrigger_behavior`. Require a known-valid reference solution for tasks whose solvability or grader configuration could be uncertain.
3. **Make each trial a valid experiment.** Use `PAT_isolate_agent_eval_trials_from_shared_state` so prior runs, caches, histories, or resource exhaustion cannot confound results. When behavior is stochastic, apply `PAT_measure_stochastic_agent_reliability_across_multiple_trials` and select metrics whose retry assumptions match the deployed product.
4. **Grade the evidence, not the story.** Verify durable outcomes with `PAT_verify_agent_success_from_resulting_state`. Apply `PAT_match_agent_eval_graders_to_the_evidence_type` to use deterministic checks where possible and model/human judgment only where necessary. Preserve alternate correct strategies with `PAT_grade_agent_outcomes_without_overconstraining_valid_paths`.
5. **Validate every probabilistic judge.** When an LLM grader is necessary, use `PAT_calibrate_llm_judges_against_human_graders` before treating its scores as decision-grade evidence. *Gate:* representative judge-human disagreement is understood and the rubric has an abstention path for insufficient evidence.
6. **Run, inspect, and challenge the measurement system.** Sample complete traces and grades. If failures look unfair, surprising, or immovable, apply `PAT_audit_the_evaluator_when_agent_scores_look_wrong` before changing the model or agent. Do not promote a score into a model-selection or release decision until evaluator defects have been ruled out.
7. **Keep the suite ahead of the system.** Apply `PAT_refresh_capability_evals_before_they_saturate` as capability tasks become solved, moving stable behavior into regression coverage while adding harder work that retains measurement headroom.
8. **Close the production loop.** After deployment, use `PAT_combine_offline_evals_with_production_feedback` to combine offline checks with monitoring, user evidence, experiments, trace review, and periodic human calibration. Promote important reproducible production failures into the regression suite.

## Notes
The suite is not a static benchmark file. It is a maintained measurement system whose tasks, environments, graders, reliability statistics, and production feedback loops all influence whether a score means what the team thinks it means. The ordering above intentionally validates the evaluator before using its output to steer model or product decisions.
