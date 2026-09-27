---
object_id: PAT_compact_agent_context_around_durable_state
object_type: pattern
name: Compact Agent Context Around Durable State
library_path:
- software-engineering
- ai-systems
- context-engineering
stage_binding: 4 final
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: PAT_budget_agent_context_for_signal_density
tags:
- ai_agents
- context_engineering
- compaction
- long_horizon
cross_links:
- rel: related_to
  target_object_id: PAT_retrieve_agent_context_just_in_time
reference:
  source_title: Effective context engineering for AI agents
  author: Anthropic Engineering
confidence: high
references: []
variants: []
---

# Compact Agent Context Around Durable State

## Pattern Rule
**IF** a long-running agent is approaching a context limit or its history has accumulated enough noise to threaten coherence
**THEN** replace the old working history with a high-recall compact state that preserves decisions, unresolved work, dependencies, and implementation facts while discarding redundant interaction detail
**ELSE** keep the live history when it remains small and high-signal enough that compaction would add more information-loss risk than value.

## Do
- Preserve durable commitments first: architectural decisions, unresolved defects, implementation constraints, current goals, and facts future steps still depend on.
- Tune compaction on difficult real traces by maximizing recall before tightening precision; first avoid losing important state, then remove material that proves unnecessary.
- Capture the durable implication of completed tool work before deleting its raw calls and outputs.
- Make the compacted state explicit enough that a fresh context can resume without relying on hidden knowledge of the discarded conversation.
- Re-run representative long-horizon tasks after changing compaction behavior because subtle omissions may surface only many steps later.

## Don't
- Don't summarize primarily for brevity; a shorter state that drops unresolved dependencies is a failed compaction.
- Don't discard details solely because they look repetitive if later decisions may still depend on the distinction they contain.
- Don't keep every historical tool response after its durable consequence has been recorded elsewhere.
- Don't assume a larger context window removes the need for compaction; irrelevant history can still dilute useful state long before the hard token limit is reached.

## Checklist
- Can a fresh agent state identify the current goal, accepted decisions, unresolved problems, and next dependencies from the compacted context alone?
- Were important facts preserved before raw tool interactions were removed?
- Has compaction been tested on traces where a seemingly minor early detail matters later?
- Does the compact state remove redundant history without erasing active constraints or open work?
- Can the agent continue after reset without reconstructing critical state from unavailable conversation history?

## Notes
Compaction is a continuity mechanism, not ordinary summarization. Its failure mode is delayed: an omitted constraint may not matter until dozens of actions later, when the original history is gone. That makes recall the safer first optimization target. Precision can be improved afterward by pruning material shown not to affect continuation.
