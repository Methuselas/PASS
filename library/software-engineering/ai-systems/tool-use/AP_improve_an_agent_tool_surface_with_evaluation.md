---
object_id: AP_improve_an_agent_tool_surface_with_evaluation
object_type: ap
name: Improve an Agent Tool Surface with Evaluation
library_path:
- software-engineering
- ai-systems
- tool-use
stage_binding: 3 rough
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: none
tags:
- ai_agents
- tool_use
- evaluation
- api_design
cross_links:
- rel: supports
  target_object_id: PAT_evaluate_agent_tools_on_realistic_multistep_tasks
- rel: supports
  target_object_id: PAT_expose_task_level_tools_not_raw_api_surfaces
- rel: supports
  target_object_id: PAT_namespace_agent_tools_to_expose_functional_boundaries
- rel: supports
  target_object_id: PAT_treat_agent_tool_descriptions_and_schemas_as_executable_prompt_surface
- rel: supports
  target_object_id: PAT_debug_agent_tools_from_complete_execution_traces
- rel: supports
  target_object_id: PAT_return_only_decision_relevant_context_from_agent_tools
- rel: supports
  target_object_id: PAT_make_agent_tool_errors_actionable_for_the_next_call
reference:
  source_title: Writing effective tools for agents — with agents
  author: Ken Aizawa with Anthropic contributors
confidence: high
references: []
variants: []
---

# Improve an Agent Tool Surface with Evaluation

## Objective
Turn a prototype agent tool surface into a measured interface that agents can select, call, recover from, and combine reliably on realistic work.

## Steps / Flow
1. **Define the evaluation before optimizing the interface.** Build realistic multistep tasks with verifiable outcomes and a held-out set using `PAT_evaluate_agent_tools_on_realistic_multistep_tasks`. Record task success, runtime, tool-call count, token use, and tool errors. Do not advance if the only evidence is a few hand-run happy paths.
2. **Right-size the tool surface around the tasks.** Apply `PAT_expose_task_level_tools_not_raw_api_surfaces` to remove endpoint-by-endpoint exposure and collapse deterministic call chains where the model gains no useful choice. *Gate:* each remaining tool has one recognizable semantic purpose.
3. **Make selection boundaries legible.** Apply `PAT_namespace_agent_tools_to_expose_functional_boundaries` and `PAT_treat_agent_tool_descriptions_and_schemas_as_executable_prompt_surface`. Names, descriptions, schemas, and examples must agree with the implementation before evaluation results are trusted.
4. **Run the evaluation and inspect complete traces.** Use `PAT_debug_agent_tools_from_complete_execution_traces` to locate the first observable divergence in failed or wasteful trials. Separate selection mistakes, bad arguments, insufficient responses, and misinterpreted responses rather than treating all failures as a model-quality problem.
5. **Repair the response contract at the failure point.** If the agent is flooded with irrelevant data, apply `PAT_return_only_decision_relevant_context_from_agent_tools`. If it cannot recover from a bad call, apply `PAT_make_agent_tool_errors_actionable_for_the_next_call`. If the wrong tool or parameter is chosen, return to the naming/schema decisions from step 3.
6. **Rerun both tuning and held-out tasks.** Accept a change only when the target failure improves without regressing held-out task success or creating a worse cost, latency, or error profile. If a change helps only the examples used to design it, undo or generalize it and repeat the loop.

## Notes
This protocol owns the iteration order, not the individual design rules. Its core workflow is prototype → evaluate → inspect traces → repair the tool interface → evaluate again. Keeping the held-out gate at the end prevents the loop from turning a general tool surface into a collection of prompts tuned to one test set.
