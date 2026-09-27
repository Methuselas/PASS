---
object_id: PAT_cluster_production_traces_to_discover_usage_and_failure_patterns
object_type: pattern
name: Cluster Production Traces to Discover Usage and Failure Patterns
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
- clustering
- failure_analysis
cross_links:
- rel: supports
  target_object_id: PAT_combine_offline_evals_with_production_feedback
- rel: related_to
  target_object_id: PAT_debug_agent_tools_from_complete_execution_traces
- rel: related_to
  target_object_id: PAT_grow_agent_prompts_from_observed_failures
reference:
  source_title: You don’t know what your agent will do until it’s in production
  author: Harrison Chase and Sam Crowder
confidence: high
references: []
variants: []
---

# Cluster Production Traces to Discover Usage and Failure Patterns

## Pattern Rule
**IF** production traffic is too large and open-ended to enumerate every important user intent or failure category in advance
**THEN** group similar traces to discover recurring usage patterns, common error modes, and unexpected edge cases, then inspect representative examples before turning a discovered cluster into a metric, evaluator, or product conclusion
**ELSE** use explicit filters and known categories when the behavior space is already narrow and well defined.

## Do
- Cluster traces by the question you are trying to answer, such as user intent, failure mode, tool-selection error, or another domain-specific behavior.
- Restrict analysis to relevant time windows, cohorts, features, or other subsets when the full traffic distribution would hide the pattern of interest.
- Surface representative traces from each cluster so people can verify what the grouping actually means.
- Use discovered failure clusters to prioritize investigation and propose new evaluation cases or monitoring criteria.
- Use discovered usage clusters to understand which agent capabilities users are actually exercising in production.
- Save repeatable analyses when the same pattern discovery is useful across releases or time periods.

## Don't
- Don't require operators to know every production failure category before monitoring begins.
- Don't treat cluster labels as ground truth without inspecting representative traces.
- Don't collapse unrelated cohorts or time periods when distribution differences are material to the question.
- Don't turn one unusual trace into a "common failure mode" without evidence that similar cases recur.
- Don't stop at pattern discovery; connect important clusters to debugging, evaluation, or product follow-up.

## Checklist
- What kind of similarity is the clustering meant to surface: intent, failure, tool use, or another behavior?
- Is the analyzed traffic slice appropriate to that question?
- Can a reviewer inspect representative traces for every important cluster?
- Which clusters recur often enough or matter enough to deserve dedicated evaluation coverage?
- Are newly discovered categories tracked over time rather than rediscovered from scratch each incident?

## Notes
Natural-language input is effectively open-ended, so a fixed catalog of known production categories can miss behaviors the team did not anticipate. Automated grouping may surface recurring usage patterns, error modes, and edge cases, but representative traces still need inspection before a cluster is treated as a stable product conclusion.
