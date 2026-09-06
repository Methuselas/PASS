---
object_id: PAT_retest_revisions_before_treating_them_as_validated
object_type: pattern
name: Retest Revisions Before Treating Them as Validated
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
- playtesting
- revision
- regression
- validation
cross_links:
- rel: related_to
  target_object_id: PAT_classify_playtest_evidence_before_revising
- rel: related_to
  target_object_id: PAT_repair_the_smallest_correct_owner_of_a_confirmed_defect
- rel: related_to
  target_object_id: PAT_build_complete_resolution_procedures_incrementally
reference:
  source_title: Designing TTRPGs For Dummies
  author: Martin Buinicki
confidence: high
references: []
variants: []
---

# Retest Revisions Before Treating Them as Validated

## Pattern Rule
**IF** a mechanic, rule, procedure, component, or prior state has been revised, retained from a mixed change, or reverted as a repair
**THEN** rerun the changed behavior and the nearby dependencies that could inherit the change before treating the result as validated
**ELSE** keep the change unvalidated even when the reasoning behind it appears sound.

## Do
- Preserve a known test case or failing case that can be rerun against the changed version.
- Execute the revised behavior rather than validating it only through textual inspection or design reasoning.
- Recheck nearby dependencies, shared resources, sequencing, state transitions, and downstream procedures that could inherit the change.
- When a mixed-result bundle is decomposed, retest retained components independently when their claimed value matters.
- Treat a partial reversion as a new tested state rather than assuming return toward an older version automatically restores all previous behavior.
- Preserve enough version and test history to distinguish a newly introduced regression from an older defect and to recover a known-working state when necessary.

## Don't
- Treat the first fix as correct because the original defect was real.
- Accept a cleaner written procedure as proof that execution, pacing, compatibility, or state propagation still works.
- Regression-test only the line or mechanic that changed when neighboring behavior shares its inputs, outputs, timing, or state.
- Assume reverting one part of a failed bundle reproduces the exact behavior of a previously validated build without rerunning the affected path.

## Checklist
- The changed behavior has been executed or concretely simulated after revision.
- At least the dependencies capable of inheriting the change have been rerun.
- The original defect or target behavior is checked again under the revised state.
- Retained components from a rejected bundle have independent evidence when they remain in the design.
- Version and test records are sufficient to identify what was tested and what prior state can be restored.
- The revision remains explicitly unvalidated until the rerun and regression checks pass.

## Notes
A correct diagnosis does not guarantee a correct repair. Revisions can solve the visible symptom while breaking timing, compatibility, shared state, adjacent procedures, or a behavior the previous version handled correctly. The validation boundary therefore sits after execution, not after editing. This applies equally to new fixes, retained pieces of mixed experiments, and reversions: each creates a concrete game state that must earn trust through the affected behavior and its dependency surface.
