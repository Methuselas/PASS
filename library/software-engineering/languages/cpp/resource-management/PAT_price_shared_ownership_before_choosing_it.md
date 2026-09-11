---
object_id: PAT_price_shared_ownership_before_choosing_it
object_type: pattern
name: Price Shared Ownership Before Choosing It
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
- resource_management
- smart_pointers
- ownership
- concurrency
cross_links:
- rel: related_to
  target_object_id: PAT_use_unique_ptr_for_exclusive_ownership
- rel: related_to
  target_object_id: PAT_pass_a_smart_pointer_only_to_transfer_ownership
- rel: related_to
  target_object_id: PAT_prefer_make_functions_to_direct_new
- rel: related_to
  target_object_id: PAT_keep_memory_alive_until_the_compare_and_swap_completes
- rel: related_to
  target_object_id: AP_give_an_acquired_resource_an_owner
reference:
  source_title: 'Effective Modern C++: 42 Specific Ways to Improve Your Use of C++11 and C++14'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Price Shared Ownership Before Choosing It

## Pattern Rule
**IF** you are considering a reference-counted smart pointer because several parties need to keep an object alive
**THEN** account for what the reference count costs in size, allocation, and synchronization before adopting it, and construct every additional owner from an existing owner rather than from a raw address
**ELSE** where an owner may legitimately outlive the object and must be able to tell, that is what a non-owning weak reference is for, and it is not the same decision.

## Do
- Know the cost categories, since they distinguish shared from exclusive ownership. A shared pointer commonly stores both an observed address and a control-block link; the control block may require a separate allocation unless a make/allocate function combines storage; and ownership changes require thread-safe reference-count maintenance. Exact size, synchronization mechanism, and allocation layout are implementation properties to measure on relevant targets.
- Treat copying the pointer as an ownership operation, not merely an address copy. It changes the shared ownership count even when no object allocation occurs, so pass by value when the callee must acquire or retain ownership and pass by reference when it only observes the handle during the call.
- Construct every subsequent owner from an existing smart pointer, never from the raw address again. A second smart pointer built from the same raw pointer creates a *second* control block, so two independent reference counts each reach zero and the object is destroyed twice.
- Avoid the named raw pointer variable entirely where you must use a direct allocation, and pass the allocation expression straight to the constructor. A raw pointer sitting in a variable is what makes the second construction look reasonable to whoever writes it.
- Use `std::enable_shared_from_this` when an object that is already shared-owned must hand out another owner of itself. `shared_from_this()` shares the existing control block; it fails with `std::bad_weak_ptr` when no qualifying owner established that association. Use `weak_from_this()` when the caller needs a non-owning result or should be able to observe an unowned state without throwing.
- Reach for a weak reference where an observer must not keep the object alive: a cache whose entries may have been evicted, a list of observers that may have been destroyed, and breaking cycles between objects that point at each other. A weak reference is not a pointer you dereference — it is asked whether the object is still there, and yields a shared pointer if so.

## Don't
- Don't adopt shared ownership for convenience. It approaches the convenience of garbage collection and it is not free, and the decision should follow from a genuine second owner rather than from not wanting to think about lifetime.
- Don't create a shared pointer from a raw pointer that another shared pointer already owns. This is the central hazard of the type, and it produces a double destruction rather than a diagnostic.
- Don't expect cycles to be collected. Two objects holding shared pointers to each other keep each other alive forever; one side has to be a weak reference, and choosing which is a design decision.
- Don't assume the object's memory is released when the object is destroyed. Weak references keep the control block alive past the object's destruction, and where the object and control block share one allocation, the object's storage stays with it.

## Checklist
- Who are the owners, and does each genuinely need to keep the object alive?
- Is every owner after the first constructed from another smart pointer?
- Does any raw pointer variable here get handed to a smart pointer constructor?
- Does the object ever need to produce a shared pointer to itself?
- Is there a cycle, and which side of it should be weak?
- Is the pointer being copied on paths that only need to read the object?

## Notes
The control block is the thing to hold in mind, because nearly every hazard here follows from it. One ownership group has one control block; it holds the ownership bookkeeping and may hold a custom deleter and allocator. Constructing a new owner independently from an already-owned raw address normally creates a second group, while copying an existing shared owner or successfully locking a weak observer joins the existing group. Two ownership groups both configured to delete the same object produce the double-destruction bug.

Where the deleter lives is a genuine design difference from exclusive ownership rather than an implementation detail. It is type-erased into the ownership state, so it is not part of the shared pointer's type — two shared pointers to the same element type with different deleters still have the same type and can share a container. The representation and indirections that support this are implementation details; measure them rather than turning a common two-word layout into a guarantee.

The weak reference is often introduced as the cycle-breaker and its more common use is the dangling-observer problem. Anything that holds a reference to an object it does not own — a cache entry, a registered observer, a handle into a table — needs to distinguish "the object is gone" from "the object is here", and a raw pointer cannot. That question is what the weak form answers, and answering it is not the same as owning.
