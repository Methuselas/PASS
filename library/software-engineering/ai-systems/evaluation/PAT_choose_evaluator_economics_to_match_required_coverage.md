---
object_id: PAT_choose_evaluator_economics_to_match_required_coverage
object_type: pattern
name: Choose Evaluator Economics to Match Required Coverage
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
- cost
- latency
- observability
cross_links:
- rel: related_to
  target_object_id: PAT_use_typed_semantic_judges_for_bounded_eval_decisions
- rel: supports
  target_object_id: PAT_combine_offline_evals_with_production_feedback
- rel: related_to
  target_object_id: PAT_measure_stochastic_agent_reliability_across_multiple_trials
reference:
  source_title: Jev is now available in LangSmith Evals
  author: Winston Huynh
confidence: high
references: []
variants: []
---

# Choose Evaluator Economics to Match Required Coverage

## Pattern Rule
**IF** evaluator cost or latency would force you to sample too few traces, score too few criteria, or avoid repeat judgments that the reliability question actually needs
**THEN** choose the least expensive and lowest-latency evaluator that still meets the required semantic quality, and spend the saved budget on the coverage, criteria, and repetition the evaluation plan requires
**ELSE** keep the more expressive evaluator when its reasoning quality or written explanation is itself necessary evidence.

## Do
- Model evaluation cost from production volume, traces scored, criteria per trace, repeated trials, and change/regression frequency rather than comparing only the price of one call.
- Include evaluator latency in online-eval design when feedback is expected to keep pace with live traffic or trigger timely operational response.
- Prefer evaluators that can score multiple independent criteria together when doing so preserves the meaning of each criterion and materially reduces marginal cost or latency.
- Use lower evaluator cost to increase useful measurement coverage: more traces, more criteria, or repeated judgments for consistency rather than simply reducing the evaluation budget.
- Reserve expensive generative judges for criteria that need open-ended reasoning, written justification, or cases escalated from cheaper first-line evaluators.
- Benchmark candidate judges on representative traces and human-labeled cases before extrapolating vendor or single-benchmark claims to your own workload.
- Revisit the economics when traffic, evaluator pricing, model behavior, or the number of feedback dimensions changes.

## Don't
- Don't design an evaluation suite whose per-call judge cost makes the intended production coverage financially impossible.
- Don't treat a fast or cheap judge as acceptable solely because it increases coverage; incorrect high-volume grading is still bad instrumentation.
- Don't compare evaluators only by headline accuracy while ignoring variance, latency, structured-output failure modes, and total run cost.
- Don't generalize one benchmark on one agent into a universal evaluator ranking.
- Don't bundle unrelated criteria into one opaque score merely to save calls when independent feedback keys would be more actionable.

## Checklist
- How many production traces should be evaluated, and what fraction is affordable with the current judge?
- How many criteria must be scored per trace?
- Do any criteria require repeated judgments to measure evaluator consistency?
- What latency is acceptable for offline scoring versus live operational feedback?
- Which criteria truly require generative reasoning rather than a bounded semantic decision?
- Has the candidate evaluator been tested against representative human judgments from this workload?

## Notes
Evaluation quality depends partly on how much behavior can actually be measured. A judge that is excellent per call but too expensive or slow to run at the required scale can produce a weaker feedback loop than a cheaper judge that is sufficiently accurate for the bounded decision and can cover far more traces.

A favorable single-agent Jev comparison on accuracy, consistency, speed, and cost is still only one test. Treat such results as a reason to benchmark the architecture on your own distribution, not as a universal product verdict.
