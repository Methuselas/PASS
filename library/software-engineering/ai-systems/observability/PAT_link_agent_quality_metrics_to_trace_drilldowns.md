---
object_id: PAT_link_agent_quality_metrics_to_trace_drilldowns
object_type: pattern
name: Link Agent Quality Metrics to Trace Drill-Downs
library_path:
- software-engineering
- ai-systems
- observability
stage_binding: 4 final
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: none
tags:
- ai_agents
- observability
- production
- dashboards
- alerts
- traces
cross_links:
- rel: related_to
  target_object_id: PAT_capture_semantic_agent_interactions_for_production_observability
- rel: related_to
  target_object_id: PAT_run_online_evaluators_on_sampled_or_filtered_production_traffic
- rel: related_to
  target_object_id: PAT_debug_agent_tools_from_complete_execution_traces
reference:
  source_title: You don’t know what your agent will do until it’s in production
  author: Harrison Chase and Sam Crowder
confidence: high
references: []
variants: []
---

# Link Agent Quality Metrics to Trace Drill-Downs

## Pattern Rule
**IF** production monitoring uses aggregate metrics or evaluator scores to detect agent quality problems
**THEN** pair those aggregates with alerts and direct drill-down to the specific traces that contributed to the signal so operators can move from "a metric changed" to concrete behavioral evidence
**ELSE** use simpler telemetry when the monitored condition is already fully diagnosable from a deterministic metric alone.

## Do
- Track business- and behavior-specific measures such as task success, user satisfaction, tool-call failure rate, or tool-use frequency alongside latency, cost, and infrastructure errors.
- Segment dashboards by workflow, feature area, model version, or another dimension that helps localize regressions.
- Define alerts on metrics whose degradation warrants action rather than on every available signal.
- Preserve a path from aggregate values to the underlying traces and representative examples.
- Compare quality with cost and latency so an improvement in one dimension does not hide a regression in another.
- Use trace drill-down to determine whether an alert reflects a real behavioral change, evaluator noise, data drift, or an infrastructure issue.

## Don't
- Don't stop at uptime, request success, and latency when the agent can return a technically successful but semantically wrong response.
- Don't build dashboards of quality scores that cannot be traced back to the interactions that produced them.
- Don't alert on every noisy metric without a defined operator response.
- Don't use one global average when a regression is isolated to a particular model version, workflow, tool, or cohort.
- Don't infer root cause from an aggregate trend without inspecting the underlying traces.

## Checklist
- Which metrics represent whether the agent is accomplishing its intended job?
- Can metrics be segmented by the dimensions needed to localize a change?
- Does every actionable quality alert lead to concrete traces for investigation?
- Are cost, latency, and quality visible together where trade-offs matter?
- Is there a defined response when a monitored threshold degrades?

## Notes
When infrastructure health does not explain agent quality, operational dashboards may also need behavior or business-outcome signals. Aggregation can make large-scale trends visible; trace drill-down provides concrete evidence for investigating why a measured trend changed.
