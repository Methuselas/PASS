---
object_id: PAT_choose_explicit_concurrency_semantics_for_overlapping_agent_inputs
object_type: pattern
name: Choose Explicit Concurrency Semantics for Overlapping Agent Inputs
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
- concurrency
- interaction
- state_management
cross_links: []
reference:
  source_title: The runtime behind production deep agents
  author: Sydney Runkle and Vivek Trivedy
confidence: high
references: []
variants: []
---

# Choose Explicit Concurrency Semantics for Overlapping Agent Inputs

## Pattern Rule
**IF** a user or external system can submit new input while an agent run is still in progress
**THEN** define one explicit policy for how the new input interacts with the active run—queue it, reject it, interrupt and continue from preserved progress, or roll back and replace the prior work
**ELSE** simple sequential execution is sufficient when only one run can exist for the state scope at a time.

## Do
- Treat overlapping input as a state-management decision, not merely as a UI event.
- Use queueing when correctness and state safety matter more than immediate reaction to the second message.
- Use rejection when the caller must wait for a current transaction or critical section to finish before issuing another command.
- Use interruption only when partial progress can be checkpointed and any in-flight tool work has defined cleanup or idempotency behavior.
- Use rollback when the newer input semantically replaces the earlier request and prior partial progress should not survive.
- Test each policy with tool calls that are slow, partially completed, or externally side-effecting.

## Don't
- Don't let two runs mutate the same conversational state concurrently without an explicit merge or serialization rule.
- Don't interrupt an active tool call unless the runtime knows whether that call completed and how to clean up or resume safely.
- Don't assume the lowest-latency policy is the safest policy.
- Don't silently discard a user's second message because the first run was still active.
- Don't call a behavior "interrupt" if it actually restarts from scratch and loses prior state; those semantics are different.

## Checklist
- Can a second input arrive before the current run finishes?
- Should it wait, fail, modify the current run, or replace it?
- What happens to partial model output and partial tool calls under interruption?
- Can the runtime prove which state version the resumed run is based on?
- Are side effects idempotent or compensatable under the chosen policy?
- Does the user interface communicate the concurrency behavior clearly enough to avoid accidental duplicate commands?

## Notes
Long-running agents turn ordinary chat "double-texting" into a concurrency problem. Queue, reject, interrupt, and rollback are materially different consistency models. Choosing one explicitly prevents convenience-layer behavior from silently determining whether partial work is preserved, discarded, or allowed to race.
