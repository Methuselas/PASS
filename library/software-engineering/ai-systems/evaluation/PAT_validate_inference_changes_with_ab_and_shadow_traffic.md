---
object_id: PAT_validate_inference_changes_with_ab_and_shadow_traffic
object_type: pattern
name: Validate Inference Changes with A/B and Shadow Traffic
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
- ai
- inference
- evaluation
- ab_testing
- shadow_traffic
- production
cross_links:
- rel: related_to
  target_object_id: PAT_combine_offline_evals_with_production_feedback
- rel: related_to
  target_object_id: PAT_run_online_evaluators_on_sampled_or_filtered_production_traffic
- rel: related_to
  target_object_id: PAT_roll_out_inference_changes_with_progressive_traffic_and_rollback_gates
reference:
  source_title: The production platform for open-weight AI inference
  author: Nikitha Suryadevara, Ted Cui, Will Van Eaton, and Charles Zedlewski
confidence: high
references: []
variants: []
---

# Validate Inference Changes with A/B and Shadow Traffic

## Pattern Rule
**IF** a new model, checkpoint, hardware profile, or serving configuration is ready for production evaluation
**THEN** test it on representative live traffic through controlled A/B routing or shadow mirroring before broad rollout
**ELSE** rely on offline evaluation alone only when live-traffic testing is impossible or the change has no meaningful production-behavior risk.

## Do
- Use A/B routing when both variants may safely serve users and you need directly comparable outcome, quality, or performance measurements.
- Use shadow traffic when a candidate should receive real production requests but must not influence the user-visible response yet.
- Compare the candidate on the metrics relevant to the change: behavior/quality, latency, throughput, cost, errors, or scaling characteristics.
- Keep request cohorts and deployment versions attributable so measurements from different variants are not mixed.
- Feed validated findings into the rollout decision rather than treating real-traffic tests as dashboards with no promotion gate.

## Don't
- Don't assume synthetic benchmarks reproduce production prompt distributions, concurrency, or system interactions.
- Don't send user-visible traffic to an unvalidated candidate when shadowing can collect the needed evidence with lower risk.
- Don't compare variants without preserving which deployment served or shadowed each request.
- Don't let A/B traffic splitting substitute for a clear success criterion.

## Checklist
- Does this change need user-visible A/B exposure or non-serving shadow exposure?
- Which production metrics determine whether the candidate is acceptable?
- Can every observation be attributed to a deployment version and cohort?
- Are offline and live-traffic results compared when they disagree?
- Does the result feed a defined promote, hold, or rollback decision?

## Notes
Two useful production tests serve different purposes: A/B testing routes a controlled share of live traffic to different deployments, while shadowing mirrors real requests to a candidate without changing the response seen by the user. This complements existing evaluation patterns by owning the deployment-level validation of weights, configurations, and hardware under actual traffic.
