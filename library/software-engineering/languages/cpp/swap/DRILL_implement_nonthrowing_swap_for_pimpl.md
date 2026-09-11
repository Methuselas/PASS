---
object_id: DRILL_implement_nonthrowing_swap_for_pimpl
object_type: drill
name: Implement an Efficient Non-throwing swap for a Pimpl Type
target_skill: Wiring up a noexcept member swap and an ADL-visible non-member customization
library_path:
- software-engineering
- languages
- cpp
- swap
stage_binding: 3 rough
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- swap
- pimpl
- exception_safety
cross_links:
- rel: related_to
  target_object_id: PAT_support_nonthrowing_swap
reference:
  source_title: 'Effective C++, Third Edition: 55 Specific Ways to Improve Your Programs and Designs'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Implement an Efficient Non-throwing swap for a Pimpl Type

## Practice Task
Given a `Widget` that holds a pointer to a `WidgetImpl` (the pimpl idiom), give it an efficient, non-throwing swap wired up correctly.

## Target Skill
Providing a member swap and an ADL-visible non-member or hidden-friend swap, then verifying generic lookup and the nothrow contract.

## Setup
No special setup required.

## Instructions
- Add a public member swap that exchanges the two internal pointers and cannot throw, and confirm the pointed-to data was never touched.
- Argue the no-throw property from what the member actually does, and state what would break it.
- Add a non-member swap in Widget's namespace that calls the member, and say why the non-member in the class's own namespace is what makes an unqualified call work.
- Do not add an overload or specialization in namespace `std`. Explain why the type's own namespace is the customization point generic callers can find through argument-dependent lookup.
- Write a client that does `using std::swap;` and then calls swap unqualified. Also exercise `std::ranges::swap` and verify both reach the fast operation.
- Assert the standard nothrow-swappable trait for `Widget` so the exception guarantee is machine-checked.

## Success Check
- The member swap is confirmed to exchange only the pointers, checked by observing that the pointed-to data was never touched.
- The no-throw property is argued from what the member actually does, and the run states what would break it. A swap of anything that allocates is not this technique and will not hold the guarantee callers depend on.
- The unqualified generic call and `std::ranges::swap` are exercised and each shown to reach the fast operation.
- The run says why the non-member in the class's own namespace is what makes the unqualified call work, rather than treating the several overloads as ceremony to be copied.
- The standard nothrow-swappable trait succeeds, and no declaration has been added to namespace `std`.

## Common Failures
- Adding an overload or specialization of swap inside namespace `std` instead of using the ADL customization point.
- Qualifying the call as std::swap and losing argument-dependent lookup to the type-specific version.

## Notes
This drills the modern swap customization: a `noexcept` member, an ADL-visible non-member or hidden friend, and generic unqualified calls. Code that hard-qualifies `std::swap` bypasses the customization and should not dictate additions to namespace `std`.
