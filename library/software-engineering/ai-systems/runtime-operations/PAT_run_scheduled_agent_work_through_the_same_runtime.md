---
object_id: PAT_run_scheduled_agent_work_through_the_same_runtime
object_type: pattern
name: Run Scheduled Agent Work Through the Same Runtime
library_path:
- software-engineering
- ai-systems
- runtime-operations
stage_binding: 0 design
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: PAT_checkpoint_long_running_agent_execution_for_durable_resumption
tags:
- ai_agents
- runtime
- scheduling
- cron
- operations
cross_links:
- rel: related_to
  target_object_id: PAT_keep_ai_orchestration_deterministic_until_ai_is_needed
reference:
  source_title: The runtime behind production deep agents
  author: Sydney Runkle and Vivek Trivedy
confidence: high
references: []
variants: []
---

# Run Scheduled Agent Work Through the Same Runtime

## Pattern Rule
**IF** an agent must perform periodic or proactive work without a user waiting on each invocation
**THEN** schedule deterministic triggers into the same production runtime used for interactive runs so scheduled work inherits the same durability, authentication, middleware, tracing, and recovery guarantees
**ELSE** keep the agent reactive when no periodic work is required.

## Do
- Let deterministic scheduling trigger the agent; do not keep an AI process awake to poll the clock.
- Choose stateful scheduling when each run should see the prior run's thread history, and stateless scheduling when each invocation should start cleanly.
- Apply the same authentication, authorization, guardrails, retry policy, and tracing to scheduled runs as to user-triggered runs.
- Decide whether completed scheduled-run threads should be retained or cleaned up based on debugging and audit needs.
- Make scheduled jobs discoverable and removable so abandoned schedules do not continue consuming resources indefinitely.
- Instrument silent-hours failures because no waiting user will be present to report that the run failed.

## Don't
- Don't build a second unobserved execution path for cron work that bypasses the production agent runtime.
- Don't use the model itself as the scheduler or polling loop.
- Don't preserve one ever-growing thread by default when runs are independent batch jobs.
- Don't create recurring jobs without ownership, cleanup, and cost controls.
- Don't assume a scheduled task can fail silently because it will run again later; repeated failure can compound unnoticed.

## Checklist
- Does each invocation need history from earlier scheduled runs?
- Are retries and checkpoint recovery available when a scheduled run fails transiently?
- Do the same policy and authorization hooks wrap scheduled and interactive runs?
- Can operators find, disable, and delete each schedule?
- Is scheduled work traced and alertable even when no user is present?
- Are retention and cleanup rules explicit for state created by recurring jobs?

## Notes
Scheduling belongs in deterministic infrastructure, while the scheduled payload may be agentic. Reusing the same runtime avoids a common split-brain architecture where interactive work is durable and observable but overnight automation has separate retries, permissions, logs, and failure behavior.
