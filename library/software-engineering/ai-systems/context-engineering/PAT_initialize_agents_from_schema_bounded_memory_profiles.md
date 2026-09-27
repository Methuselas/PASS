---
object_id: PAT_initialize_agents_from_schema_bounded_memory_profiles
object_type: pattern
name: Initialize Agents from Schema-Bounded Memory Profiles
library_path:
- software-engineering
- ai-systems
- context-engineering
stage_binding: 0 design
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: PAT_split_agent_context_between_preload_and_runtime_retrieval
tags:
- ai_agents
- context_engineering
- memory
- profiles
- personalization
cross_links:
- rel: related_to
  target_object_id: PAT_consolidate_long_term_memories_into_evolving_facts
- rel: related_to
  target_object_id: PAT_separate_thread_state_from_cross_conversation_memory
- rel: related_to
  target_object_id: PAT_retrieve_agent_context_just_in_time
reference:
  source_title: Agent context engineering for production
  author: Google Cloud Next presenters with AT&T
confidence: high
references: []
variants: []
---

# Initialize Agents from Schema-Bounded Memory Profiles

## Pattern Rule
**IF** a small set of durable facts is important on nearly every interaction and can be defined as stable fields ahead of time
**THEN** maintain those facts in a developer-defined profile schema and preload the relevant profile at interaction start, while leaving query-specific or unpredictable memory behind just-in-time retrieval
**ELSE** use ordinary selective memory retrieval when no fixed set of fields is broadly useful enough to justify always-on context.

## Do
- Define a fixed schema for the durable fields that should shape the agent's behavior across sessions.
- Keep profile values compact so the profile supplies current state without reproducing the verbose conversations that produced it.
- Precompute and maintain profile values outside the live interaction path so they are immediately available when a new session starts.
- Maintain multiple profile schemas when different agents or surfaces need different projections of the same underlying history.
- Use the known schema to write field-specific instructions about how the agent should apply the profile values.
- Keep rare, large, or question-dependent memories behind tools or skills so the always-on profile stays small.

## Don't
- Don't turn the profile into an unbounded biography or transcript dump.
- Don't preload fields merely because they can be extracted; each field should have a predictable use in agent logic.
- Don't force every agent to receive the same profile when their tasks require different slices of durable context.
- Don't use a fixed profile as a substitute for fresh retrieval when the needed fact is volatile or specific to the current query.

## Checklist
- Which durable fields are useful often enough to justify preload?
- Is each field concise and governed by a clear schema?
- Are expensive extraction and consolidation completed before the interaction starts?
- Do different agents need different profile projections?
- Which memory remains better suited to just-in-time lookup?

## Notes
A memory profile combines static structure with evolving values. When the selected fields are broadly useful, the fixed schema can give the developer control over what is globally important, move expensive understanding work out of the interaction path, and provide a compact initialization object whose fields can be addressed explicitly by the prompt. Treat it as the always-on side of the preload-versus-retrieval split, not as a replacement for selective memory search, and verify its latency and quality effects on the actual workload.
