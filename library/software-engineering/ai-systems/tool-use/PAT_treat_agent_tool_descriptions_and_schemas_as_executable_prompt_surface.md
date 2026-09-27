---
object_id: PAT_treat_agent_tool_descriptions_and_schemas_as_executable_prompt_surface
object_type: pattern
name: Treat Agent Tool Descriptions and Schemas as Executable Prompt Surface
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
- schemas
- prompting
cross_links:
- rel: related_to
  target_object_id: PAT_namespace_agent_tools_to_expose_functional_boundaries
reference:
  source_title: Writing effective tools for agents — with agents
  author: Ken Aizawa with Anthropic contributors
confidence: high
references: []
variants: []
---

# Treat Agent Tool Descriptions and Schemas as Executable Prompt Surface

## Pattern Rule
**IF** a model chooses and calls a tool from its name, description, parameter schema, and examples
**THEN** design those fields as part of the agent's executable behavior contract and evaluate changes to them like code changes
**ELSE** ordinary documentation can remain secondary when no model consumes it to decide what action to take.

## Do
- Explain the tool as if onboarding a capable teammate who lacks your implicit domain knowledge.
- Define specialized terminology, query formats, resource relationships, constraints, and expected outputs explicitly.
- Use unambiguous parameter names and strict schemas that remove interpretations the implementation cannot support.
- Keep the description consistent with the actual implementation and with neighboring tools after every interface change.
- Measure whether description or schema edits improve tool selection and argument quality on held-out tasks.

## Don't
- Don't treat tool descriptions as comments that can drift while the implementation changes.
- Don't hide a critical usage rule in prose when a stricter schema can make the invalid call unrepresentable.
- Don't use vague parameter names whose meaning depends on undocumented context.
- Don't assume a wording change is cosmetic when it changes the tokens from which the model chooses its action.

## Checklist
- Could an agent infer when to use this tool from the visible contract alone?
- Are domain-specific terms and formats defined rather than assumed?
- Do parameter names and types rule out ambiguous interpretations?
- Does the description still match the implementation and neighboring tools?
- Has a meaningful contract change been checked against agent-use evaluations?

## Notes
For a model caller, the visible tool specification is not merely a reference manual. It is injected into the same context that drives action selection, so wording, names, parameter types, and examples directly alter behavior. That makes the specification closer to executable configuration than passive documentation and gives it the same obligation to stay synchronized and tested.
