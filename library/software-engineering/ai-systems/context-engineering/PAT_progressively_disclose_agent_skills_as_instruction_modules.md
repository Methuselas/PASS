---
object_id: PAT_progressively_disclose_agent_skills_as_instruction_modules
object_type: pattern
name: Progressively Disclose Agent Skills as Instruction Modules
library_path:
- software-engineering
- ai-systems
- context-engineering
stage_binding: 0 design
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: PAT_retrieve_agent_context_just_in_time
tags:
- ai_agents
- context_engineering
- skills
- progressive_disclosure
- token_efficiency
cross_links:
- rel: related_to
  target_object_id: PAT_budget_agent_context_for_signal_density
- rel: related_to
  target_object_id: PAT_treat_agent_tool_descriptions_and_schemas_as_executable_prompt_surface
reference:
  source_title: Agent context engineering for production
  author: Google Cloud Next presenters with AT&T
confidence: high
references: []
variants: []
---

# Progressively Disclose Agent Skills as Instruction Modules

## Pattern Rule
**IF** an agent has a library of reusable domain instructions or task expertise that is too large to place in every initial context
**THEN** expose only compact routing metadata for each skill up front and load the full skill instructions only after the agent selects that skill
**ELSE** preload instructions that are universally required for every decision or whose delayed availability would make the first action unsafe or incorrect.

## Do
- Represent each skill initially with a compact identifier, title, and clear description of when it should be used.
- Load the skill's detailed instructions into working context only when the current task actually needs that expertise.
- Write the lightweight description so the model can distinguish neighboring skills without seeing their full bodies.
- Keep skills conceptually separate from tools: use skills to supply reusable instructions or expertise, and tools to perform executable actions or retrieve external state.
- Measure whether the progressive-disclosure boundary reduces context load without increasing wrong-skill selection or missed capabilities.

## Don't
- Don't preload every full skill merely because the agent may use one later.
- Don't make the routing metadata so vague that the model must load several skills just to discover which one applies.
- Don't hide global safety constraints, identity rules, or always-required operating instructions inside optional skills.
- Don't turn instruction modules into fake tools solely to obtain on-demand loading when no executable action is involved.

## Checklist
- What minimal metadata lets the agent decide whether a skill is relevant?
- Is the full skill body loaded only after selection?
- Can the agent distinguish this skill from adjacent skills from the lightweight description alone?
- Which instructions must remain globally visible rather than progressively disclosed?
- Has token reduction been checked against wrong-skill or missed-skill behavior?

## Notes
Skills can act as a context-management mechanism: only first-level metadata is initially visible, while the complete skill is loaded after invocation. This is progressive disclosure applied to behavioral expertise rather than to external documents. It complements just-in-time retrieval but owns a different object: reusable instruction modules that make an agent expert in a domain without paying the full context cost before that expertise is needed.
