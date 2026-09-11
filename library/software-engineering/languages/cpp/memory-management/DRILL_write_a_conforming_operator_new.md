---
object_id: DRILL_write_a_conforming_operator_new
object_type: drill
name: Write a Conforming Class-Specific operator new and delete
target_skill: Preserving allocation contracts across size, failure, alignment, and deallocation forms
library_path:
- software-engineering
- languages
- cpp
- memory-management
stage_binding: 3 rough
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- memory_management
- allocation
- conventions
cross_links:
- rel: related_to
  target_object_id: PAT_follow_new_delete_conventions
reference:
  source_title: 'Effective C++, Third Edition: 55 Specific Ways to Improve Your Programs and Designs'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Write a Conforming Class-Specific operator new and delete

## Practice Task
Write a class-specific operator new and operator delete that follow the required conventions.

## Target Skill
Implementing a class-specific allocation family without losing global failure, alignment, or matching-deallocation behavior.

## Setup
No special setup required.

## Instructions
- Delegate the ordinary form to `::operator new` so the global `new_handler`, zero-size, and `std::bad_alloc` contract is preserved; instrument around the delegation rather than reimplementing it.
- Add and exercise the alignment-aware form for an over-aligned instance, verifying the returned address satisfies the requested alignment.
- Forward any request whose size is not the class size to the global operator new, and exercise a wrong-sized request showing it reach the global version.
- Provide matching unsized, sized, aligned, and sized-aligned delete forms required by the supported allocation paths, each delegating to its corresponding global form. Record which overloads the test toolchain actually selects without assuming every implementation chooses the same optional sized form.
- Either make the pooled class `final` or exercise a larger derived allocation and demonstrate the wrong-size request is forwarded. If deletion occurs through a base pointer, make the destructor virtual; otherwise the program is undefined before allocator accounting can rescue it.

## Success Check
- The ordinary form delegates to the global form, and the run demonstrates the intended allocation and failure path rather than duplicating the global handler loop.
- An over-aligned allocation is exercised and its address is checked against the requested alignment.
- A wrong-sized request is exercised and shown reaching the global version. This path appears only under inheritance, which is exactly why it goes untested.
- Matching deallocation overloads are present for every exercised allocation form, and instrumentation records which one the toolchain selects.
- Inheritance is either prohibited with `final` or tested with wrong-size forwarding and a virtual destructor for polymorphic deletion.

## Common Failures
- Reimplementing the global new-handler loop unnecessarily and getting its progress or failure behavior wrong.
- Omitting the alignment-aware form for an over-aligned type.
- Forgetting that inheritance can call the base operator new with a derived object's larger size.

## Notes
This drills the modern allocation overload family. Delegation preserves standard failure behavior; the class-specific work is the measured customization plus truthful handling of size, alignment, inheritance, and every deallocation path the supported expressions may select.
