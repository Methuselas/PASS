---
object_id: PAT_support_nonthrowing_swap
object_type: pattern
name: Support a Non-throwing swap for Pimpl-style Types
library_path:
- software-engineering
- languages
- cpp
- swap
stage_binding: 3 rough
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- swap
- exception_safety
- pimpl
cross_links:
- rel: related_to
  target_object_id: PAT_handle_self_assignment_in_copy_assignment
- rel: related_to
  target_object_id: AP_make_a_function_exception_safe
- rel: related_to
  target_object_id: AP_write_copy_control_for_a_resource_owning_class
reference:
  source_title: 'Effective C++, Third Edition: 55 Specific Ways to Improve Your Programs and Designs'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Support a Non-throwing swap for Pimpl-style Types

## Pattern Rule
**IF** the default std::swap would be inefficient for your type — typically a pimpl type holding a pointer to its real data
**THEN** provide a fast `noexcept` member swap and an ADL-visible non-member or hidden-friend `swap` that calls it, then call swap unqualified after `using std::swap`.

## Do
- Write a public member swap that exchanges the internal pointers and never throws.
- Add a non-member swap in the same namespace that calls the member, so argument-dependent lookup finds it.
- When you call swap yourself, write `using std::swap;` and then call swap unqualified, so the best version is chosen.
- Verify the standard nothrow-swappable trait for the type (and the corresponding concepts where used) so generic code can rely on the guarantee.

## Don't
- Don't add overloads to namespace `std`, and don't require a `std::swap` specialization as part of the customization. The ADL-visible overload is the normal extension point and is also found by `std::ranges::swap`.
- Don't let the member swap throw — the strong exception-safety guarantee in other code depends on it.

## Checklist
- Is there a non-throwing member swap that exchanges only the internals?
- Is there a non-member swap in the type's namespace that calls the member?
- Is the non-member or hidden-friend swap visible to argument-dependent lookup?
- Do my own swap calls use an unqualified swap after `using std::swap;`?

## Notes
The generic swap operation uses moves, which may already be cheap for a well-designed pimpl type, but an explicit swap remains valuable when it is the primitive behind assignment and exception guarantees. The modern customization is an ADL-visible non-member—often a hidden friend—that delegates to a `noexcept` member. Generic callers use `using std::swap; swap(a, b);`, while ranges customization also respects the ADL operation. Code that hard-qualifies `std::swap` has intentionally bypassed that extension point and should not drive a namespace-`std` customization policy.
