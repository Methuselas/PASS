---
object_id: PAT_keep_long_running_agent_runs_on_compatible_deployment_versions
object_type: pattern
name: Keep Long-Running Agent Runs on Compatible Deployment Versions
library_path:
- software-engineering
- ai-systems
- runtime-operations
stage_binding: 4 final
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: PAT_checkpoint_long_running_agent_execution_for_durable_resumption
tags:
- ai_agents
- runtime
- deployment
- versioning
- long_running
cross_links:
- rel: related_to
  target_object_id: PAT_checkpoint_long_running_agent_execution_for_durable_resumption
- rel: related_to
  target_object_id: PAT_enforce_agent_policies_in_deterministic_middleware
reference:
  source_title: How we built our multi-agent research system
  author: Jeremy Hadfield, Barry Zhang, Kenneth Lien, Florian Scholz, Jeremy Fox, and Daniel Ford
confidence: high
references: []
variants: []
---

# Keep Long-Running Agent Runs on Compatible Deployment Versions

## Pattern Rule
**IF** agent runs can remain active while prompts, tools, or execution logic are being deployed
**THEN** keep old and new runtime versions available concurrently and route in-flight work to the version compatible with the state it started under while new traffic is shifted gradually to the new version
**ELSE** ordinary atomic deployment is sufficient when no execution can outlive the deployment boundary or all saved state is explicitly migration-safe.

## Do
- Treat prompts, tool contracts, and execution code as a versioned compatibility set for long-running stateful runs.
- Preserve the version identity associated with an active run or checkpoint so resumption does not unknowingly cross into incompatible behavior.
- Introduce a new version alongside the old one and shift new traffic gradually while existing runs finish on their compatible stack.
- Retire the old version only after its in-flight runs are complete or their state has been deliberately migrated.
- Test deployment behavior with paused, checkpointed, tool-active, and long-duration runs rather than only fresh requests.

## Don't
- Don't replace prompts or tool schemas globally while old runs are still holding state that assumes the previous contracts.
- Don't resume a checkpoint under a new execution stack merely because the deploy completed successfully for new traffic.
- Don't assume stateless request deployment practices are sufficient for agents that run across minutes, hours, or longer.
- Don't keep old versions indefinitely without tracking which live runs still require them.

## Checklist
- Can an agent run or checkpoint survive across a deployment?
- Which prompt, tool, model, and execution versions must remain compatible with its saved state?
- How is an in-flight run routed back to the correct version after a pause or retry?
- When is it safe to stop serving the old version?
- Are migrations explicit when a run must cross versions?
- Have long-running and interrupted executions been tested during rollout?

## Notes
Rainbow deployments let old and new agent versions run simultaneously while traffic moves gradually between them. The underlying lesson is compatibility preservation for stateful execution. Long-running agents can be partway through a web of prompts, tools, and decisions when a deploy occurs, so rollout strategy must account for the state version they already carry.
