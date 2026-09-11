---
object_id: PAT_prefer_make_functions_to_direct_new
object_type: pattern
name: Prefer the make Functions to Direct Use of new
library_path:
- software-engineering
- languages
- cpp
- memory-management
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- memory_management
- smart_pointers
- exception_safety
- performance
cross_links:
- rel: related_to
  target_object_id: PAT_use_unique_ptr_for_exclusive_ownership
- rel: related_to
  target_object_id: PAT_price_shared_ownership_before_choosing_it
- rel: related_to
  target_object_id: PAT_manage_resources_with_raii_objects
- rel: related_to
  target_object_id: PAT_choose_braces_or_parentheses_deliberately
- rel: related_to
  target_object_id: AP_give_an_acquired_resource_an_owner
reference:
  source_title: 'Effective Modern C++: 42 Specific Ways to Improve Your Use of C++11 and C++14'
  author: Scott Meyers
confidence: high
references: []
variants:
- variant_id: VAR_standalone_new_statement
  variant_name: Put the new and Its Smart Pointer in a Standalone Statement
  variant_basis: constraint
  difference_from_foundation: The object is still created with a direct `new`, but the
    smart pointer that will own it is constructed in its own statement, before the call
    that consumes it, rather than exposing the raw pointer across more code.
  when_to_use: A make function cannot be used — a custom deleter is required, a braced
    initializer must be passed, or the type has class-specific allocation functions that
    a single-allocation make function would bypass. Immediate construction keeps the
    exceptional raw-ownership interval visible and minimal.
  when_not_to_use: A make function is available and none of those constraints apply. The
    standalone statement preserves explicit ownership and does nothing about the
    duplicated type name or the second allocation.
  absorbed_from_object_id: PAT_store_newed_object_in_smart_pointer_standalone
---

# Prefer the make Functions to Direct Use of new

## Pattern Rule
**IF** you are creating an object to be owned by a smart pointer
**THEN** create it with the corresponding make function rather than passing a `new` expression to the smart pointer's constructor
**ELSE** where the pointer needs a custom deleter, or the object must be initialized with a braced initializer, the make functions cannot express it and direct `new` is the answer — under the standalone-statement discipline below.

## Do
- Use `std::make_unique` and `std::make_shared` to express creation and ownership in one operation, eliminate repeated type names, and avoid exposing a raw owning pointer.
- Count the second benefit where shared ownership is involved: a make function for a shared pointer performs one allocation for the object and its control block together, where a direct `new` performs two. The result is smaller and faster code and one less trip to the allocator.
- Stop writing the type twice. `new` names the type and so does the smart pointer being constructed, and the make function names it once — which matters most when the type is long and when it later changes.
- Use the C++20 array overloads when array ownership is genuinely needed, and consider the `make_*_for_overwrite` forms only when skipped value-initialization is intentional and measured.
- Fall back to direct `new` deliberately where the make functions cannot serve, and immediately construct the final smart pointer in its own statement. That bounded exception is preserved as `VAR_standalone_new_statement`.
- Prefer passing a `new` expression directly to the smart pointer's constructor over passing a named raw pointer variable, in that fallback case. A named raw pointer invites a second smart pointer to be constructed from the same address, and two owners of one object each believe they must destroy it.

## Don't
- Don't use a make function when a custom deleter is required. There is no way to supply one, and the deleter is part of what the pointer is for.
- Don't use a make function expecting a braced initializer to be forwarded as one. The arguments are forwarded with parentheses, which is a deliberate documented choice — the make function cannot know which delimiter the caller wanted, and for some types the two select different constructors.
- Don't assume the single-allocation benefit is free of consequences for shared pointers. The object and its control block occupy one block of memory, so that memory cannot be released until the last weak reference is gone, not merely the last shared one. For a large object with long-lived weak references, two allocations may be preferable.
- Don't use a shared-pointer make function for a class with its own allocation functions. Those are written for objects of the class's size and the make function asks for a larger block containing the control block too.

## Checklist
- Does any direct `new` here have a documented reason that a make function cannot express?
- Is the type named more than once at this creation site?
- If a make function is not being used, which of the documented limitations applies?
- Where direct `new` is unavoidable, is it in its own statement, and is the result passed straight to the smart pointer rather than through a named variable?
- For shared ownership of a large object, will weak references keep its memory alive after the object is destroyed?

## Notes
`VAR_standalone_new_statement` preserves the direct-allocation fallback. Its predecessor used a standalone smart-pointer construction to prevent an allocation from being stranded by another argument's exception. Since C++17, evaluations of function arguments do not interleave in that way, so this is no longer the correctness reason for preferring make functions under the C++20 baseline. The standalone form remains useful when a custom deleter, braced initializer, or class-specific allocation function rules a make function out: it makes the exceptional raw-ownership boundary small and explicit.

Function arguments still have unspecified relative order, so code must not depend on which complete argument evaluation happens first. That is distinct from the pre-C++17 interleaving hazard: under the C++20 floor, another argument cannot run between a `new` expression and the smart-pointer constructor that contains it.

The trade on the single allocation is the one place where the recommendation genuinely reverses, and it is worth stating precisely so it is not applied superstitiously. Combining the object and its control block is the source of the performance advantage and also means the block is freed only when both counts reach zero. Weak references keep the control block alive; with a separate allocation they keep only the control block alive, and with a combined one they keep the object's storage alive too.
