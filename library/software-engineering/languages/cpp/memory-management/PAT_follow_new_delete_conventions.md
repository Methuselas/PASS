---
object_id: PAT_follow_new_delete_conventions
object_type: pattern
name: Follow the Conventions When Writing new and delete
library_path:
- software-engineering
- languages
- cpp
- memory-management
stage_binding: 3 rough
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- memory_management
- allocation
- conventions
cross_links:
- rel: related_to
  target_object_id: PAT_give_polymorphic_base_a_virtual_destructor
- rel: related_to
  target_object_id: PAT_match_new_and_delete_forms
- rel: related_to
  target_object_id: AP_replace_new_and_delete_for_a_named_reason
reference:
  source_title: 'Effective C++, Third Edition: 55 Specific Ways to Improve Your Programs and Designs'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Follow the Conventions When Writing new and delete

## Pattern Rule
**IF** you write your own operator new or operator delete
**THEN** prefer delegating to the matching global allocation function, preserve its failure and zero-size contract, honor requested alignment, and provide the deallocation signatures that can be selected for every supported allocation form.

## Do
- Delegate ordinary storage acquisition to `::operator new(size)` and aligned acquisition to `::operator new(size, alignment)` unless the custom allocator itself has a measured reason to replace those semantics. Delegation preserves `new_handler`, `bad_alloc`, zero-size, and alignment behavior.
- If implementing storage acquisition directly, return non-null suitably aligned storage or throw, and reproduce the replaceable allocation function's `new_handler` retry contract rather than returning null from a throwing form.
- In a class-specific operator new, forward any request whose size differs from the class size to the global operator new (this also covers the zero-byte case, since a class size is never zero), and mirror the forwarding in operator delete.

## Don't
- Don't forget that a base class operator new is inherited, so it can be asked for a derived object's larger size; check the size and hand the wrong sizes to the global version.
- Don't use deletion through a non-virtual base as a size-routing technique. Deleting a derived object through such a base pointer is undefined behavior regardless of allocator bookkeeping.
- Don't discard alignment or assume the unsized delete overload is the only deallocation function an implementation may select.

## Checklist
- Does delegation or the direct implementation preserve `new_handler`, zero-size, failure, and alignment behavior?
- Do class-specific new and delete forward wrong-sized requests to the global versions?
- Are the matching unsized, sized, aligned, and placement deallocation paths present where the supported new expressions can select them?

## Notes
The easiest conforming allocation function is a thin wrapper around the corresponding global function: it inherits the language-required failure handling, zero-size behavior, and alignment. A direct allocator assumes those obligations itself. Because a class allocation function can be found for a derived allocation, a fixed-size pool must reject or forward a size it does not own. Modern deallocation lookup may select sized and alignment-aware signatures, so the tested interface must match the actual supported new-expression forms rather than the three overloads remembered from pre-alignment-aware C++.
