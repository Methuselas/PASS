---
object_id: PAT_separate_thread_state_from_cross_conversation_memory
object_type: pattern
name: Separate Thread State from Cross-Conversation Memory
library_path:
- software-engineering
- ai-systems
- context-engineering
stage_binding: 0 design
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: PAT_persist_agent_working_notes_outside_context
tags:
- ai_agents
- context_engineering
- memory
- persistence
- tenancy
cross_links:
- rel: related_to
  target_object_id: PAT_retrieve_agent_context_just_in_time
- rel: related_to
  target_object_id: PAT_checkpoint_long_running_agent_execution_for_durable_resumption
reference:
  source_title: The runtime behind production deep agents
  author: Sydney Runkle and Vivek Trivedy
confidence: high
references: []
variants: []
---

# Separate Thread State from Cross-Conversation Memory

## Pattern Rule
**IF** an agent needs both continuity inside one conversation and durable knowledge that should survive across separate conversations
**THEN** store conversation-scoped execution history separately from cross-conversation memory, and scope each store to the identity boundary that is allowed to retrieve it
**ELSE** keep one simpler state mechanism when the application truly has only one conversation scope and no durable user-, assistant-, project-, or organization-level memory.

## Do
- Keep short-term conversational state with the thread or run that produced it, including messages, intermediate execution state, and resumable checkpoints.
- Store long-term facts outside any one thread so later conversations can retrieve them without reopening the original execution history.
- Namespace durable memory by the owning identity boundary, such as user, assistant, project, or organization.
- Retrieve only the long-term memories relevant to the current decision instead of injecting the entire accumulated store into every conversation.
- Keep durable memory in a format that can be queried, inspected, migrated, and corrected independently of the model provider.
- Define retention and deletion behavior separately for thread state and cross-conversation memory because their lifecycles are different.

## Don't
- Don't use a thread checkpoint as the only store for information that must be available in unrelated future conversations.
- Don't promote every transient tool result or scratch note into long-term memory merely because durable storage exists.
- Don't let one tenant's memory namespace bleed into another tenant's retrieval path.
- Don't force a new conversation to replay an old thread just to recover a stable preference or project convention.

## Checklist
- Which state belongs only to the current conversation?
- Which facts must remain available across conversations?
- What identity or project boundary owns each long-term memory?
- Can durable memory be queried and corrected without replaying the original conversation?
- Is retrieval selective enough to avoid turning the memory store into permanent context bloat?
- Are thread-retention and long-term-memory retention policies intentionally distinct?

## Notes
Conversation continuity and long-term memory solve different problems. Checkpointed thread state lets an execution continue; a cross-thread store lets future executions begin with durable knowledge. Treating them as separate scopes reduces leakage, makes lifecycle rules clearer, and prevents a single ever-growing conversation history from becoming the memory system.
