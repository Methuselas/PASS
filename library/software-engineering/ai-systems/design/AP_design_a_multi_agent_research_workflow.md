---
object_id: AP_design_a_multi_agent_research_workflow
object_type: ap
name: Design a Multi-Agent Research Workflow
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
- research
- orchestration
- workflow
cross_links:
- rel: supports
  target_object_id: PAT_choose_multi_agent_architecture_for_parallelizable_high_value_work
- rel: supports
  target_object_id: PAT_delegate_subagents_with_explicit_task_contracts
- rel: supports
  target_object_id: PAT_scale_agent_effort_to_task_complexity
- rel: supports
  target_object_id: PAT_parallelize_independent_agent_and_tool_work
- rel: supports
  target_object_id: PAT_persist_subagent_artifacts_and_pass_references
- rel: supports
  target_object_id: PAT_keep_long_running_agent_runs_on_compatible_deployment_versions
- rel: supports
  target_object_id: PAT_persist_agent_working_notes_outside_context
- rel: supports
  target_object_id: PAT_grade_agent_outcomes_without_overconstraining_valid_paths
- rel: supports
  target_object_id: PAT_debug_agent_tools_from_complete_execution_traces
reference:
  source_title: How we built our multi-agent research system
  author: Jeremy Hadfield, Barry Zhang, Kenneth Lien, Florian Scholz, Jeremy Fox, and Daniel Ford
confidence: high
references: []
variants: []
---

# Design a Multi-Agent Research Workflow

## Objective
Build a research workflow in which a lead agent decomposes an open-ended query, delegates independent branches to specialized subagents, controls the amount of work spent, preserves useful outputs outside transient contexts, and synthesizes the results into a coherent answer without making multi-agent coordination itself the source of duplicated work, runaway cost, or deployment fragility.

## Steps / Flow
1. **Qualify the task for multi-agent execution.** Apply `PAT_choose_multi_agent_architecture_for_parallelizable_high_value_work`. Use fan-out when the query contains multiple independent research directions, benefits from more context or tool capacity, and has enough value to justify the cost. *Gate:* if the work is tightly coupled or cheap enough for one agent, do not add subagents.
2. **Create and persist the lead plan.** The coordinator identifies the research strategy, open branches, and expected synthesis criteria. Persist durable planning state with `PAT_persist_agent_working_notes_outside_context` when the run may exceed one context or survive interruptions.
3. **Define the division of labor.** For each branch, use `PAT_delegate_subagents_with_explicit_task_contracts` to state the objective, expected output, source/tool guidance, and boundaries relative to sibling workers. *Advance only when* the assignments are distinct enough to avoid obvious duplication and collectively cover the required question.
4. **Allocate effort deliberately.** Use `PAT_scale_agent_effort_to_task_complexity` to choose the number of workers, tool-call budget, and exploration depth. Start with the effort justified by the query rather than the maximum available fan-out.
5. **Execute independent work concurrently.** Apply `PAT_parallelize_independent_agent_and_tool_work` to run independent subagents and tool calls in parallel. Keep evidence-dependent refinements sequential inside a branch when later searches need earlier findings.
6. **Return high-signal findings without losing full artifacts.** Subagents provide concise findings for synthesis. When a worker produces a large structured result that downstream stages may need intact, use `PAT_persist_subagent_artifacts_and_pass_references` instead of copying or repeatedly summarizing it through the coordinator.
7. **Synthesize, inspect gaps, and adapt.** The lead agent merges results, checks the requested coverage, and decides whether evidence is sufficient. If a gap remains, create a new bounded assignment or refine an existing branch rather than blindly increasing all workers' budgets.
8. **Evaluate the outcome and coordination behavior.** Grade results with `PAT_grade_agent_outcomes_without_overconstraining_valid_paths`, because different valid searches can reach the same answer. Use complete traces through `PAT_debug_agent_tools_from_complete_execution_traces` to diagnose duplication, poor tool choice, premature stopping, or runaway search effort.
9. **Protect long-running production work across failures and deploys.** Use durable checkpoints for resumable execution and `PAT_keep_long_running_agent_runs_on_compatible_deployment_versions` so prompt/tool/runtime changes do not strand runs that started under an older contract.
10. **Completion check.** Verify that the task actually benefited from parallel decomposition, every branch had a clear owner, fan-out stayed within budget, synthesis preserved necessary evidence, failures were recoverable without restarting the whole job, and deployment behavior does not invalidate in-flight state.

## Notes
An orchestrator-worker research system has a lead agent that plans and delegates, subagents that search independently, synthesis that may trigger additional work, and later stages that attach citations. The reusable workflow is not “spawn many agents.” It is a controlled loop of qualification, explicit delegation, bounded parallel execution, synthesis, evaluation, and durable production operation.
