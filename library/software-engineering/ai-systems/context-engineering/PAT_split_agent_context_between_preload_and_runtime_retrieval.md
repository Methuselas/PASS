---
object_id: PAT_split_agent_context_between_preload_and_runtime_retrieval
object_type: pattern
name: Split Agent Context Between Preload and Runtime Retrieval
library_path:
- software-engineering
- ai-systems
- context-engineering
stage_binding: 0 design
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: PAT_budget_agent_context_for_signal_density
tags:
- ai_agents
- context_engineering
- retrieval
- latency
cross_links:
- rel: related_to
  target_object_id: PAT_retrieve_agent_context_just_in_time
reference:
  source_title: Effective context engineering for AI agents
  author: Anthropic Engineering
confidence: high
references: []
variants: []
---

# Split Agent Context Between Preload and Runtime Retrieval

## Pattern Rule
**IF** an agent needs some information on nearly every run while other detail is large, dynamic, or only conditionally relevant
**THEN** preload the stable, frequently needed guidance and retrieve conditional detail at runtime, choosing the split by latency, freshness, and context cost
**ELSE** use a single retrieval strategy when the task is small enough that the hybrid boundary adds no practical value.

## Do
- Put stable operating guidance, task-critical constraints, and small high-frequency facts in the initial context when waiting to retrieve them would only add latency.
- Leave large, volatile, or rarely needed material behind search and navigation tools so the agent loads it only when a branch requires it.
- Measure the runtime cost of exploration as well as the token cost of preload; shifting everything to on-demand retrieval can make an otherwise efficient agent slow.
- Prefer direct access to fresh underlying resources when maintaining a precomputed index would add staleness without enough speed benefit.
- Revisit the split as models, retrieval tools, data volume, and latency requirements change.

## Don't
- Don't preload every potentially relevant document merely to avoid tool calls later.
- Don't force the agent to rediscover stable instructions or universally required facts on every run.
- Don't assume precomputed retrieval is always superior; an index can become stale while direct navigation remains current.
- Don't adopt a hybrid architecture when the simpler preload-only or retrieval-only design already meets the task's reliability and latency needs.

## Checklist
- Which information is stable and needed on most runs?
- Which information is large, dynamic, or needed only after a branch is known?
- What latency is added by runtime exploration, and what context is saved by avoiding preload?
- Does any precomputed retrieval layer create a freshness problem the agent could avoid by navigating the source directly?
- Is the chosen split simpler than alternatives while still meeting task requirements?

## Notes
Preload and agentic retrieval optimize different costs. Preload buys immediate availability at the expense of attention and freshness; runtime retrieval preserves context and can access current data but spends tool calls and wall-clock time. The useful architecture places the boundary where the task's actual frequency, volatility, and latency make each side pay for itself.
