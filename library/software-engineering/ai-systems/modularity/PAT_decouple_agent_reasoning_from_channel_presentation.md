---
object_id: PAT_decouple_agent_reasoning_from_channel_presentation
object_type: pattern
name: Decouple Agent Reasoning from Channel Presentation
library_path:
- software-engineering
- ai-systems
- modularity
stage_binding: 0 design
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: none
tags:
- ai_agents
- modularity
- multichannel
- presentation
- context_continuity
cross_links:
- rel: related_to
  target_object_id: PAT_separate_thread_state_from_cross_conversation_memory
- rel: related_to
  target_object_id: PAT_isolate_ai_agents_by_task_context_and_permissions
reference:
  source_title: Agent context engineering for production
  author: Google Cloud Next presenters with AT&T
confidence: high
references: []
variants: []
---

# Decouple Agent Reasoning from Channel Presentation

## Pattern Rule
**IF** the same conversational workflow must serve multiple channels such as web, app, chat, or voice while preserving one logical relationship with the user
**THEN** keep reasoning, orchestration, and shared context in a channel-independent logic layer and adapt only the final interaction format through channel-specific presentation components
**ELSE** a channel-specific implementation is acceptable when the workflow, state, and behavior truly do not need to transfer across surfaces.

## Do
- Centralize the business conversation and orchestration logic so channel changes do not create separate versions of the same reasoning system.
- Normalize incoming channel events into a shared logical interaction model before they update long-lived context.
- Use formatter or presenter components to adapt responses to the constraints of web, app, voice, or other surfaces.
- Keep persistent user context independent of the display channel so a later interaction can continue from the same durable state.
- Let channel adapters own modality and formatting concerns without duplicating the agent's decision logic.

## Don't
- Don't maintain independent memory silos for each channel when the product promises cross-channel continuity.
- Don't copy the full reasoning stack into every surface and expect the implementations to remain behaviorally aligned.
- Don't let a formatter silently make domain decisions that should belong to the shared logic layer.
- Don't force the core agent to reason in the incidental structure of one UI when several channels must consume the same output.

## Checklist
- Is there one authoritative reasoning and context layer across channels?
- Are channel-specific constraints handled by presentation adapters rather than duplicated business logic?
- Can a user change surfaces without losing durable conversational state?
- Are incoming events normalized before they enter shared context?
- Could a new channel be added without cloning the agent's core decision logic?

## Notes
When one conversational workflow must span several channels, separating its logic from its formatter can let output adapt to the active channel while shared context persists across surfaces. Confirm that the channels genuinely share workflow state before accepting the extra abstraction; presentation can then vary by modality without duplicating the reasoning layer.
