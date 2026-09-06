---
object_id: PAT_automate_mechanical_maintenance_without_hiding_causality
object_type: pattern
name: Automate Mechanical Maintenance Without Hiding Causality
library_path:
- game-design
- mechanics
stage_binding: 0 design
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- mechanics
- automation
- usability
- operating-cost
- transparency
cross_links:
- rel: related_to
  target_object_id: PAT_budget_mechanical_operating_cost_by_decision_value_and_activation_cadence
- rel: related_to
  target_object_id: PAT_make_the_game_operable_without_hidden_designer_knowledge
reference:
  source_title: Designing TTRPGs For Dummies
  author: Martin Buinicki
confidence: high
references: []
variants: []
---

# Automate Mechanical Maintenance Without Hiding Causality

## Pattern Rule
**IF** software or another tool can perform arithmetic, lookup, timers, derived-value propagation, or other mechanical maintenance that is not itself intended play
**THEN** automate that servicing work while keeping the inputs, causes, and player-facing state changes inspectable enough for users to understand why the result changed
**ELSE** leave the operation visible when performing or inspecting it is itself part of the intended decision experience.

## Do
- Move repetitive arithmetic, lookup, timer servicing, and derived-state propagation out of the player's manual workload when the tool can perform them reliably.
- Preserve a readable explanation of the inputs and causes behind modifiers, state changes, capability changes, or other player-facing results.
- Let automation remove servicing work without removing the decisions players must make around the resulting state.
- Check that users can inspect enough of the calculation or dependency chain to diagnose an unexpected result without reproducing every internal computation manually.
- Evaluate automation by the human work it actually removes, not by whether the underlying rules remain mathematically complex.

## Don't
- Preserve manual bookkeeping merely because a tabletop implementation once required people to perform it.
- Hide automated modifier or state changes so completely that players cannot understand why an outcome, capability, or available choice changed.
- Count automated arithmetic as player-facing decision complexity when the player no longer performs it.
- Treat automation as proof that a mechanic is well designed when the remaining player-facing decisions or feedback are still poor.

## Checklist
- At least one repeated servicing operation is removed from manual play when automation is available and appropriate.
- Player-facing results expose the inputs or causes needed to understand why they changed.
- Users can diagnose an unexpected modifier or derived-state change without reconstructing the entire computation by hand.
- Automation does not erase a decision, scarcity, uncertainty, or other friction that the game intentionally asks players to manage.
- The measured operating burden reflects what humans still do after automation rather than the complexity of hidden computation alone.

## Notes
Automation changes the cost of complexity but not the need for legible causality. A tool can cheaply execute work that would be tedious at the table, yet players still need to understand state changes they must choose around. The useful split is between **servicing work**, which may disappear into the implementation, and **decision-relevant causes and consequences**, which remain visible enough to support informed play.
