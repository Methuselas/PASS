---
object_id: PAT_pause_agent_execution_at_human_decision_points
object_type: pattern
name: Pause Agent Execution at Human Decision Points
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
- human_in_the_loop
- approval
- control_flow
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

# Pause Agent Execution at Human Decision Points

## Pattern Rule
**IF** an agent reaches a consequential action or a decision that legitimately depends on human judgment
**THEN** checkpoint the full execution state, surface a structured interrupt payload, release the worker, and resume from that exact decision point when the human response arrives
**ELSE** let the agent loop continue without unnecessary approval friction when the action is low-risk and fully determined by existing policy and context.

## Do
- Place approval or clarification interrupts immediately before the decision or side effect they are intended to govern.
- Surface enough structured context for the reviewer to understand the proposed action without reconstructing the whole run.
- Accept richer resume values than approve/reject when the workflow benefits from edits, missing context, or corrected parameters.
- Persist the run before pausing so a response can arrive minutes or days later without retaining a live worker.
- Let approval logic travel with the tool or action when that is the most reliable way to ensure the check cannot be bypassed by another path.
- Define what happens when multiple branches are waiting for independent human inputs.

## Don't
- Don't keep a worker or client request blocked indefinitely while waiting for a person.
- Don't ask for human approval after the consequential side effect has already happened.
- Don't turn every tool call into a human gate; reserve interruption for risk, ambiguity, or policy-defined review points.
- Don't force binary approval when the reviewer needs to edit the draft, supply missing data, or redirect the action.
- Don't rely on a prompt-level instruction such as "ask before sending" when the runtime can enforce an actual pause.

## Checklist
- What exact action or uncertainty triggers the human gate?
- Is the execution state durable before the pause occurs?
- Can the worker release resources while the run waits?
- What structured data does the reviewer need to approve, edit, reject, or clarify?
- Does the resume value re-enter the workflow at the same logical decision point?
- Can parallel pending approvals be tracked without losing or mismatching responses?

## Notes
Human-in-the-loop is most robust when it is an execution primitive rather than a conversational convention. A durable interrupt turns human latency into a normal suspended state of the workflow and allows review to happen without keeping infrastructure alive or depending on the model to remember that approval was required.
