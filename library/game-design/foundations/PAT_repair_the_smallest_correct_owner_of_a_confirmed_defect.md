---
object_id: PAT_repair_the_smallest_correct_owner_of_a_confirmed_defect
object_type: pattern
name: Repair the Smallest Correct Owner of a Confirmed Defect
library_path:
- game-design
- foundations
stage_binding: 3 rough
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- revision
- defects
- refactoring
- ownership
cross_links:
- rel: related_to
  target_object_id: PAT_classify_playtest_evidence_before_revising
- rel: related_to
  target_object_id: PAT_retest_revisions_before_treating_them_as_validated
- rel: related_to
  target_object_id: PAT_reuse_core_resolution_grammar_before_adding_new_mechanics
reference:
  source_title: Designing TTRPGs For Dummies
  author: Martin Buinicki
confidence: high
references: []
variants: []
---

# Repair the Smallest Correct Owner of a Confirmed Defect

## Pattern Rule
**IF** a defect has been confirmed strongly enough to justify revision
**THEN** change the smallest rule, dependency, or assumption that actually owns the failure, escalating to redesign or removal when the regulating architecture itself is wrong
**ELSE** do not accumulate downstream patches around an unconfirmed or mislocated cause.

## Do
- Trace the failure to the rule, dependency, interface, ordering decision, state assumption, or regulating constraint that actually permits it.
- Prefer a local repair when one dependency cleanly bypasses an otherwise sound mechanic or constraint.
- Redesign or remove the underlying mechanic when normal legal play repeatedly escapes its root regulating assumption and local fixes would merely surround the defect with exceptions.
- Compare a proposed repair with returning to a known-working prior state when the replacement has not earned its migration, complexity, or regression cost.
- Preserve unaffected behavior and interfaces when the defect is local rather than rewriting adjacent systems for conceptual neatness.
- Hand the resulting change to **Retest Revisions Before Treating Them as Validated** before treating the repair as trusted.

## Don't
- Patch several downstream symptoms when one upstream dependency is the actual failure owner.
- Preserve a structurally broken mechanic by adding exception after exception because the original mechanism is treated as untouchable.
- Redesign a whole subsystem merely because a narrow dependency can be corrected cleanly.
- Keep a replacement solely because work has already been spent on it when a known-working state is cheaper and better supported.
- Call a repair complete before its changed behavior and affected dependencies have been rerun.

## Checklist
- The defect's causal owner is named more specifically than the visible symptom.
- A local repair is used when the root architecture remains sound.
- Structural redesign or removal is justified by failure of the regulating assumption rather than by dislike of one outcome.
- The chosen change avoids unnecessary damage to unaffected behavior and interfaces.
- Reversion to a known-working state was considered when the replacement carries material migration or regression cost.
- The repair is routed into regression testing before validation.

## Notes
The smallest correct repair is not necessarily the smallest edit. It is the narrowest change that reaches the actual owner of the failure. A one-line exception can be too small when the mechanic's basic assumption has collapsed, while a subsystem rewrite can be far too large when one dependency bypasses an otherwise sound limiter. Locating ownership before editing prevents patch accretion and protects established behavior that was not implicated by the evidence.
