---
object_id: DRILL_check_unreal_material_edit_undo_and_rejection
object_type: drill
name: Check Unreal Material Edit Undo and Rejection
library_path:
- software-engineering
- unreal-engine
- editor
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- materials
- undo
- boundary_cases
cross_links:
- rel: teaches
  target_object_id: AP_apply_a_reversible_unreal_material_edit
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
target_skill: Make an editor material edit reversible and observable
variants: []
---

# Check Unreal Material Edit Undo and Rejection

## Practice Task
Produce a disposable editor fixture that edits one material slot on both a root and a separate non-root mesh component, then demonstrate undo, redo and rejection without mutation.

## Target Skill
This exercise gives practice in `AP_apply_a_reversible_unreal_material_edit`: capture the actual edited state and expose usable outcomes.

## Setup
An Unreal editor C++ toolchain, an isolated test project, two distinguishable materials, and transactional mesh components with at least one material slot. Record a clean undo-history baseline in that disposable process.

## Instructions
1. Create the root/non-root fixture and record its original material overrides.
2. Apply the new material through the callable edit operation, then record the observed override.
3. Undo once and record the restored override; redo once and record the new override again. Repeat for the non-root target.
4. Repeat the assignment with the same material. Record the material override and undo-history count before and after the attempt.
5. Attempt a null selection, an invalid component and an out-of-range slot. Record each returned reason and check both state and undo-history count against the pre-attempt values.
6. Explain which object owns the override and why it was recorded before mutation. Keep the build result and actual runtime observations.
7. State separately whether viewport gesture routing, Blueprint-template edits and notification rendering were exercised.

## Success Check
- The editor fixture builds and runs; a described or predicted result does not qualify.
- Exact override observations demonstrate apply, undo and redo for both component arrangements.
- Unchanged assignments and all rejected attempts leave the component state and undo-history count unchanged.
- Rejections return useful reasons rather than only a false flag.
- The explanation identifies storage ownership and pre-mutation recording.
- Claims stay within the interfaces actually tested.

## Common Failures
- Recording the object after the edit.
- Using only a root component to justify all component layouts.
- Letting an invalid slot grow an override array before rejecting it.
- Returning success without checking whether any supported slot was edited.
- Calling a visible toast proof that a remote caller received the outcome.

## Notes
The fixture distinguishes a working mutation from a reversible edit. A non-root case and unchanged-history cases expose near misses that a screenshot of the final material cannot show.
