---
object_id: PAT_scope_agent_state_and_authority_per_tenant
object_type: pattern
name: Scope Agent State and Authority per Tenant
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
- multi_tenancy
- authorization
- identity
cross_links:
- rel: related_to
  target_object_id: PAT_separate_thread_state_from_cross_conversation_memory
reference:
  source_title: The runtime behind production deep agents
  author: Sydney Runkle and Vivek Trivedy
confidence: high
references: []
variants: []
---

# Scope Agent State and Authority per Tenant

## Pattern Rule
**IF** an agent runtime serves more than one user, organization, or operator role
**THEN** bind threads, memories, credentials, and administrative actions to authenticated identities and enforce authorization at the resource boundary on every request
**ELSE** a simpler single-tenant deployment may omit tenant routing while still preserving least-privilege boundaries for tools and operators.

## Do
- Authenticate each request before attaching user-scoped state or tools to the run.
- Tag threads, assistants, memories, and other durable resources with ownership or tenancy metadata at creation time.
- Enforce authorization on both reads and mutations so a guessed resource identifier cannot cross tenant boundaries.
- Keep end-user authorization, third-party delegated credentials, and operator/admin permissions as separate layers even when they share the same runtime.
- Issue or broker user-scoped third-party credentials at runtime rather than sharing one global credential across tenants when user authority matters.
- Test negative cases explicitly: one tenant attempting to read another tenant's thread, memory, tool credential, trace, or configuration.

## Don't
- Don't rely on the model prompt to remember which user's data it may access.
- Don't treat authentication as authorization; knowing who the caller is does not by itself define which resources they may read or mutate.
- Don't mix end-user identity with deployment-operator privileges.
- Don't attach broad service credentials to every run when actions should occur under the requesting user's authority.
- Don't assume namespace conventions alone are sufficient isolation without enforcement at the storage or request boundary.

## Checklist
- Is every durable resource associated with an owner or tenant scope?
- Are authorization checks applied on both creation/mutation and retrieval paths?
- Can the agent obtain only the third-party authority of the current user or service role?
- Are operator permissions separated from customer permissions?
- Do tests prove that cross-tenant resource identifiers are rejected rather than merely hidden from discovery?
- Are traces and memories protected by the same tenant model as live runs?

## Notes
Multi-tenancy introduces more than login. The runtime must isolate persistent state, delegated authority, and administrative control as separate security surfaces. These boundaries should be enforced by deterministic infrastructure, because a model cannot safely be the component that decides whether it is authorized to see a resource.
