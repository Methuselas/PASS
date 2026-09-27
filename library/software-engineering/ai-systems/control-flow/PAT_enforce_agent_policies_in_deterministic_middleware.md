---
object_id: PAT_enforce_agent_policies_in_deterministic_middleware
object_type: pattern
name: Enforce Agent Policies in Deterministic Middleware
library_path:
- software-engineering
- ai-systems
- control-flow
stage_binding: 0 design
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: PAT_keep_ai_orchestration_deterministic_until_ai_is_needed
tags:
- ai_agents
- control_flow
- middleware
- guardrails
- policy
cross_links:
- rel: related_to
  target_object_id: PAT_isolate_ai_agents_by_task_context_and_permissions
reference:
  source_title: The runtime behind production deep agents
  author: Sydney Runkle and Vivek Trivedy
confidence: high
references: []
variants: []
---

# Enforce Agent Policies in Deterministic Middleware

## Pattern Rule
**IF** a safety, privacy, cost, retry, logging, or authorization rule must hold on every relevant model or tool interaction
**THEN** enforce it in deterministic runtime middleware at the call boundary rather than relying on the model to remember the rule from its prompt
**ELSE** keep genuinely advisory behavior in the prompt when occasional deviation does not violate a hard system invariant.

## Do
- Put mandatory transformations and checks at stable hooks before or after model and tool calls.
- Redact data before it reaches model input or tracing when policy requires that the model or logs never see the original value.
- Enforce hard call counts, budgets, rate limits, retry rules, or fallback behavior in code.
- Make middleware apply consistently across normal runs, retries, background execution, streaming, and pause/resume paths.
- Keep policy failures explicit and observable so the agent and operators can distinguish a blocked action from an ordinary tool error.
- Test bypass paths such as alternate tools, resumed runs, retries, and background jobs.

## Don't
- Don't encode a hard invariant only as "please never" text in the system prompt.
- Don't redact after sensitive data has already been sent to the model or written into traces.
- Don't let retries or resumptions skip middleware that would have wrapped the original call.
- Don't make cost ceilings depend on the model deciding that it has called a paid tool enough times.
- Don't hide policy enforcement so thoroughly that operators cannot tell why a call was blocked or transformed.

## Checklist
- Which policies are mandatory rather than advisory?
- At which exact model or tool boundary can each invariant be enforced deterministically?
- Does the same middleware run on retries, resumptions, background jobs, and streamed interactions?
- Is sensitive information removed before every sink that must not receive it?
- Are limits measured by runtime state rather than model self-report?
- Can tests prove there is no alternate execution path that bypasses the policy hook?

## Notes
Prompts influence model behavior; middleware enforces runtime behavior. The distinction matters most for rules that must remain true even when the model is confused, adversarially influenced, retried, or resumed through a different interaction path. Hard guarantees belong at deterministic boundaries.
