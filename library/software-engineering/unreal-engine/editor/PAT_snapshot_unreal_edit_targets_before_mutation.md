---
object_id: PAT_snapshot_unreal_edit_targets_before_mutation
object_type: pattern
name: Snapshot Unreal Edit Targets Before Mutation
library_path:
- software-engineering
- unreal-engine
- editor
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: PAT_have_the_doer_record_the_undo
tags:
- unreal_engine
- transactions
- undo
- components
cross_links: []
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Snapshot Unreal Edit Targets Before Mutation

## Pattern Rule
**IF** an Unreal editor operation changes an object's persistent state
**THEN** validate the intended edit, open a named `FScopedTransaction`, call `Modify()` on the objects whose state must be restored before changing it, and verify both undo and redo on the actual target.

## Do
- Use a transaction description the user can recognize in Undo History; one user action should produce one undo step.
- Record the object that owns the changed data. For a material override, call the mesh component's `Modify()` before `SetMaterial()`; record the actor as well when its state participates.
- Let the transaction's scope end only after all related changes have completed.
- Check that target objects participate in transactions; a transaction wrapper cannot capture an object excluded from the transaction system.
- Treat a failure to record the actual state as a rejected edit, including when a construction-script component delegates recording to its actor; component flags alone do not prove its recording owner is eligible.
- Reject invalid targets or material slots before opening the transaction. A rejected edit must leave state and undo history unchanged.
- Exercise a component that is not the actor's root, as well as a root component, when the operation promises component editing.

## Don't
- Don't call `Modify()` after overwriting the value: that records the changed state rather than the state the user expects to recover.
- Don't assume actor recording covers every component. Root and construction-script recording paths need not cover a separate native component.
- Don't claim undo works from successful mutation alone.

## Checklist
- Did recording precede the mutation?
- Does one undo restore the exact prior override and one redo restore the intended new override?
- Does the same result hold for the actual component arrangement the tool supports?
- Does rejected input leave values and transaction history unchanged?

## Notes
This specializes `PAT_have_the_doer_record_the_undo` through Unreal's snapshot-based transaction machinery. The visible actor is not necessarily the storage owner of the edited value. A successful root-component example therefore does not establish that arbitrary component edits have been recorded.
