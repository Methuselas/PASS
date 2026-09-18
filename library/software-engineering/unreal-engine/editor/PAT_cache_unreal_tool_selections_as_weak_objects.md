---
object_id: PAT_cache_unreal_tool_selections_as_weak_objects
object_type: pattern
name: Cache Unreal Tool Selections as Weak Objects
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
- uobject
- weak_references
- editor_tools
cross_links: []
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Cache Unreal Tool Selections as Weak Objects

## Pattern Rule
**IF** a plain C++ editor helper caches a selected UObject without owning its lifetime
**THEN** store it through `TWeakObjectPtr` and resolve it at the moment of use, treating an absent or expired object as a reported unavailable selection.

## Do
- Use a weak material reference for a material-copy clipboard whose job is to remember a selection, not keep an asset alive.
- Resolve the pointer once at the start of the action and use that result for the immediate operation.
- Keep a failed copy and an expired prior selection distinguishable in feedback where it helps recovery.
- Decide whether the helper's state must be reflected or retained. A plain non-UCLASS helper cannot make its fields visible to garbage collection merely by writing a property annotation.

## Don't
- Don't assume a cached raw pointer remains usable because it was valid when copied.
- Don't silently paste a different default material when the copied selection is unavailable.
- Don't replace owning references with weak ones where keeping the object alive is the requirement.

## Checklist
- Is the helper borrowing the selected object rather than retaining it?
- Is the weak reference resolved before every use?
- Does unavailable selection stop the edit and produce a useful explanation?

## Notes
The clipboard and the material asset have different lifetimes. A weak selection lets the helper survive an asset's disappearance without making the clipboard an accidental lifetime owner. This does not prescribe weak storage for reflected owning fields or for an operation that requires explicit retention.
