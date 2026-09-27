---
object_id: PAT_retrieve_agent_context_just_in_time
object_type: pattern
name: Retrieve Agent Context Just in Time
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
- progressive_disclosure
cross_links:
- rel: related_to
  target_object_id: PAT_return_only_decision_relevant_context_from_agent_tools
reference:
  source_title: Effective context engineering for AI agents
  author: Anthropic Engineering
confidence: high
references: []
variants: []
---

# Retrieve Agent Context Just in Time

## Pattern Rule
**IF** an agent can discover large or detailed information when a task actually needs it
**THEN** keep lightweight references in working context and let the agent retrieve targeted slices progressively instead of preloading the full data set
**ELSE** preload information whose immediate availability is required for correct or latency-sensitive decisions.

## Do
- Keep compact handles such as file paths, saved queries, resource names, or links that let the agent locate richer material later.
- Give the agent search, range, file-navigation, or targeted-read tools that can reveal only the next useful slice.
- Preserve useful metadata such as hierarchy, names, timestamps, and location because it helps the agent decide where to look before spending context on contents.
- Let each retrieval result narrow the next search so context grows by progressive disclosure rather than bulk ingestion.
- Persist durable conclusions separately when an exploration will outlive the current working context.

## Don't
- Don't load an entire corpus into model context merely because some portion might become useful.
- Don't make the agent retrieve through opaque identifiers when human-readable structure can guide navigation more efficiently.
- Don't expose only all-or-nothing reads for large resources when a targeted query or range would answer the immediate question.
- Don't assume autonomous retrieval is free; poorly guided search can burn time and context on dead ends.

## Checklist
- Can the agent locate detailed information from compact references already in context?
- Are retrieval tools able to return targeted subsets rather than whole objects?
- Does metadata help the agent choose the next resource before opening it?
- Can the agent deepen an investigation incrementally without retaining every prior result?
- Is there a persistence mechanism for conclusions that must survive beyond the current context window?

## Notes
The retrieval system can act as external working memory. Keeping only references and decision-relevant slices lets the model explore a much larger information space than it could hold at once, while progressive disclosure makes each new token earn its place by answering a question raised by the preceding context.
