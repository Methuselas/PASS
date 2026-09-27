---
object_id: AP_maintain_long_horizon_agent_continuity
object_type: ap
name: Maintain Long-Horizon Agent Continuity
library_path:
- software-engineering
- ai-systems
- context-engineering
stage_binding: 0 design
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: none
tags:
- ai_agents
- context_engineering
- long_horizon
- continuity
cross_links:
- rel: supports
  target_object_id: PAT_budget_agent_context_for_signal_density
- rel: supports
  target_object_id: PAT_retrieve_agent_context_just_in_time
- rel: supports
  target_object_id: PAT_split_agent_context_between_preload_and_runtime_retrieval
- rel: supports
  target_object_id: PAT_compact_agent_context_around_durable_state
- rel: supports
  target_object_id: PAT_persist_agent_working_notes_outside_context
- rel: supports
  target_object_id: PAT_isolate_ai_agents_by_task_context_and_permissions
reference:
  source_title: Effective context engineering for AI agents
  author: Anthropic Engineering
confidence: high
references: []
variants: []
---

# Maintain Long-Horizon Agent Continuity

## Objective
Keep an agent coherent across long tasks, context growth, resets, and delegated exploration without carrying the entire interaction history in every model call.

## Steps / Flow
1. **Name the continuity state before choosing a mechanism.** Identify the current goal, accepted decisions, unresolved problems, dependencies, and artifacts that future work must preserve. Use `PAT_budget_agent_context_for_signal_density` to distinguish durable signal from interaction history that merely happened to produce it.
2. **Keep ordinary detail external until it is needed.** Apply `PAT_split_agent_context_between_preload_and_runtime_retrieval` and `PAT_retrieve_agent_context_just_in_time` so stable guidance is readily available while large or dynamic evidence remains behind targeted retrieval. *Gate:* the live context contains enough information to act but is not the only copy of state required after a reset.
3. **Choose the continuity mechanism by task shape.** For sequential work whose conversational thread must continue, use `PAT_compact_agent_context_around_durable_state`. For iterative work with milestones, resumptions, and explicit open items, use `PAT_persist_agent_working_notes_outside_context`. For context-heavy or separable exploration, use `PAT_isolate_ai_agents_by_task_context_and_permissions` so a worker gets a clean context and returns a distilled result. Combine mechanisms when the task has more than one of these shapes.
4. **Externalize state before a boundary destroys access to it.** Update working notes before stopping or resetting. Compact before the active history becomes too noisy or reaches the hard limit. Give delegated workers the task, evidence access, and authority they need while the coordinator retains the high-level plan. *Advance only when* the next context can recover the commitments that still matter.
5. **Resume from durable state, then retrieve detail on demand.** A fresh context first loads the compacted state or current working notes, then retrieves supporting artifacts as the next decisions require them. A coordinator incorporates distilled subagent results rather than importing the workers' full scratch histories.
6. **Recover by repairing the failed continuity boundary.** If a reset loses an important dependency, restore it from durable artifacts when possible, then increase compaction recall or improve what the working notes capture. If the coordinator cannot act from a subagent handoff, request the missing evidence or revise the handoff contract instead of copying all exploratory context by default.
7. **Completion check.** Start from a fresh or reduced context and verify that the agent can state the current goal, binding decisions, unresolved work, dependencies, and next action; retrieve required detail without full-history preload; and continue without contradictory stale notes or hidden reliance on discarded conversation state.

## Notes
These mechanisms solve different continuity problems and are intentionally composable. Compaction carries a conversational thread across a context reset, external notes maintain explicit project state over milestones and resumptions, and isolated subagents prevent one deep exploration from consuming the coordinator's working context. The common invariant is that important state survives outside whichever context is about to be discarded.
