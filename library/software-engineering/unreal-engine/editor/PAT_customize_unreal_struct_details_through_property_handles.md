---
object_id: PAT_customize_unreal_struct_details_through_property_handles
object_type: pattern
name: Customize Unreal Struct Details Through Property Handles
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
- property_editor
- slate
- reflection
cross_links:
- rel: related_to
  target_object_id: PAT_encode_unreal_property_intent_in_reflection_metadata
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Customize Unreal Struct Details Through Property Handles

## Pattern Rule
**IF** standard Unreal property metadata cannot make a stable struct readable or efficiently editable
**THEN** register an editor-only `IPropertyTypeCustomization` that composes property-handle widgets, derives summaries defensively and refreshes only from owned reflected dependencies.

## Do
- Prefer a customization for stable, frequently repeated structs where compact array headers or in-place access materially reduce search and expansion work.
- Resolve native members with checked member names and validate every returned handle. Read and write through `IPropertyHandle` where possible so multi-object editing, transactions and reset behavior remain intact.
- Reuse `CreatePropertyValueWidget()` for editable values instead of duplicating Unreal's property semantics in a second control.
- Derive header summaries from current handles, cover empty/multiple-values/unavailable states and avoid dereferencing raw value storage unless the type and lifetime are proven.
- Subscribe only to child properties that affect the summary when practical. Retain weak utilities/delegates, coalesce refreshes and prevent refresh loops.
- Register each customization with `PropertyEditor` during the editor module's supported startup point and unregister the exact type layout during shutdown, guarded by module availability.
- Treat Blueprint-defined struct layouts and generated field identifiers as versioned external schemas. Fail closed when a member cannot be resolved and prefer supported extension APIs over an engine fork.

## Don't
- Don't reinterpret raw property storage after a schema change merely because the code still compiles.
- Don't force-refresh the entire details panel for unrelated child changes when a narrower dependency set is known.
- Don't hard-code generated Blueprint field identifiers without a detection and maintenance strategy.
- Don't patch PropertyEditor internals just to generalize a customization unless the engine fork and compatibility burden are explicitly owned.

## Checklist
- Does the customization preserve standard editing, undo, multi-select and reset behavior?
- Are missing, empty and multiple-value states safe and legible?
- Do registration and unregistration use the same stable type identity?
- Is every dependency on Blueprint schema or engine internals explicit and tested against supported versions?

## Notes
The customization is a projection over reflected data, not a replacement data model. A concise summary can aggregate child values, but the property system must remain the authority for edits and transactions.
