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
- In the classic version, read `iterator_category` from `std::iterator_traits`, write overloaded workers, and pass the category tag from the entry point so overload resolution selects a worker during compilation.
- Check each classic worker against its advertised operations: random access may use `+=`; bidirectional may step both directions; an input iterator may advance only forward.
- In the C++20 version, constrain the entry point to an appropriate iterator/sentinel contract and choose the short implementation branch with `if constexpr` and standard iterator concepts.
- Compile both versions for a pointer, a bidirectional standard iterator, and an input iterator. Include a negative-distance case only where the iterator contract permits it.
- Write an ordinary runtime-`if` version or explain its failure precisely: a branch that is never executed must still be well-formed for the instantiated type.
- Explain why classic tag inheritance selects a compatible weaker worker, and why the C++20 version should query the required operation rather than compare tags for equality.

## Success Check
- Both implementations compile for the three required iterator shapes, and the evidence includes which branch or overload each selected.
- Each implementation uses only operations its stated category or concept guarantees, including the negative-distance distinction.
- The runtime-branch failure is demonstrated or explained precisely: runtime control flow cannot discard an ill-formed template branch.
- The comparison identifies tag dispatch as a classic-protocol compatibility technique and concepts plus `if constexpr` as the C++20 default for this closed operation choice.

## Common Failures
- Comparing classic category tags for exact equality, which misses stronger categories that inherit from weaker ones.
- Treating an input iterator as bidirectional when exercising a negative distance.
- Constraining the C++20 version by a named tag instead of by the operation it actually needs.

## Notes
This preserves the classic traits-and-overload technique because existing iterator protocols still use it, while making the C++20 decision explicit: concepts describe admissible operations, and `if constexpr` is the direct tool for a small closed compile-time branch.
