---
object_id: PAT_decide_what_a_container_holds
object_type: pattern
name: Decide What a Container Holds
library_path:
- software-engineering
- languages
- cpp
- containers
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- containers
- copy_control
- slicing
- resource_management
cross_links:
- rel: related_to
  target_object_id: PAT_use_unique_ptr_for_exclusive_ownership
- rel: related_to
  target_object_id: PAT_choose_a_container_on_more_than_algorithmic_complexity
- rel: related_to
  target_object_id: PAT_manage_resources_with_raii_objects
- rel: related_to
  target_object_id: AP_settle_a_containers_contract_before_filling_it
reference:
  source_title: 'Effective STL: 50 Specific Ways to Improve Your Use of the Standard Template Library'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Decide What a Container Holds

## Pattern Rule
**IF** you are choosing the element type for a container
**THEN** choose it knowing the container constructs, destroys, and may move or copy elements according to each operation's requirements, so the element's value and ownership semantics must remain correct under those operations
**ELSE** where small values have ordinary value semantics, storing them directly is usually the simplest and most local design.

## Do
- Fix the model first. A container owns its element objects; insertion may copy, move, or construct them in place, access normally yields references or iterators rather than copies, and reallocation or reordering may move or copy under the operation's requirements.
- Treat expensive relocation as part of the container choice. A type with costly or potentially throwing moves can make growth and rearrangement expensive or alter exception guarantees, while node-based storage trades relocation for allocation and indirection.
- Watch for slicing, which arrives silently. A container of base-class objects given a derived object stores the base part and discards the rest, so the stored element is a base object — its added state gone and its virtual calls resolving to the base versions.
- Where polymorphic objects need identity and dynamic lifetime, store an ownership type such as `std::unique_ptr` or, only when ownership is genuinely shared, `std::shared_ptr`. Pointer-like storage avoids slicing but introduces indirection and an explicit lifetime model.
- Make owning handles visibly owning rather than raw. A container destroys its elements, but destroying a raw pointer does not release the pointed-to object; use raw pointers only for a documented non-owning view whose source outlives the container.

## Don't
- Don't rely on a cleanup loop at the end of the scope to release raw pointers. It works only if control reaches it, and an exception thrown between filling the container and running the loop leaks everything in it — which is the case an owning element type handles and a loop cannot.
- Don't derive publicly from a standard container to turn it into an ownership abstraction. Composition lets the wrapper state and enforce its own interface; deletion through a standard-container base pointer would also be undefined because its destructor is not virtual.
- Don't give copy or move surprising destructive side effects. Algorithms and containers may invoke the operations at implementation-chosen points allowed by their contracts, so ownership transfer belongs in move and copying must preserve the source.

## Checklist
- What do construction, move, copy, and destruction cost, and which does each required container operation permit?
- Could a derived object ever be handed to this container, and what would be stored if it were?
- If the container held allocated objects, what releases them, and does it run when an exception is thrown?
- Does the element type's copy or move do anything besides copy or move?

## Notes
The requirement that copying be *conventional* is the one that catches people, because it is not about cost. The historical case is the ownership-transferring smart pointer that the standard library used to provide, whose copy operation modified the object being copied — sorting a container of them set elements to null and destroyed the objects they had pointed at, so an operation that should have reordered a container instead emptied parts of it. The committee eventually made such containers illegal, and the type has since been removed from the language.

The lesson generalizes past that one type and is why it is worth keeping after the type is gone. Any element whose copy or move has observable side effects will have those side effects triggered by container operations that appear to be doing something else, at points the standard is free to choose and implementations differ about.

The modern position on move-only element types is more permissive than the historical copy-in/copy-out model. Many container operations support move-only elements, emplacement can construct directly in storage, and access returns references. Requirements are operation-specific, so a type can be a valid element for some uses without satisfying every operation. What has not changed is that copying and moving must have their ordinary, documented meanings.
