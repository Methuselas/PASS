---
object_id: PAT_autoscale_inference_on_workload_relevant_signals
object_type: pattern
name: Autoscale Inference on Workload-Relevant Signals
library_path:
- software-engineering
- ai-systems
- runtime-operations
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: none
tags:
- ai
- inference
- autoscaling
- runtime
- capacity
- slo
cross_links:
- rel: related_to
  target_object_id: PAT_tune_inference_serving_as_a_workload_specific_profile
- rel: related_to
  target_object_id: PAT_preposition_and_share_model_weights_for_faster_startup
reference:
  source_title: The production platform for open-weight AI inference
  author: Nikitha Suryadevara, Ted Cui, Will Van Eaton, and Charles Zedlewski
confidence: high
references: []
variants: []
---

# Autoscale Inference on Workload-Relevant Signals

## Pattern Rule
**IF** inference demand changes over time and replicas or capacity can be scaled dynamically
**THEN** drive scaling from the signal that best represents the workload's bottleneck or SLO rather than relying on one generic utilization metric for every service
**ELSE** use fixed capacity when demand is stable enough that autoscaling complexity adds no operational value.

## Do
- Consider inflight requests, GPU utilization, TTFT, end-to-end latency, decoding speed, or throughput as candidate signals according to the workload.
- Select scaling thresholds from observed SLO behavior instead of from a provider default alone.
- Account for replica startup time when deciding how early to scale; combine autoscaling with weight prewarming when cold starts are material.
- Validate both scale-up and scale-down behavior under representative traffic spikes and lulls.
- Monitor the chosen signal alongside user-facing latency and throughput so the autoscaler can be corrected when its proxy stops matching the real objective.

## Don't
- Don't assume GPU utilization is always the best demand signal for every model and traffic shape.
- Don't scale on a metric that reacts only after the user-facing SLO is already badly degraded.
- Don't ignore startup latency when calculating how quickly new capacity can absorb demand.
- Don't leave scale-down behavior untested; oscillation or aggressive contraction can create repeated cold starts and latency spikes.

## Checklist
- Which metric changes earliest when this workload approaches its SLO limit?
- Does the autoscaling signal represent queue pressure, compute pressure, or user-visible latency?
- How long does new inference capacity take to become ready?
- Are scale-up, scale-down, and burst scenarios tested?
- Do scaling decisions remain correlated with actual TTFT, latency, decode speed, or throughput?

## Notes
Inference autoscaling should not be limited to one generic metric. Different workloads may be better represented by inflight requests, GPU utilization, TTFT, latency, decoding speed, or throughput. The transferable principle is to bind capacity control to the workload's real limiting signal and SLO.
