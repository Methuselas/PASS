---
object_id: DRILL_implement_traits_based_dispatch
object_type: drill
name: Compare Iterator Tag Dispatch with C++20 Concept Dispatch
target_skill: Selecting an iterator implementation at compile time while distinguishing compatibility traits from C++20 operation constraints
library_path:
- software-engineering
- languages
- cpp
- traits
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- traits
- templates
- compile_time
cross_links:
- rel: related_to
  target_object_id: PAT_use_traits_classes_for_type_info
reference:
  source_title: 'Effective C++, Third Edition: 55 Specific Ways to Improve Your Programs and Designs'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Compare Iterator Tag Dispatch with C++20 Concept Dispatch

## Practice Task
Implement an `advance(iter, d)` exercise twice: first with classic `std::iterator_traits` category dispatch, then with C++20 iterator concepts and `if constexpr`. Use iterator arithmetic for random-access iterators and valid stepping for the weaker cases.

## Target Skill
Choosing compile-time dispatch from the actual protocol in use, and explaining when a compatibility trait or a C++20 concept is the right interface.

## Setup
No special setup required.

## Instructions
- In the classic version, read `iterator_category` from `std::iterator_traits`, write overloaded workers for random-access, bidirectional, and input iterators, and pass the category tag from the entry point so overload resolution selects a worker during compilation.
- Check each classic worker against its advertised operations: random access may use `+=`; bidirectional may step both directions; an input iterator may advance only forward.
- In the C++20 version, constrain the entry point to an appropriate iterator/sentinel contract and choose the short implementation branch with `if constexpr` and standard iterator concepts.
- Compile and run both versions for a pointer, a bidirectional standard iterator, an input iterator, a forward-only iterator such as `std::forward_list`'s, and the iterator of `std::views::iota`, recording which branch or overload each selected. Include a negative-distance case only where the iterator contract permits it.
- State which classic worker the forward-only iterator reached and why, and what an exact comparison against each category tag would have selected for it.
- Write an ordinary runtime-`if` version, compile it for a non-random-access iterator, and retain the diagnostic.
- Call your `advance` unqualified on a standard container's iterator, and record what the compiler does.
- Compare the two versions and state when each is the right interface.

## Success Check
- Both implementations compile and run for all five iterator shapes, and the evidence includes which branch or overload each selected.
- Each implementation uses only operations its stated category or concept guarantees, including the negative-distance distinction.
- The forward-only iterator is recorded reaching the input worker through tag inheritance, and the run says an exact comparison against the input tag would have matched nothing.
- The `std::views::iota` iterator is recorded taking the one-step path under classic dispatch and `+=` under the C++20 version: it advertises only an input category to classic code while modeling random access. A run that tests standard container iterators alone sees the two versions agree everywhere and concludes the choice is one of style.
- The runtime-branch failure is compiled and its diagnostic retained: runtime control flow cannot discard an ill-formed template branch. An explanation without the build satisfies this bullet in wording only.
- The unqualified call is recorded: on a standard iterator, argument-dependent lookup finds `std::advance` as well, and the call is ambiguous.
- The comparison identifies tag dispatch as a classic-protocol compatibility technique and concepts plus `if constexpr` as the C++20 default for this closed operation choice.

## Common Failures
- Comparing classic category tags for exact equality, which misses stronger categories that inherit from weaker ones.
- Treating an input iterator as bidirectional when exercising a negative distance.
- Constraining the C++20 version by a named tag instead of by the operation it actually needs.
- Calling a function named `advance` unqualified on standard iterators, where argument-dependent lookup also finds `std::advance`.

## Notes
This preserves the classic traits-and-overload technique because existing iterator protocols still use it, while making the C++20 decision explicit: concepts describe admissible operations, and `if constexpr` is the direct tool for a small closed compile-time branch. A range iterator that is random-access in C++20 terms can still advertise only an input category to classic dispatch, which is where the two stop being interchangeable.
