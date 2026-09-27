---
object_id: PAT_debug_agent_tools_from_complete_execution_traces
object_type: pattern
name: Debug Agent Tools from Complete Execution Traces
library_path:
- software-engineering
- ai-systems
- tool-use
stage_binding: 3 rough
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: none
tags:
- ai_agents
- tool_use
- debugging
- observability
cross_links:
- rel: related_to
  target_object_id: PAT_evaluate_agent_tools_on_realistic_multistep_tasks
reference:
  source_title: Writing effective tools for agents — with agents
  author: Ken Aizawa with Anthropic contributors
confidence: high
references: []
variants: []
---

# Debug Agent Tools from Complete Execution Traces

## Pattern Rule
**IF** an agent succeeds inconsistently, misuses a tool, or cannot explain why a tool interaction failed
**THEN** inspect the full execution trace — tool selections, parameters, responses, retries, omissions, and final result — and diagnose the first observable divergence instead of relying on the agent's retrospective explanation
**ELSE** use ordinary deterministic debugging when no model-controlled decision lies on the failing path.

## Do
- Preserve the raw sequence of model turns, tool calls, tool responses, and errors for evaluation runs.
- Look for repeated calls, skipped calls, invalid parameters, misread response fields, and unnecessary broad queries.
- Compare successful and failed traces to identify which interface choice changes the agent's path.
- Use aggregate tool-call metrics to find recurring friction that is easy to miss in one transcript.
- Treat what the agent omits from its explanation as possible evidence; verify behavior from the trace itself.

## Don't
- Don't accept the model's stated reasoning as a complete record of what happened.
- Don't debug only the final answer when the error may have entered several tool calls earlier.
- Don't collapse tool responses out of logs if you need to know whether the agent was given enough context to recover.
- Don't assume a successful final answer proves the path was efficient or robust.

## Checklist
- Is the complete tool-call sequence available for the failing trial?
- Can you identify the first point where the path differs from a successful or intended run?
- Did the tool return enough context for the next decision?
- Are repeated or invalid calls visible in aggregate metrics as well as individual traces?
- Does the proposed fix target an observed interface failure rather than the agent's post-hoc story about it?

## Notes
Agent behavior is only partially self-describing. A model can omit an important mistake from its own explanation, and a correct final answer can hide wasteful or brittle behavior. The execution trace is therefore the debugging artifact: it exposes how the tool surface actually shaped the agent's decisions.
