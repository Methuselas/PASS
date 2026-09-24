---
object_id: PAT_encode_unreal_property_intent_in_reflection_metadata
object_type: pattern
name: Encode Unreal Property Intent in Reflection Metadata
library_path:
- software-engineering
- unreal-engine
- editor
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- reflection
- metadata
- usability
cross_links: []
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Encode Unreal Property Intent in Reflection Metadata

## Pattern Rule
**IF** an Unreal property or function is exposed to designers or Blueprints
**THEN** encode units, valid bounds, useful interaction ranges, dependencies and compact identity in reflection metadata before building custom UI.

## Do
- Choose names and categories that state the domain meaning, then add `Units` when user unit conversion is welcome or `ForceUnits` when display must remain fixed.
- Distinguish validity from convenience: use `ClampMin`/`ClampMax` for values the object cannot accept and `UIMin`/`UIMax` for the normal slider range. Use `Delta` only as an interaction hint.
- Use `EditCondition` for real dependencies and `InlineEditConditionToggle` when the controlling Boolean is meaningful beside its dependents. Hide a row only when absence is clearer than disabled context.
- Give repeated struct elements a compact identity with enum-indexed static arrays or `TitleProperty` when that property remains meaningful and sufficiently unique.
- Treat metadata as part of the editor-facing contract. Exercise typed entry, dragging, copy/paste, reset-to-default, multi-object editing and the disabled/hidden states.
- Keep runtime validation for inputs that may arrive outside the details panel; editor metadata does not replace invariants at serialization, Blueprint or API boundaries.

## Don't
- Don't use a UI range as though it were a hard validity guarantee.
- Don't omit a unit because the current author remembers the convention.
- Don't hide dependent data when users need to understand why it is unavailable.
- Don't build a custom Slate control until metadata and standard property widgets have been exhausted.

## Checklist
- Are physical units and percentage/multiplier conventions explicit?
- Are hard bounds separated from the comfortable editing range?
- Can users see and understand every dependency state?
- Do repeated elements expose enough identity without expansion?

## Notes
Reflection metadata is the lowest-cost durable documentation because it appears at the point of editing. It improves clarity without creating a second value owner or a custom-widget lifecycle.
