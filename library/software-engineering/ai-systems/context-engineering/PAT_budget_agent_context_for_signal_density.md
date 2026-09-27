---
object_id: PAT_budget_agent_context_for_signal_density
object_type: pattern
name: Budget Agent Context for Signal Density
library_path:
- software-engineering
- ai-systems
- context-engineering
stage_binding: 0 design
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: none
tags:
- ai_agents
- context_engineering
- attention_budget
- token_efficiency
cross_links:
- rel: related_to
  target_object_id: PAT_return_only_decision_relevant_context_from_agent_tools
reference:
  source_title: Effective context engineering for AI agents
  author: Anthropic Engineering
confidence: high
references: []
variants: []
---

# Budget Agent Context for Signal Density

## Pattern Rule
**IF** an agent can be given more instructions, history, retrieved data, examples, or tool output than it needs for the next decision
**THEN** treat the context window as a finite attention budget and keep the smallest high-signal set that is sufficient for the desired behavior
**ELSE** include the additional material when removing it would hide evidence, constraints, or state the agent actually needs.

## Do
- Judge context by its effect on the current decision, not by whether the information is generally relevant to the project.
- Reserve room for the evidence and state that will arrive during the run instead of filling the window at startup.
- Prefer concise, explicit instructions and targeted context over duplicated explanations that compete for attention.
- Re-check context composition as multi-turn agents accumulate tool results, history, and retrieved data; useful context can become stale or redundant later.
- Measure behavior after adding context, because a larger window raises capacity but does not guarantee that the model will use every token equally well.

## Don't
- Don't treat the advertised context-window size as a target to fill.
- Don't preload information merely because it might become useful eventually when it can be retrieved at the point of need.
- Don't assume irrelevant tokens are harmless because the model technically fits them; they still compete with instructions and evidence for attention.
- Don't solve a context-quality problem only by switching to a model with a larger window.

## Checklist
- Which tokens materially affect the agent's next decisions?
- What information is duplicated, stale, or retrievable on demand?
- Is enough context budget left for runtime evidence and tool results?
- Does removing low-signal material preserve or improve task performance?
- Is every large context addition justified by a failure or requirement it actually addresses?

## Notes
Longer context expands what a model can receive, not what it can attend to with uniform precision. Multi-turn agents continuously accumulate possible context, so the engineering problem is selection: keep information whose marginal value exceeds the distraction and attention cost it introduces. This makes context composition an operating constraint of the system rather than a one-time prompt-writing exercise.
