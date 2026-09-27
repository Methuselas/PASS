---
object_id: PAT_checkpoint_long_running_agent_execution_for_durable_resumption
object_type: pattern
name: Checkpoint Long-Running Agent Execution for Durable Resumption
library_path:
- software-engineering
- ai-systems
- runtime-operations
stage_binding: 0 design
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: none
tags:
- ai_agents
- runtime
- durable_execution
- checkpointing
- reliability
cross_links:
- rel: related_to
  target_object_id: PAT_persist_agent_working_notes_outside_context
- rel: related_to
  target_object_id: PAT_keep_ai_orchestration_deterministic_until_ai_is_needed
reference:
  source_title: The runtime behind production deep agents
  author: Sydney Runkle and Vivek Trivedy
confidence: high
references: []
variants: []
---

# Checkpoint Long-Running Agent Execution for Durable Resumption

## Pattern Rule
**IF** an agent run can last long enough to cross worker failures, deploys, retries, background execution, or indefinite waits
**THEN** persist execution state at stable step boundaries so the runtime can release the process and later retry, replay, or resume from the latest completed checkpoint
**ELSE** use ordinary request-scoped execution when the operation is short, restartable, and has no expensive or irreversible intermediate work to preserve.

## Do
- Write durable checkpoints after stable execution steps so recovery starts from completed work rather than from the beginning of the conversation.
- Key persisted execution state to a stable run or thread identity that survives worker and process boundaries.
- Release workers when execution is waiting for external input instead of holding a process or client connection open indefinitely.
- Define retry policy explicitly: which failures are transient, how backoff works, how many attempts are allowed, and which step is safe to retry.
- Make model calls and tool side effects idempotent or checkpoint-aware enough that recovery does not silently duplicate consequential actions.
- Treat checkpoint storage as control-plane state, not merely as a transcript archive.

## Don't
- Don't require a long agent to restart from the first prompt after a worker crash or deploy when prior expensive work can be recovered safely.
- Don't keep an idle worker alive for hours or days solely because a human or external system has not responded yet.
- Don't retry arbitrary failed steps without considering whether a tool call may already have produced an external side effect.
- Don't store only conversational text when correct resumption also depends on structured graph, tool, or workflow state.

## Checklist
- What is the smallest stable boundary after which the run can resume safely?
- Is the latest durable checkpoint available to a different worker process?
- Can a paused run release compute resources and still resume from the same logical position?
- Are retryable failures distinguished from permanent or side-effect-ambiguous failures?
- Could recovery duplicate a payment, message, file mutation, or other irreversible action?
- Can a deployment or worker crash occur mid-run without erasing completed work?

## Notes
Long-running agent reliability is primarily a state-management problem. Once execution state is durable across process boundaries, the same mechanism supports crash recovery, human pauses, background work, replay, and other interaction modes that would otherwise require separate ad hoc recovery paths.
