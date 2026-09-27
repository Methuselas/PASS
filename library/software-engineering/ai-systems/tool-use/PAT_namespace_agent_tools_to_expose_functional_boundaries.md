---
object_id: PAT_namespace_agent_tools_to_expose_functional_boundaries
object_type: pattern
name: Namespace Agent Tools to Expose Functional Boundaries
library_path:
- software-engineering
- ai-systems
- tool-use
stage_binding: 0 design
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: PAT_convey_usage_through_names_and_types
tags:
- ai_agents
- tool_use
- naming
- namespaces
cross_links:
- rel: related_to
  target_object_id: PAT_expose_task_level_tools_not_raw_api_surfaces
reference:
  source_title: Writing effective tools for agents — with agents
  author: Ken Aizawa with Anthropic contributors
confidence: high
references: []
variants: []
---

# Namespace Agent Tools to Expose Functional Boundaries

## Pattern Rule
**IF** an agent can choose among many tools from different services, resources, or capability groups
**THEN** encode those boundaries consistently in tool names so related actions cluster visibly and overlapping verbs do not become ambiguous
**ELSE** keep simple standalone names when the tool set is small enough that no competing interpretation exists.

## Do
- Use a consistent service or resource namespace when several tool families expose similar operations such as search, get, create, or update.
- Keep the semantic action visible after the namespace so the name still tells the agent what the tool does.
- Choose prefix or suffix schemes by evaluation when model behavior differs; naming is part of the executable interface.
- Align names with the same natural task boundaries used to design the tool surface.
- Rename or remove ambiguous tools when traces show systematic selection errors.

## Don't
- Don't publish several bare `search`, `get`, or `create` tools whose only distinction lives in a long description.
- Don't mix naming schemes across one tool surface without a reason the agent can recognize.
- Don't assume a naming convention is harmless because it is obvious to human developers; test whether the target model selects the intended tools.
- Don't use namespacing to paper over tools that are still functionally redundant.

## Checklist
- Can a reader tell which service or resource owns each ambiguous action from the tool name alone?
- Are related tools named with one consistent scheme?
- Does the name reveal both the capability group and the semantic action?
- Have naming variants been evaluated when tool selection is sensitive to the scheme?
- Are persistent selection mistakes fixed in the names or surface rather than only explained in more prompt text?

## Notes
Tool names are not passive labels for an agent. They are part of the context from which the model infers what actions exist and which one applies. When many tool families share common verbs, namespacing can reduce ambiguity, but held-out evaluation must determine whether a proposed naming scheme actually improves model tool selection.
