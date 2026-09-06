---
object_id: PAT_add_resolution_factors_only_when_they_expose_actionable_causes
object_type: pattern
name: Add Resolution Factors Only When They Expose Actionable Causes
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
- resolution
- modifiers
- complexity
- decisions
cross_links:
- rel: related_to
  target_object_id: PAT_invoke_resolution_only_for_meaningful_uncertainty
- rel: related_to
  target_object_id: PAT_budget_mechanical_operating_cost_by_decision_value_and_activation_cadence
- rel: related_to
  target_object_id: PAT_match_information_precision_to_decision_precision
reference:
  source_title: Designing TTRPGs For Dummies
  author: Martin Buinicki
confidence: high
references: []
variants: []
---

# Add Resolution Factors Only When They Expose Actionable Causes

## Pattern Rule
**IF** a resolved task could be represented by several situational causes, modifiers, or sub-steps
**THEN** give a cause separate mechanical representation only when knowing or changing that cause can alter a meaningful player decision, preparation, approach, or consequential branch
**ELSE** fold it into the coarser difficulty or state already used by the resolution grammar.

## Do
- Start with the coarsest difficulty or state distinction that supports the decisions the procedure is meant to create.
- Add a modifier, factor, or sub-resolution when it represents a cause players can respond to through tools, time, position, preparation, assistance, approach, resource expenditure, or another supported choice.
- Make an actionable cause legible early enough for players to change their plan when the fiction would make that cause knowable.
- Keep distinct factors separate when they lead to materially different counterplay even if their immediate numerical penalty is similar.
- Fold non-actionable detail into the baseline difficulty when separating it would add arithmetic, lookup, or branch cost without exposing a new decision.
- Re-test stacked factors at realistic use frequency so individually reasonable detail does not become dominant operating cost when several causes commonly apply together.

## Don't
- Add modifiers merely to restate that a task is difficult.
- Decompose every fictional cause into a separate number when players cannot learn, influence, or respond differently to those causes.
- Hide an actionable factor until after commitment when the character could reasonably have accounted for it beforehand.
- Treat additional causal detail as automatically more realistic or more skillful play.
- Preserve a long modifier stack whose individual entries produce no distinct counterplay.

## Checklist
- Every explicit situational factor names a cause rather than only a difficulty label.
- A player can identify at least one supported response to each factor that is meant to be actionable.
- Factors with different counterplay remain distinguishable where that difference affects choice.
- Non-actionable causes are compressed into a coarser state instead of becoming independent handling steps.
- Common stacked-factor cases remain operationally affordable at their expected cadence.
- Players receive actionable causal information before commitment whenever the fiction makes it reasonably knowable.

## Notes
This Pattern owns the **granularity of causal representation after a resolution is already justified**. It does not decide whether a check should happen at all; `PAT_invoke_resolution_only_for_meaningful_uncertainty` owns that gate. Nor does every fictional influence deserve its own modifier. The useful question is whether separating the cause creates counterplay, planning, or a distinct consequential branch. If two causes are mechanically identical and invite the same response, combining them may preserve all meaningful play at lower operating cost. If they invite different responses, keeping them distinct can make situation analysis and preparation matter.
