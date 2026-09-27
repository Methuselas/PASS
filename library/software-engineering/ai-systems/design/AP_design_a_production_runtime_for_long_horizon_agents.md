---
object_id: AP_design_a_production_runtime_for_long_horizon_agents
object_type: ap
name: Design a Production Runtime for Long-Horizon Agents
library_path:
- software-engineering
- ai-systems
- design
stage_binding: 0 design
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: none
tags:
- ai_agents
- runtime
- production
- reliability
- architecture
cross_links:
- rel: supports
  target_object_id: PAT_checkpoint_long_running_agent_execution_for_durable_resumption
- rel: supports
  target_object_id: PAT_separate_thread_state_from_cross_conversation_memory
- rel: supports
  target_object_id: PAT_scope_agent_state_and_authority_per_tenant
- rel: supports
  target_object_id: PAT_pause_agent_execution_at_human_decision_points
- rel: supports
  target_object_id: PAT_choose_explicit_concurrency_semantics_for_overlapping_agent_inputs
- rel: supports
  target_object_id: PAT_enforce_agent_policies_in_deterministic_middleware
- rel: supports
  target_object_id: PAT_fork_checkpointed_agent_runs_for_counterfactual_debugging
- rel: supports
  target_object_id: PAT_isolate_agent_code_execution_and_broker_credentials
- rel: supports
  target_object_id: PAT_run_scheduled_agent_work_through_the_same_runtime
reference:
  source_title: The runtime behind production deep agents
  author: Sydney Runkle and Vivek Trivedy
confidence: high
references: []
variants: []
---

# Design a Production Runtime for Long-Horizon Agents

## Objective
Design the infrastructure beneath an agent harness so long-running work can survive failures, wait for humans, preserve the right state, isolate tenants and code execution, handle overlapping inputs, and remain observable across interactive and scheduled execution.

## Steps / Flow
1. **Separate harness from runtime.** Identify what belongs to model behavior—prompts, tools, skills, agent loop—and what belongs to deterministic infrastructure—execution state, queues, persistence, auth, policy enforcement, scheduling, and tracing. *Gate:* no hard runtime invariant depends solely on the model remembering an instruction.
2. **Make execution durable first.** Apply `PAT_checkpoint_long_running_agent_execution_for_durable_resumption` before layering on pauses, background work, or complex interaction modes. Define checkpoint boundaries, retry semantics, idempotency expectations, and recovery across worker/process boundaries.
3. **Define state scopes deliberately.** Use `PAT_separate_thread_state_from_cross_conversation_memory` so resumable conversation state and long-term memory have different stores, lifecycle rules, and identity scopes.
4. **Secure the tenant boundary.** Apply `PAT_scope_agent_state_and_authority_per_tenant` to threads, memories, delegated credentials, traces, and operator actions. *Gate:* a caller cannot access another tenant's resource merely by possessing or guessing its identifier.
5. **Design interaction semantics.** Add `PAT_pause_agent_execution_at_human_decision_points` for consequential or genuinely ambiguous decisions. Add `PAT_choose_explicit_concurrency_semantics_for_overlapping_agent_inputs` so second messages cannot race or silently corrupt active state.
6. **Move hard policies into runtime code.** Use `PAT_enforce_agent_policies_in_deterministic_middleware` for redaction, budgets, rate limits, retries, fallback, moderation, or other invariants that must wrap every relevant call.
7. **Instrument for diagnosis and controlled replay.** Preserve complete traces and checkpoint history. Use `PAT_fork_checkpointed_agent_runs_for_counterfactual_debugging` when you need to compare alternate downstream paths from the same upstream state, then promote durable lessons into eval coverage.
8. **Contain general code execution.** If the agent needs a shell or arbitrary code, apply `PAT_isolate_agent_code_execution_and_broker_credentials` before exposing the capability. *Gate:* compromise of the sandbox must not reveal reusable host or API credentials.
9. **Reuse the runtime for proactive work.** Apply `PAT_run_scheduled_agent_work_through_the_same_runtime` so recurring jobs inherit the same durability, auth, middleware, tracing, and recovery model instead of creating a second operational stack.
10. **Keep integration boundaries replaceable.** Prefer inspectable state, standard data formats, and interoperable interfaces where practical so the runtime can evolve without forcing a rewrite of the harness or surrendering access to the agent's accumulated memory and traces.

## Notes
A capable harness is not enough for production. The runtime is a separate system whose reliability and security properties determine whether the agent can survive long tasks, crashes, delayed humans, multiple users, concurrent messages, arbitrary code execution, and unattended schedules. Durable execution is intentionally first because most of the later capabilities depend on being able to stop and resume across process boundaries.
