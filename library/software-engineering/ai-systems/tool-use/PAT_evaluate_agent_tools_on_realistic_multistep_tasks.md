---
object_id: PAT_evaluate_agent_tools_on_realistic_multistep_tasks
object_type: pattern
name: Evaluate Agent Tools on Realistic Multistep Tasks
library_path:
- software-engineering
- ai-systems
- tool-use
stage_binding: 3 rough
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: PAT_test_behaviors_not_functions
tags:
- ai_agents
- tool_use
- evaluation
- testing
cross_links: []
reference:
  source_title: Writing effective tools for agents — with agents
  author: Ken Aizawa with Anthropic contributors
confidence: high
references: []
variants: []
---

# Evaluate Agent Tools on Realistic Multistep Tasks

## Pattern Rule
**IF** you are evaluating whether an AI agent can use a tool or tool set correctly
**THEN** test it on realistic end-to-end tasks that require the same combinations of lookup, reasoning, and action the production agent will face, and grade verifiable outcomes rather than only isolated calls
**ELSE** use narrow unit tests for deterministic tool implementation details that do not depend on agent choice.

## Do
- Build tasks from real workflows, data shapes, and services rather than toy prompts that make the intended tool obvious.
- Include cases that require several tool calls when production work does; a tool surface that works only one call at a time has not been tested as an agent interface.
- Pair each task with an outcome that can actually be checked, while allowing multiple valid paths to reach it.
- Track runtime, tool-call count, token use, invalid calls, and tool errors alongside task success so inefficient or confusing interfaces are visible.
- Keep held-out tasks for later iterations so improvements to descriptions or schemas are measured on examples that were not used to tune them.

## Don't
- Don't conclude that a tool is agent-friendly because a hand-written single-call prompt succeeds.
- Don't force the grader to reject a correct result merely because formatting or the chosen tool path differs from one expected transcript.
- Don't specify one exact sequence of calls when several strategies can legitimately produce the correct outcome.
- Don't tune against the same small task set until the tool interface merely memorizes its evaluation shape.

## Checklist
- Do the tasks resemble production workflows rather than isolated API examples?
- Do complex tasks require multiple calls where production work does?
- Can every task be graded by a verifiable result or environment state?
- Are efficiency and misuse signals recorded in addition to success/failure?
- Is there a held-out set that was not used to optimize the current interface?

## Notes
An agent tool is not fully tested by proving that its underlying function works. The uncertain part is whether a model recognizes when to use it, chooses useful parameters, combines it with other tools, and interprets the returned context correctly. Realistic multistep evaluations exercise that interface boundary while still leaving room for more than one valid strategy.
