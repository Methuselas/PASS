---
object_id: PAT_consolidate_long_term_memories_into_evolving_facts
object_type: pattern
name: Consolidate Long-Term Memories into Evolving Facts
library_path:
- software-engineering
- ai-systems
- context-engineering
stage_binding: 0 design
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: PAT_separate_thread_state_from_cross_conversation_memory
tags:
- ai_agents
- context_engineering
- memory
- consolidation
- deduplication
cross_links:
- rel: related_to
  target_object_id: PAT_process_long_term_memory_off_the_response_hot_path
- rel: related_to
  target_object_id: PAT_make_long_term_memory_inspectable_and_reversible
- rel: related_to
  target_object_id: PAT_scope_agent_state_and_authority_per_tenant
reference:
  source_title: Agent context engineering for production
  author: Google Cloud Next presenters with AT&T
confidence: high
references: []
variants: []
---

# Consolidate Long-Term Memories into Evolving Facts

## Pattern Rule
**IF** repeated interactions may restate, refine, or contradict information already stored for the same memory owner
**THEN** compare newly extracted candidate memories with existing scoped memories and merge, update, or add them so the store represents evolving facts instead of an append-only pile of near-duplicates
**ELSE** append directly when the information is genuinely independent and no existing memory represents the same concept.

## Do
- Extract candidate memories from interaction data before deciding what durable state should change.
- Compare each candidate with existing memories for the same scope or owner.
- Update or merge semantically overlapping information and create a new memory only when the information is materially distinct.
- Permit pre-extracted facts from an agent or deterministic pipeline to enter at the consolidation stage when extraction has already been done elsewhere.
- Define the categories of information worth persisting and, when useful, provide examples that show the extraction behavior you want.

## Don't
- Don't append every mention as a new memory; repeated names, preferences, and refinements can quickly pollute retrieval.
- Don't consolidate across users, tenants, projects, or other ownership scopes merely because two memories look semantically similar.
- Don't erase a meaningful refinement by reducing several distinct facts into one vague summary.
- Don't treat extraction and consolidation as the same problem; deciding what is meaningful and deciding how it relates to existing state are separate steps.

## Checklist
- Does the candidate describe a concept already represented in this owner's memory?
- Should the existing memory be updated, merged, or left intact with a new sibling fact?
- Is the comparison restricted to the correct memory scope?
- Are extraction categories and examples aligned with what future interactions actually need?
- Will the resulting store be less repetitive and easier to retrieve than the raw interaction history?

## Notes
A two-stage memory-generation process can first extract candidate information from verbose interactions, then consolidate it against what is already known for that owner. Where repeated interactions overlap, this can prevent harmless restatements from becoming permanent context noise and let preferences or other facts evolve while preserving one usable representation of the current state.
