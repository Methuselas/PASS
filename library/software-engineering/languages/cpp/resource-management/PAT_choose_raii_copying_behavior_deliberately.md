---
object_id: PAT_choose_raii_copying_behavior_deliberately
object_type: pattern
name: Choose an RAII Class's Copying Behavior Deliberately
library_path:
- software-engineering
- languages
- cpp
- resource-management
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- raii
- copy_control
- resource_management
cross_links:
- rel: related_to
  target_object_id: PAT_delete_the_functions_you_want_to_forbid
- rel: related_to
  target_object_id: PAT_manage_resources_with_raii_objects
- rel: related_to
  target_object_id: AP_give_an_acquired_resource_an_owner
- rel: related_to
  target_object_id: AP_write_copy_control_for_a_resource_owning_class
reference:
  source_title: 'Effective C++, Third Edition: 55 Specific Ways to Improve Your Programs and Designs'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Choose an RAII Class's Copying Behavior Deliberately

## Pattern Rule
**IF** you write your own resource-managing (RAII) class rather than using a ready-made smart pointer
**THEN** choose explicitly whether the owner is move-only, shares ownership, or performs a deep copy, because compiler-generated memberwise copying usually mishandles the underlying resource.

## Do
- Make the class move-only when exclusive ownership can be transferred: declare copy operations `= delete` and implement or default move operations that leave the source harmless.
- Reference-count the resource when it should live until the last holder is gone: hold it in a shared pointer, supplying a custom deleter (such as an unlock function) so the count reaching zero triggers release rather than deletion.
- Deep-copy the resource when callers genuinely need independent copies.

## Don't
- Don't accept the compiler-generated copying functions for a resource-managing class unchecked; copying just the handle without copying or accounting for the resource yields double releases or leaks.
- Don't encode ownership transfer as a copy operation. In modern C++, transfer is move construction or move assignment; a copy must preserve its source.

## Checklist
- Have I chosen move-only ownership, shared ownership, or deep-copy value semantics for this RAII class?
- Does the chosen behavior match how the underlying resource must be shared or duplicated?
- If reference-counting, does the deleter release the resource rather than delete it?
- If move-only, is copying rejected and is the moved-from object safe to destroy?

## Notes
Every RAII author faces the question the `Lock`/`Mutex` example poses: what should another owner mean? The modern answers are move-only exclusive ownership, reference-counted shared ownership, and a true deep copy. Old C++ encoded transfer as `auto_ptr` copy; modern C++ gives transfer its own operation, move, so copying never surprises the source by emptying it. The ownership semantics of the resource dictate the special members of the class.
