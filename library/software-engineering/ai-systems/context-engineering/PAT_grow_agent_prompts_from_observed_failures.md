---
object_id: PAT_grow_agent_prompts_from_observed_failures
object_type: pattern
name: Grow Agent Prompts from Observed Failures
library_path:
- software-engineering
- ai-systems
- context-engineering
stage_binding: 3 rough
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: none
tags:
- ai_agents
- context_engineering
- prompts
- evaluation
- few_shot
cross_links:
- rel: related_to
  target_object_id: PAT_evaluate_agent_tools_on_realistic_multistep_tasks
reference:
  source_title: Effective context engineering for AI agents
  author: Anthropic Engineering
confidence: high
references: []
variants: []
---

# Grow Agent Prompts from Observed Failures

## Pattern Rule
**IF** an agent prompt is being expanded before its failure modes are known
**THEN** start with the minimum instructions needed to define the task, test with a capable model, and add instructions or examples only to repair observed behavior
**ELSE** preserve already-required constraints whose necessity is known from production, safety, or an established contract.

## Do
- Establish a minimal behavioral baseline before adding layers of prompt policy.
- Turn a repeated failure into a clear instruction only when the instruction addresses the mechanism behind the failure.
- Use a small set of diverse, canonical examples that demonstrate the intended behavior across meaningful boundaries.
- Re-run representative and held-out cases after additions so a local prompt repair does not create a broader regression.
- Remove clauses and examples that no longer change behavior or that duplicate stronger guidance elsewhere.

## Don't
- Don't preload a laundry list of speculative edge cases before knowing whether the model mishandles them.
- Don't turn every single bad example into a permanent special-case instruction.
- Don't mistake prompt length for coverage; many narrow examples can crowd out the general rule they were meant to teach.
- Don't keep legacy prompt text solely because it once addressed a problem that the current model, tools, or system no longer has.

## Checklist
- Can each added instruction or example be traced to a real requirement or observed failure?
- Do the examples span distinct canonical behaviors rather than many minor variations of one case?
- Did the change improve the target failure on repeat tests and preserve held-out behavior?
- Are obsolete or redundant prompt clauses periodically removed?
- Would the prompt still make sense if the exact examples used during tuning were replaced with new cases?

## Notes
Prompt growth easily becomes an append-only history of incidents. Starting small creates a measurable baseline, while failure-driven additions make every extra token earn its place. Canonical examples are valuable because they teach a behavior boundary; an exhaustive edge-case catalog spends context on memorizing cases and makes future maintenance harder.
