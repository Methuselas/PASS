---
object_id: PAT_delegate_subagents_with_explicit_task_contracts
object_type: pattern
name: Delegate Subagents with Explicit Task Contracts
library_path:
- software-engineering
- ai-systems
- modularity
stage_binding: 0 design
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: PAT_isolate_ai_agents_by_task_context_and_permissions
tags:
- ai_agents
- multi_agent
- delegation
- orchestration
- task_contracts
cross_links:
- rel: supports
  target_object_id: PAT_isolate_ai_agents_by_task_context_and_permissions
- rel: related_to
  target_object_id: PAT_write_agent_instructions_at_the_right_altitude
- rel: related_to
  target_object_id: PAT_treat_agent_tool_descriptions_and_schemas_as_executable_prompt_surface
reference:
  source_title: How we built our multi-agent research system
  author: Jeremy Hadfield, Barry Zhang, Kenneth Lien, Florian Scholz, Jeremy Fox, and Daniel Ford
confidence: high
references: []
variants: []
---

# Delegate Subagents with Explicit Task Contracts

## Pattern Rule
**IF** a coordinator delegates open-ended work to subagents
**THEN** give every subagent an explicit task contract that states its objective, expected output, relevant tools or source guidance, and boundaries relative to sibling workers
**ELSE** use a simpler shared task only when overlap and ambiguity cannot create duplicated work or uncovered gaps.

## Do
- Define the concrete question or scope each subagent owns rather than delegating a broad topic label.
- State what the subagent should return so the coordinator can compare and synthesize outputs consistently.
- Tell the worker which tool classes or source types are appropriate when the task depends on choosing among heterogeneous resources.
- Describe boundaries between sibling assignments so each worker knows what not to cover as well as what to cover.
- Make the division of labor collectively exhaustive enough for the coordinator to detect gaps before synthesis.
- Revise delegation prompts when traces show repeated duplication, scope drift, or missed coverage.

## Don't
- Don't dispatch several workers with near-identical vague instructions and assume diversity will emerge automatically.
- Don't make the coordinator infer after the fact which worker was responsible for an uncovered part of the task.
- Don't bury the desired output format or source constraints in generic role text.
- Don't give every worker the same broad scope when the purpose of fan-out is independent coverage.

## Checklist
- What exact objective does this worker own?
- What output format or evidence should it return?
- Which tools or source classes are appropriate for this assignment?
- What are the boundaries with sibling workers?
- Would two workers plausibly perform the same search from these instructions?
- Can the coordinator identify a missing branch before accepting the combined result?

## Notes
Vague delegation can cause subagents to misinterpret assignments, duplicate searches, and leave gaps. Delegation quality is therefore part of the system architecture: the orchestrator is not only spawning workers, it is defining interfaces between them. This pattern complements task/context isolation by specifying the work contract carried across that boundary.
