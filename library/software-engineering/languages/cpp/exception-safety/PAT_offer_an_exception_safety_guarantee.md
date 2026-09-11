---
object_id: PAT_offer_an_exception_safety_guarantee
object_type: pattern
name: Offer a Definite Exception-Safety Guarantee
library_path:
- software-engineering
- languages
- cpp
- exception-safety
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- exception_safety
- resource_management
- invariants
cross_links:
- rel: related_to
  target_object_id: PAT_manage_resources_with_raii_objects
- rel: related_to
  target_object_id: PAT_use_copy_and_swap_for_strong_guarantee
- rel: related_to
  target_object_id: AP_make_a_function_exception_safe
reference:
  source_title: 'Effective C++, Third Edition: 55 Specific Ways to Improve Your Programs and Designs'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Offer a Definite Exception-Safety Guarantee

## Pattern Rule
**IF** you write a function that could throw or that calls something that throws
**THEN** make it leak no resources and corrupt no data, and offer one of the three guarantees on purpose — basic (a valid state), strong (state unchanged on failure), or nothrow — choosing the strongest that is practical.

## Do
- Use RAII objects — a lock guard, a smart pointer — so resources are released even when an exception is thrown.
- Reorder so you do not record that something happened until it actually has, such as incrementing a change counter only after the change succeeds.
- Document the guarantee each function offers; it is part of the function's interface, chosen as deliberately as any other part.
- Use `noexcept` when escaping exceptions are forbidden by the interface and the implementation can uphold that promise. Remember that violation calls `std::terminate`; the specifier does not manufacture recovery or make a fallible operation succeed.

## Don't
- Don't inherit a callee's weaker guarantee blindly. A transaction, temporary value, rollback guard, or caught-and-translated failure may let the caller provide a stronger observable guarantee; without such isolation or recovery, the callee's effects limit what the caller can promise.
- Don't confuse a function with no `noexcept` specifier with a non-throwing contract, and don't confuse `noexcept` with the strong guarantee. The former permits propagation; the latter is a promise about state when an operation fails.

## Checklist
- On a thrown exception, does this function leak a resource or leave data corrupted?
- Which guarantee — basic, strong, or nothrow — does it offer, and is it the strongest practical one?
- If a callee has a weaker guarantee, what isolation, rollback, or recovery lets this function promise more?
- Does any `noexcept` declaration match every path that can escape?

## Notes
The naive `changeBackground` fails both requirements: if constructing the new image throws, the manually locked mutex leaks and `bgImage` is left dangling with the counter already bumped. RAII removes the leak; reordering or preparing a replacement before commit removes the corruption. Then choose a guarantee deliberately — non-throwing where the operation can uphold it, otherwise strong where transaction structure is practical, otherwise basic. A callee's guarantee constrains the design, but a caller can strengthen its own observable result by isolating tentative work, rolling it back, or translating the failure. `noexcept` separately controls whether an exception may escape; it does not name the basic or strong state guarantee.
