---
object_id: PAT_design_a_callable_for_the_copies_an_algorithm_will_make
object_type: pattern
name: Design a Callable for an Algorithm's Value Requirements
library_path:
- software-engineering
- languages
- cpp
- algorithms
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- algorithms
- function_objects
- slicing
- efficiency
cross_links:
- rel: related_to
  target_object_id: PAT_make_a_predicate_a_pure_function
- rel: related_to
  target_object_id: PAT_minimize_compilation_dependencies
- rel: related_to
  target_object_id: PAT_prefer_pass_by_reference_to_const
reference:
  source_title: 'Effective STL: 50 Specific Ways to Improve Your Use of the Standard Template Library'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Design a Callable for an Algorithm's Value Requirements

## Pattern Rule
**IF** you are handing a stateful callable to a standard algorithm
**THEN** check that algorithm's copy, move, const-call, and return requirements, keep the callable cheap to pass by value, and do not rely on mutations being visible through the original callable object
**ELSE** where the callable is large, move-only, or identity-sensitive, pass a small explicit reference or ownership wrapper only when the algorithm's contract accepts it.

## Do
- Read the selected classic or ranges algorithm's callable requirements instead of assuming every algorithm treats state the same way. Many C++20 algorithms require a copy-constructible predicate or projection and may copy it internally.
- Keep captures small and make the call operation usable with the cv-qualification the algorithm requires.
- Put shared observation state behind an explicit reference or shared owner when the test must inspect it after the call. A mutation made only inside one algorithm-owned copy may not appear in the original object.
- If polymorphic behavior is genuinely required, type-erase or share it deliberately. Template deduction normally preserves the callable's concrete type; slicing occurs only when the callable was already converted or passed through a base object.

## Don't
- Don't assume a lambda is exempt. A lambda capturing a large object by value is a large callable; capturing by reference avoids that size and introduces a lifetime question in its place.
- Don't force pass-by-reference by naming the algorithm's template arguments explicitly at the call site. It is legal, almost nobody does it, and some implementations of some algorithms will not compile when the callable arrives by reference.
- Don't infer from a successful call that a move-only callable is portable across the supported algorithms and libraries. Verify the named algorithm's actual requirements under the project's C++20 toolchains.

## Checklist
- How large is this callable, counting everything captured or stored by value?
- Is it copyable, movable, and callable with the qualification the chosen algorithm requires?
- Does any state need to be observed after the call, and if so where is that shared state stored?
- If it needs polymorphism, is type erasure or shared indirection explicit rather than accidental base-object conversion?

## Notes
The durable rule is about value semantics, not a universal count of copies. Algorithms are permitted to copy their callable according to their specified requirements, and implementations differ in how many times they do so. A small value-like closure survives that freedom. State whose identity matters must live somewhere every copy intentionally shares, and its lifetime and synchronization then become part of the design.

The advice reads as being about hand-written functor classes because that is what it was written for, and it transfers to lambdas without amendment. A lambda is a function object with a compiler-written class, and the capture list determines its size exactly as member declarations would.

A concrete function object or lambda also keeps the call target visible to optimization more readily than an erased or indirect call. Treat that as an opportunity, not a guarantee: measure the real algorithm and input before choosing a storage model for presumed inlining.
