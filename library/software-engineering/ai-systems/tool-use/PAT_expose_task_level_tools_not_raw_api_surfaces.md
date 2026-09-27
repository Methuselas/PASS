---
object_id: PAT_expose_task_level_tools_not_raw_api_surfaces
object_type: pattern
name: Expose Task-Level Tools Instead of Raw API Surfaces
library_path:
- software-engineering
- ai-systems
- tool-use
stage_binding: 0 design
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: PAT_expose_clean_api_hide_implementation
tags:
- ai_agents
- tool_use
- api_design
- context_efficiency
cross_links: []
reference:
  source_title: Writing effective tools for agents — with agents
  author: Ken Aizawa with Anthropic contributors
confidence: high
references: []
variants: []
---

# Expose Task-Level Tools Instead of Raw API Surfaces

## Pattern Rule
**IF** an AI agent must act through an existing API, database, service, or application
**THEN** expose a small set of tools around the semantic tasks the agent actually needs to accomplish, hiding low-level call chains and irrelevant data behind deterministic implementations
**ELSE** expose the lower-level primitive directly when the agent genuinely needs its independent flexibility and evaluation shows it can use that primitive reliably.

## Do
- Start from production tasks and ask what action a competent human would name, not which backend endpoints happen to exist.
- Combine deterministic lookup, filtering, joining, and bookkeeping behind one tool when those steps are normally chained to accomplish a single task.
- Give every tool a distinct purpose so the agent can infer which action belongs to which tool.
- Prefer search and targeted retrieval tools over list-everything interfaces when the agent only needs a small subset of the underlying data.
- Re-evaluate the tool surface when traces show repeated call chains that could be safely collapsed into one semantic operation.

## Don't
- Don't wrap every backend endpoint merely because it is available.
- Don't force the model to spend context and reasoning reconstructing deterministic workflows your software can perform exactly.
- Don't create several tools whose purposes overlap so heavily that choosing among them becomes another inference problem.
- Don't consolidate unrelated capabilities into one vague catch-all tool just to reduce the tool count.

## Checklist
- Does each exposed tool correspond to a recognizable user or agent task?
- Are deterministic intermediate steps hidden when the agent gains no useful choice from seeing them?
- Can the agent select among tools from their distinct purposes without reconstructing backend architecture?
- Does each tool return only the data needed for the task it represents?
- Have repeated multi-call sequences in traces been reviewed as candidates for safe consolidation?

## Notes
An API designed for deterministic callers often exposes implementation-shaped primitives because ordinary code can cheaply compose them. Agents pay a different cost: every extra option, intermediate response, and deterministic substep consumes context and introduces another opportunity for an incorrect choice. The right agent tool surface therefore follows task affordances rather than endpoint parity.
