---
object_id: PAT_write_agent_instructions_at_the_right_altitude
object_type: pattern
name: Write Agent Instructions at the Right Altitude
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
- prompts
- instructions
cross_links:
- rel: related_to
  target_object_id: PAT_treat_agent_tool_descriptions_and_schemas_as_executable_prompt_surface
reference:
  source_title: Effective context engineering for AI agents
  author: Anthropic Engineering
confidence: high
references: []
variants: []
---

# Write Agent Instructions at the Right Altitude

## Pattern Rule
**IF** an agent needs behavioral guidance that must remain useful across varied cases
**THEN** state concrete goals, constraints, and heuristics without scripting brittle case-by-case control flow or relying on vague assumed context
**ELSE** use exact deterministic logic in software when the behavior truly must follow a fixed branch sequence.

## Do
- Make the desired behavior explicit enough that the model can act without guessing unstated assumptions.
- Express reusable heuristics and decision criteria instead of enumerating every anticipated branch in prose.
- Separate background, instructions, tool guidance, and output expectations when that organization makes the contract easier to inspect.
- Move hard invariants and exact state transitions into deterministic code rather than encoding them as a growing prompt program.
- Test whether a competent model can generalize the instructions to cases that were not spelled out verbatim.

## Don't
- Don't encode an expanding decision tree in natural-language instructions when ordinary code can enforce it exactly.
- Don't replace specificity with slogans such as "be helpful" or "use good judgment" when the agent needs concrete criteria.
- Don't assume the model shares organizational history, terminology, or hidden requirements that were never placed in context.
- Don't increase instruction detail merely to make the prompt look comprehensive; added text should resolve a real behavioral ambiguity.

## Checklist
- Are the goals and constraints concrete enough to guide an unfamiliar valid case?
- Is any prompt text functioning as brittle hardcoded control flow that belongs in software?
- Does the agent need hidden background knowledge to interpret an instruction correctly?
- Can the same guidance cover several cases through a heuristic instead of one clause per case?
- Have unseen cases been used to check that the instruction generalizes rather than memorizes examples?

## Notes
Agent instructions fail at both extremes. Over-specified prompts become natural-language programs whose branches are difficult to maintain and easy to contradict; under-specified prompts force the model to invent missing policy. The useful middle level tells the model what matters and how to reason about it while leaving exact deterministic machinery to software.
