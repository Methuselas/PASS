---
object_id: PAT_keep_unreal_editor_browser_models_synchronized
object_type: pattern
name: Keep Unreal Editor Browser Models Synchronized
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
- editor_tools
- slate
- delegates
- lifecycle
cross_links:
- rel: related_to
  target_object_id: PAT_cache_unreal_tool_selections_as_weak_objects
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Keep Unreal Editor Browser Models Synchronized

## Pattern Rule
**IF** a Slate editor browser projects live world objects into a list or tree model
**THEN** separate the view model from widgets, retain source objects weakly, subscribe for every mutation path that can invalidate the projection, and reconcile while preserving stable user-facing state.

## Do
- Give each row a stable identity distinct from display text. Store source `UObject` references weakly unless the browser is their explicit owner.
- Build grouping and sorting in a view-model layer. Let `STreeView` or `SListView` request roots, children and rows without making widgets the canonical data store.
- Populate from a deliberate editor world, then handle actor add/delete and any relevant property, map, undo/redo or replacement events. Treat delegate coverage as a correctness contract.
- Prefer an incremental update when the event identifies the affected object. When it does not, schedule a coalesced full reconciliation instead of knowingly leaving the model stale.
- Before a full reconciliation, capture selection and expansion by stable identity; restore only identities that still resolve afterward.
- Validate weak objects at row generation and activation. Remove or disable stale rows rather than dereferencing them.
- Request the narrowest supported refresh and batch repeated events. If a complete rebuild is necessary, do it once after the mutation burst.
- Retain every delegate handle or owner association and remove subscriptions before the widget/model dies.

## Don't
- Don't assume add/delete delegates cover undo, redo, map replacement or object reinstancing.
- Don't use actor labels or row indexes as persistent identity.
- Don't rebuild synchronously once per event in a large transaction.
- Don't leave a known stale window as the normal recovery model when a refresh or reconciliation path can be provided.

## Checklist
- Which editor events can change membership, grouping, labels or object identity?
- Can a complete reconciliation preserve valid expansion and selection?
- Are source objects weak and checked immediately before use?
- Are subscriptions removed and pending refreshes cancelled on teardown?

## Notes
The projection may group actors by class, asset, layer or another key. The invariant is that the browser remains a disposable view over editor state, not a second authority that silently diverges.
