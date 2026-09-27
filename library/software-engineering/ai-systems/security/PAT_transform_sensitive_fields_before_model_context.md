---
object_id: PAT_transform_sensitive_fields_before_model_context
object_type: pattern
name: Transform Sensitive Fields Before Model Context
library_path:
- software-engineering
- ai-systems
- security
stage_binding: 0 design
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: PAT_isolate_ai_agents_by_task_context_and_permissions
tags:
- ai_agents
- security
- privacy
- pii
- data_loss_prevention
cross_links:
- rel: related_to
  target_object_id: PAT_scope_agent_state_and_authority_per_tenant
- rel: related_to
  target_object_id: PAT_return_only_decision_relevant_context_from_agent_tools
reference:
  source_title: Agent context engineering for production
  author: Google Cloud Next presenters with AT&T
confidence: high
references: []
variants: []
---

# Transform Sensitive Fields Before Model Context

## Pattern Rule
**IF** an agent workflow contains personally identifiable, sensitive personal, or similarly protected fields that the model does not need in raw form to perform its reasoning
**THEN** apply deterministic data-protection processing before those fields enter model context and restore the protected values only at a trusted post-model boundary when the application actually needs them
**ELSE** expose only the minimum raw sensitive data that the model must see for the task to be correct.

## Do
- Identify protected fields before constructing the model request rather than asking the model to discover and hide them itself.
- Apply the product's approved data-loss-prevention, encryption, tokenization, or equivalent reversible protection mechanism at the deterministic boundary.
- Keep the mapping or restoration capability outside model context and under normal application authorization controls.
- Rehydrate protected values only in the trusted layer that needs to present or execute with them.
- Combine field protection with task-scoped tools and filtered data access so the model receives only the sensitive surface required for its role.

## Don't
- Don't rely on prompt instructions as the primary control for whether protected data may be exposed to the model.
- Don't decrypt or restore protected fields earlier than the consuming application requires.
- Don't treat transformed sensitive data as permission to ignore tenant, retention, or access-control boundaries.
- Don't send every available protected field merely because a reversible protection layer exists.

## Checklist
- Which fields are classified as protected before the model call?
- Does the model need the raw value, or only a stable placeholder or transformed representation?
- Where is the reversible mapping stored, and can the model access it?
- At what trusted boundary are values restored?
- Are tool results and memory projections filtered by the same minimum-data principle?

## Notes
A DLP boundary around the agent system can protect privacy-sensitive data before it reaches the LLM and restore it after model processing where required. The portable engineering lesson is to make sensitive-field handling a deterministic infrastructure concern outside the model's discretion, then minimize the raw data that crosses the model boundary.
