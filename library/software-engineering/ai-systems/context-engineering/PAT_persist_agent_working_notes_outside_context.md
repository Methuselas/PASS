---
object_id: PAT_persist_agent_working_notes_outside_context
object_type: pattern
name: Persist Agent Working Notes Outside Context
library_path:
- software-engineering
- ai-systems
- context-engineering
stage_binding: 3 rough
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: PAT_budget_agent_context_for_signal_density
tags:
- ai_agents
- context_engineering
- memory
- long_horizon
cross_links:
- rel: related_to
  target_object_id: PAT_compact_agent_context_around_durable_state
reference:
  source_title: Effective context engineering for AI agents
  author: Anthropic Engineering
confidence: high
references: []
variants: []
---

# Persist Agent Working Notes Outside Context

## Pattern Rule
**IF** an agent task spans enough turns, tool calls, or context resets that active commitments and dependencies cannot safely remain only in conversation history
**THEN** maintain a small durable working record outside the context window and reload the relevant notes when resuming or crossing a context boundary
**ELSE** keep state in the live context when the task is short enough that an external working record would add synchronization overhead without protecting continuity.

## Do
- Record the current goal, accepted decisions, unresolved work, dependencies, and next actions in a durable note or task-state artifact.
- Update the record when a decision changes or a milestone completes so later contexts do not inherit stale plans.
- Reload the notes after a reset or before resuming long-horizon work instead of relying on conversational recall.
- Keep notes compact and operational: preserve what future work needs to act, not every sentence that produced the decision.
- Separate durable project artifacts from the agent's working-memory notes so temporary planning state does not masquerade as authoritative product data.

## Don't
- Don't rely on the model to remember commitments that have fallen out of the active context window.
- Don't turn the note file into a transcript dump; external storage does not make low-signal history free to reason about.
- Don't append forever without correcting superseded decisions or closing completed tasks.
- Don't reload the entire memory store on every turn when only a small subset is relevant to the current step.

## Checklist
- Can a fresh context recover the current goal, open work, dependencies, and next actions from the persisted record?
- Are changed decisions updated rather than contradicted by older notes?
- Does the record omit completed interaction detail that no future step needs?
- Is the agent instructed or orchestrated to reread the record after context resets and resumptions?
- Are temporary planning notes clearly separated from authoritative source files or system state?

## Notes
External notes move continuity out of the model's transient attention and into durable state. The useful record is closer to a working ledger than a diary: it carries forward decisions and unfinished obligations that future steps must honor while leaving reconstructable conversation detail behind.
