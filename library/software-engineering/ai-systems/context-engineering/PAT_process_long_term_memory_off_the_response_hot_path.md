---
object_id: PAT_process_long_term_memory_off_the_response_hot_path
object_type: pattern
name: Process Long-Term Memory off the Response Hot Path
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
- asynchronous_processing
- latency
cross_links:
- rel: related_to
  target_object_id: PAT_compact_agent_context_around_durable_state
- rel: related_to
  target_object_id: PAT_run_scheduled_agent_work_through_the_same_runtime
reference:
  source_title: Agent context engineering for production
  author: Google Cloud Next presenters with AT&T
confidence: high
references: []
variants: []
---

# Process Long-Term Memory off the Response Hot Path

## Pattern Rule
**IF** long-term memory is primarily needed to improve later turns or future sessions rather than the response currently being generated
**THEN** durably ingest interaction events during the live exchange and perform expensive memory extraction and consolidation asynchronously outside the response path
**ELSE** process memory synchronously when the current decision cannot be correct without the newly derived memory.

## Do
- Separate event ingestion from memory interpretation so the agent can finish the user-facing turn without waiting for extraction work.
- Buffer or stream the interaction events needed for later extraction before the live context disappears.
- Trigger background processing at an intentional boundary such as a period of inactivity, an explicit flush, or another reliable session milestone.
- Let the memory worker extract and consolidate durable information while the conversational agent remains focused on the active request.
- Ensure the resulting memory is ready before the next interaction that is expected to consume it.

## Don't
- Don't run an expensive memory-generation pass after every message when the result is only useful in a future interaction.
- Don't infer that a conversation has ended too early if premature extraction would produce fragmented or contradictory memories.
- Don't offload memory work without first persisting the source events needed to reconstruct what happened.
- Don't delay a memory update whose immediate absence would make the current action unsafe or materially wrong.

## Checklist
- Is this memory needed for the current answer or for a later interaction?
- Are source events durably captured before asynchronous processing begins?
- What inactivity, flush, or lifecycle rule triggers extraction?
- Can background processing finish before the next expected read?
- What happens if the background worker fails or is delayed?

## Notes
A long-term-memory pipeline can decouple ingestion from processing because persistent memories usually prepare the system for the next interaction, not the current one. Moving extraction and consolidation out of the response path is therefore both a latency optimization and a context-engineering boundary: the live agent handles the immediate task while a separate process distills durable state for future context construction.
