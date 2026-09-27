---
object_id: PAT_return_only_decision_relevant_context_from_agent_tools
object_type: pattern
name: Return Only Decision-Relevant Context from Agent Tools
library_path:
- software-engineering
- ai-systems
- tool-use
stage_binding: 0 design
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: PAT_ask_for_the_least_order_the_consumer_needs
tags:
- ai_agents
- tool_use
- context_engineering
- token_efficiency
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

# Return Only Decision-Relevant Context from Agent Tools

## Pattern Rule
**IF** an agent tool can return more data than the next model decision needs
**THEN** make the default response concise and high-signal, with filtering, pagination, range selection, or an explicit detailed mode for the cases that genuinely need more
**ELSE** return the full result when the complete payload is itself necessary for the next action and fits comfortably within the agent's working context.

## Do
- Design the default response around the information the next decision consumes, not everything the backend happens to know.
- Resolve opaque identifiers into meaningful names when the agent can act correctly without the raw IDs.
- Provide detailed modes only when downstream tool calls require technical identifiers or extra metadata.
- Add filtering, pagination, ranges, or truncation controls before large results can flood the context window.
- When truncating, tell the agent what was omitted and how to request the next relevant slice.

## Don't
- Don't dump whole collections into model context when a targeted search can retrieve the needed subset.
- Don't include UUIDs, MIME details, internal URLs, or bookkeeping fields by default unless they influence the next action.
- Don't assume a larger context window makes irrelevant payload free; irrelevant tokens still compete with useful evidence and instructions.
- Don't silently truncate results in a way that makes the agent believe it saw the complete set.

## Checklist
- Which returned fields directly change the agent's next decision?
- Can irrelevant rows or fields be filtered before they become tokens?
- Is there a concise default and a deliberate path to richer output when needed?
- Are large responses paginated, bounded, or range-selectable?
- Does every truncation explain how to retrieve the missing relevant portion?

## Notes
For agent tools, response volume is part of interface correctness. A deterministic caller can cheaply ignore extra fields in memory; an LLM must process them as context. Returning less is therefore not merely a bandwidth optimization: it reduces distraction and leaves more of the finite attention budget for the evidence that actually determines the next action.
