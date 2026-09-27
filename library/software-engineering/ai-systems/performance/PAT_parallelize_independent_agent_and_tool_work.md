---
object_id: PAT_parallelize_independent_agent_and_tool_work
object_type: pattern
name: Parallelize Independent Agent and Tool Work
library_path:
- software-engineering
- ai-systems
- performance
stage_binding: 1 skeleton
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: none
tags:
- ai_agents
- multi_agent
- parallelism
- latency
- tool_use
cross_links:
- rel: related_to
  target_object_id: PAT_choose_multi_agent_architecture_for_parallelizable_high_value_work
- rel: related_to
  target_object_id: PAT_choose_explicit_concurrency_semantics_for_overlapping_agent_inputs
- rel: related_to
  target_object_id: PAT_scale_agent_effort_to_task_complexity
reference:
  source_title: How we built our multi-agent research system
  author: Jeremy Hadfield, Barry Zhang, Kenneth Lien, Florian Scholz, Jeremy Fox, and Daniel Ford
confidence: high
references: []
variants: []
---

# Parallelize Independent Agent and Tool Work

## Pattern Rule
**IF** multiple subagent tasks or tool calls are independent for the current step and their results can be joined after completion
**THEN** execute them concurrently so wall-clock latency tracks the slowest required branch rather than the sum of all independent branches
**ELSE** keep dependent work sequential when later calls need evidence or decisions produced by earlier ones.

## Do
- Parallelize at both levels when useful: several independent subagents at the coordinator and several independent tool calls inside a worker.
- Define the join point explicitly so the coordinator knows which results are required before synthesis can continue.
- Keep dependent search refinement sequential when the next query genuinely depends on evaluating the previous result.
- Bound parallel fan-out with the task's effort budget so latency improvements do not become uncontrolled cost growth.
- Record per-branch failures so one failed call can be retried or handled without replaying successful independent branches.

## Don't
- Don't serialize independent searches merely because the first prototype used a simple loop.
- Don't launch calls in parallel when they mutate shared state without safe concurrency semantics.
- Don't parallelize dependent reasoning steps whose inputs do not exist yet.
- Don't treat the number of concurrent calls as an optimization target independent of provider limits, tool quotas, and cost.

## Checklist
- Which branches can begin from the same current state without depending on one another?
- What results must be present at the join point?
- Are any calls mutating shared state or consuming a scarce shared quota?
- Is parallel fan-out bounded by a complexity or cost budget?
- Can failed branches be retried without rerunning successful ones?
- Does measured wall-clock latency improve enough to justify the coordination overhead?

## Notes
Parallelizing subagent fan-out or tool calls can reduce wall-clock latency when branches are genuinely independent, but the gain must be measured against scheduling and join overhead. The transferable unit is independence: concurrency helps when branches can proceed without waiting on each other's evidence. This differs from user-input concurrency, which governs competing runs over shared state; here the parallel work is intentionally created inside one coordinated task.
