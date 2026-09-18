---
object_id: PAT_enforce_an_explicit_unreal_selection_policy
object_type: pattern
name: Enforce an Explicit Unreal Selection Policy
library_path:
- software-engineering
- unreal-engine
- editor
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: PAT_beware_assumptions_avoid_or_enforce
tags:
- unreal_engine
- editor_tools
- reimport
cross_links: []
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Enforce an Explicit Unreal Selection Policy

## Pattern Rule
**IF** an Unreal editor operation derives its target from selected actors or their components
**THEN** choose and enforce its cardinality and component-selection policy before extracting the asset or mutating anything.

## Do
- Snapshot selected actors into a fresh array through the editor selection API.
- If the operation requires exactly one actor, require a count of one and a valid actor; return a useful error for zero or multiple selections.
- Name a deliberate last-selected or all-selected policy explicitly when that is the desired operation.
- Specify whether the operation uses one named component, the first matching component, or all matching components.
- Validate the component and its referenced asset before passing the asset to another subsystem.
- When processing many components, deduplicate shared asset references and identify the actual assets affected.

## Don't
- Don't silently return the last selected actor while telling users the operation requires one selection.
- Don't assume finding a mesh component means it contains a valid mesh asset.
- Don't append a new selection snapshot to a stale output array.

## Checklist
- Do zero, one and multiple selections produce the declared outcomes?
- Is component selection explicit and is a missing asset rejected?
- Do reported targets identify the actual assets rather than only their actor instances?

## Notes
This specializes `PAT_beware_assumptions_avoid_or_enforce`. Actor selection, component selection and asset identity are separate decisions. A component references an asset that other actors may also use; reimporting that asset is not an edit confined to the selected instance.
