---
object_id: PAT_make_agent_tool_errors_actionable_for_the_next_call
object_type: pattern
name: Make Agent Tool Errors Actionable for the Next Call
library_path:
- software-engineering
- ai-systems
- tool-use
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: PAT_return_result_type_to_convey_error_cause
tags:
- ai_agents
- tool_use
- error_handling
- recovery
cross_links: []
reference:
  source_title: Writing effective tools for agents — with agents
  author: Ken Aizawa with Anthropic contributors
confidence: high
references: []
variants: []
---

# Make Agent Tool Errors Actionable for the Next Call

## Pattern Rule
**IF** a tool rejects an agent call for invalid input, an exceeded limit, or another recoverable mistake
**THEN** return a structured error that names the failed constraint and tells the agent how to form a valid retry
**ELSE** surface the non-recoverable failure clearly without inventing a retry path that cannot succeed.

## Do
- State which parameter or constraint failed and what value shape, range, or format is accepted.
- Include a short valid example when the interface is easy to misread.
- Distinguish recoverable input mistakes from backend failures the agent cannot fix by changing arguments.
- If a query is too broad or a result was truncated, point toward the filter, range, or pagination mechanism that can narrow it.
- Keep the error concise enough that the repair instruction is easy to find in the next model turn.

## Don't
- Don't return only an opaque status code when the agent can correct the call itself.
- Don't dump a stack trace as the primary recovery interface for a model caller.
- Don't say merely `invalid input` when several parameters or formats are possible.
- Don't suggest retries for deterministic validation failures unless the response also explains what must change.

## Checklist
- Can the agent tell exactly what failed without inferring it from implementation details?
- Does the response say what a valid next call looks like?
- Are recoverable and non-recoverable failures distinguishable?
- Does a broad-result failure point toward a narrowing mechanism?
- Could the agent retry correctly from the error message alone?

## Notes
A recoverable error is another turn in the tool protocol. Human developers may inspect documentation or source after a bad call; an agent usually has only the returned context in front of it. Error text therefore acts as executable steering: the best response converts the failed call into the information needed to make the next one valid.
