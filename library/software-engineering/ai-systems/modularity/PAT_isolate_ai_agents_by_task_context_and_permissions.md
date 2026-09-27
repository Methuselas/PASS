---
object_id: PAT_isolate_ai_agents_by_task_context_and_permissions
object_type: pattern
name: Isolate AI Agents by Task, Context, and Permissions
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
- ai
- agents
- isolation
- least_privilege
- context
cross_links: []
reference:
  source_title: The Hot New AI Model Nobody's Heard Of, But We Already Use the Concept
  author: Rob Braxman Tech Deep Dive
confidence: medium
references: []
variants: []
---

# Isolate AI Agents by Task, Context, and Permissions

## Pattern Rule
**IF** one AI workflow performs tasks with different knowledge, tools, resource costs, or risk levels
**THEN** split the workflow into task-specific agents or workers and give each one only the context, permissions, tools, and workspace required for its own job
**ELSE** keep tasks together only when they genuinely share the same authority, context, and resource requirements and the split would add coordination without reducing exposure or cost.

## Do
- Give the first process that examines untrusted input the narrowest role and permissions compatible with classification.
- Scope each worker's context to its task instead of loading every knowledge source, history, and tool into every request.
- Put resource-heavy capabilities such as retrieval or external API access only on the workers that need them.
- Use separate workspaces or equivalent capability boundaries when the harness supports them, and avoid administrative access for workers that do not require it.
- Treat remembered conversation state as a capability: omit it from a worker whose job should depend only on the current item and fixed directives.

## Don't
- Don't give a general-purpose agent every tool and every knowledge source because some later branch may need them.
- Don't expose installation structure, administrative privileges, external APIs, or persistent memory to an input-screening worker without a concrete need.
- Don't assume isolation makes malicious input harmless; it limits what a compromised or misdirected worker can reach and must be combined with validation and explicit routing policy.
- Don't combine cheap, expensive, safe, and privileged branches merely to avoid dispatch logic.

## Checklist
- What exact task does each agent or worker own?
- Which context, memory, tools, files, APIs, and permissions does that task actually require?
- Can the untrusted-input stage operate without administrative or broad workspace access?
- Are expensive retrieval or external-access capabilities confined to the branches that use them?
- If one worker is misled, what resources can it reach beyond its own task boundary?

## Notes
Task specialization is not only a performance technique. It is also an authority boundary. A worker that only classifies an incoming message does not need the same context or capabilities as a worker that performs retrieval or calls external services. Keeping those capabilities separate reduces unnecessary context load and limits the blast radius of a bad decision.

A production workflow can use isolated workspaces, task-specific directives, restricted permissions, and no memory for its initial evaluation stage. The portable lesson is to align an agent's authority and context with the smallest task it owns.
