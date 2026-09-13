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
Given a `Widget` that holds a `std::unique_ptr` to a `WidgetImpl` (the pimpl idiom), measure what the standard swap already costs, then give it a non-throwing swap wired up correctly.

## Target Skill
Providing a member swap and an ADL-visible non-member or hidden-friend swap, verifying generic lookup and the nothrow contract, and knowing what the custom swap buys over the standard one.

## Setup
Give `WidgetImpl` a copy counter and count allocations, so the cost of each swap can be observed.

## Instructions
- Before writing any swap, call `std::swap` on two `Widget`s and record the `WidgetImpl` copies and the allocations: once with `Widget`'s move operations declared `noexcept`, and once with only its copy operations. Check the standard nothrow-swappable trait in both.
- Add a public member swap that exchanges the two internal pointers and cannot throw, and confirm the pointed-to data was never touched.
- Argue the no-throw property from what the member actually does, and state what would break it.
- Add a non-member swap in Widget's namespace, or a hidden friend, that calls the member, and say what makes an unqualified call find it.
- Do not add an overload or specialization in namespace `std`. State where generic callers look for a type's own swap instead.
- Write a client that does `using std::swap;` and then calls swap unqualified. Also call `std::ranges::swap` and a qualified `std::swap`, and record which of the three reach the member swap.
- Assert the standard nothrow-swappable trait for `Widget` so the exception guarantee is machine-checked.
- State what the custom swap buys this `Widget` over the standard one, given the first measurement.

## Success Check
- The first measurement is recorded: with `noexcept` moves the standard swap copies no `WidgetImpl`, allocates nothing, and already satisfies the nothrow-swappable trait; with copies only it copies the implementation and does not satisfy the trait. A run that adds a custom swap for efficiency without this measurement has repeated the reason rather than tested it.
- The member swap is confirmed to exchange only the pointers, checked by observing that the pointed-to data was never touched.
- The no-throw property is argued from what the member actually does, and the run states what would break it. A swap of anything that allocates is not this technique and will not hold the guarantee callers depend on.
- Which calls reached the member swap is recorded: the unqualified call and `std::ranges::swap` do, and a qualified `std::swap` does not — it compiles and silently takes the generic path. The run says the non-member or hidden friend is found by argument-dependent lookup on `Widget`'s namespace, rather than treating the several overloads as ceremony to be copied.
- The standard nothrow-swappable trait succeeds, and no declaration has been added to namespace `std`.
- The closing statement is argued from the measurement: once the moves are `noexcept`, the custom swap buys a single pointer exchange where the generic path performs three moves, and a primitive that copy-and-swap assignment can be built on — not an escape from copying, which the moves already provided.

## Common Failures
- Adding an overload or specialization of swap inside namespace `std` instead of using the ADL customization point.
- Qualifying the call as std::swap and losing argument-dependent lookup to the type-specific version.
- Citing speed as the reason for a custom swap on a type whose `noexcept` moves already make the standard swap cheap.

## Notes
This drills the modern swap customization: a `noexcept` member, an ADL-visible non-member or hidden friend, and generic unqualified calls. For a pimpl type with `noexcept` moves the standard swap is already cheap, so the custom one earns its place as a primitive rather than as a speedup. Code that hard-qualifies `std::swap` bypasses the customization and should not dictate additions to namespace `std`.
