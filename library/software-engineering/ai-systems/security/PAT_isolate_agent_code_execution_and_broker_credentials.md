---
object_id: PAT_isolate_agent_code_execution_and_broker_credentials
object_type: pattern
name: Isolate Agent Code Execution and Broker Credentials
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
- sandbox
- code_execution
- credentials
cross_links:
- rel: related_to
  target_object_id: PAT_scope_agent_state_and_authority_per_tenant
reference:
  source_title: The runtime behind production deep agents
  author: Sydney Runkle and Vivek Trivedy
confidence: high
references: []
variants: []
---

# Isolate Agent Code Execution and Broker Credentials

## Pattern Rule
**IF** an agent can execute arbitrary shell commands or code
**THEN** run that code inside an isolated sandbox with explicit resource and network boundaries, and broker authenticated requests without exposing reusable secrets inside the sandbox
**ELSE** do not expose a general execution tool when predeclared tools are sufficient for the task.

## Do
- Make sandbox availability an explicit capability boundary; if no sandbox exists, do not expose arbitrary execution at all.
- Isolate filesystem, process, resource, and network access from the host and other tenants.
- Treat sandbox contents as potentially attacker-controlled when prompts, web pages, emails, or tool outputs can contain injected instructions.
- Keep long-lived credentials outside the sandbox and inject authorization at an outbound proxy or equivalent trusted boundary.
- Use domain allowlists, transport requirements, resource limits, and lifecycle policy appropriate to the workload.
- Decide whether a sandbox should live for one run, one thread, or a broader assistant scope based on the persistence the task actually needs.

## Don't
- Don't run model-generated commands directly on the application host.
- Don't place reusable API keys or cloud credentials in sandbox environment variables when the agent can read and exfiltrate them.
- Don't assume a sandbox makes commands inside it trustworthy; it protects surrounding systems, not the sandbox's own contents.
- Don't expose a general-purpose shell just because it is convenient if narrow tools can complete the same job with less authority.
- Don't reuse one mutable sandbox across unrelated tenants without a strong isolation model.

## Checklist
- What can code inside the sandbox read, write, execute, and reach over the network?
- Can the agent obtain any reusable credential material directly?
- Are outbound authenticated requests brokered by a trusted component outside the sandbox?
- What is the sandbox lifecycle and which state intentionally persists across runs?
- Can prompt injection compromise only the sandbox, or can it escape into host or tenant resources?
- Is arbitrary code execution actually necessary for this agent role?

## Notes
A sandbox limits the blast radius of untrusted code; it does not make the code safe. Separating credential possession from credential use is therefore critical. If the sandbox can make an authorized request without ever seeing the underlying secret, compromise of the sandbox no longer automatically becomes compromise of the credential itself.
