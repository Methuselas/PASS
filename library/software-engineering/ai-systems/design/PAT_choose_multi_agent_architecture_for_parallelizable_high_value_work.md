---
object_id: PAT_choose_multi_agent_architecture_for_parallelizable_high_value_work
object_type: pattern
name: Choose Multi-Agent Architecture for Parallelizable High-Value Work
library_path:
- software-engineering
- ai-systems
- design
stage_binding: 0 design
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: none
tags:
- ai_agents
- multi_agent
- architecture
- parallelism
- economics
cross_links:
- rel: related_to
  target_object_id: PAT_isolate_ai_agents_by_task_context_and_permissions
- rel: related_to
  target_object_id: PAT_budget_agent_context_for_signal_density
- rel: supports
  target_object_id: PAT_scale_agent_effort_to_task_complexity
reference:
  source_title: How we built our multi-agent research system
  author: Jeremy Hadfield, Barry Zhang, Kenneth Lien, Florian Scholz, Jeremy Fox, and Daniel Ford
confidence: high
references: []
variants: []
---

# Choose Multi-Agent Architecture for Parallelizable High-Value Work

## Pattern Rule
**IF** a task can be decomposed into multiple largely independent lines of investigation, benefits from more working context or tool activity than one agent can efficiently carry, and is valuable enough to justify materially higher inference cost
**THEN** consider a multi-agent orchestrator-worker architecture that lets specialized workers explore in parallel and return compressed findings to a coordinator
**ELSE** prefer a single-agent or simpler workflow when the work is tightly dependent, requires all workers to share the same context, or does not justify the extra coordination and token cost.

## Do
- Look for natural breadth-first decomposition: independent entities, hypotheses, sources, regions, time periods, or other branches that can be researched simultaneously.
- Treat separate subagent contexts as additional working capacity, not merely as a way to rename sequential steps.
- Use multi-agent execution when the task benefits from distinct tools, prompts, or exploration trajectories and the coordinator can synthesize the outputs afterward.
- Compare the performance gain against the increased token and tool-call budget before making multi-agent execution the default.
- Keep tightly coupled work in one agent when frequent cross-branch coordination would erase the benefits of independent exploration.

## Don't
- Don't add subagents to a task just because the runtime supports them.
- Don't assume work is parallelizable when each branch depends heavily on discoveries from the others.
- Don't make a high-cost multi-agent path the default for low-value fact lookup or routine chat.
- Don't confuse more agents with better decomposition; duplicated or overlapping branches can spend more tokens without adding coverage.

## Checklist
- Can the task be split into independent branches that can make progress at the same time?
- Does one context window or one sequential search path constrain coverage?
- Can workers operate with distinct prompts, tools, or evidence and return concise results?
- How much additional token and tool-call cost will the architecture consume?
- Is the value of the task high enough to justify that cost?
- Would shared-context dependencies make a single agent simpler and more reliable?

## Notes
On breadth-first research workloads with genuinely independent branches, multi-agent execution can increase parallel search capacity, but token use and coordination overhead can also rise materially. Measure those effects on the target workload. Use multiple agents only when the observed task shape and economics support the trade, not as a universal upgrade.
