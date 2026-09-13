---
object_id: DRILL_complete_a_derived_class_copying_functions
object_type: drill
name: Complete a Derived Class's Copying Functions
target_skill: Writing derived-class copying functions that copy base parts and every member
library_path:
- software-engineering
- languages
- cpp
- copy-control
stage_binding: 3 rough
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- copy_control
- inheritance
- class_design
cross_links:
- rel: related_to
  target_object_id: PAT_copy_all_members_and_base_parts
reference:
  source_title: 'Effective C++, Third Edition: 55 Specific Ways to Improve Your Programs and Designs'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Complete a Derived Class's Copying Functions

## Practice Task
Given a base `Customer` (a name and a last-transaction date) and a derived `PriorityCustomer` (a priority) whose hand-written copying functions copy only `priority`, fix them so nothing is dropped, then decide whether the class should hand-write them at all.

## Target Skill
Copying every local member and invoking the base class's copying and moving functions from a derived class, and recognizing when removing the hand-written functions is the better repair.

## Setup
Give `Customer`'s members a type that counts its own copies and moves.

## Instructions
- Read the class declaration and list which members and base parts the current copying functions fail to copy.
- Copy-construct and copy-assign an object, and record the state of the base part in each result.
- In the copy constructor, invoke the base copy constructor in the member initialization list.
- In the copy assignment operator, call the base class operator= before copying the derived members.
- State what happens instead when each of those two base calls is omitted.
- State the relationship between the two copying functions, and whether either should be implemented by calling the other.
- Add a new member to the base class, name every copying function that must now change before consulting the compiler, then consult the compiler and compare the two lists.
- Move-construct the fixed class with `std::move` and record how many base members were copied and how many moved.
- Add a derived move constructor and record the same counts.
- Remove every hand-written copying and moving function, repeat the copy and move measurements, and state what would justify writing them again.

## Success Check
- The members and base parts the original copying functions miss are listed before the fix, produced by reading the class declaration rather than by reading the copying functions, which is what omitted them in the first place.
- The failure is demonstrated: an object is copied and the base part is shown default-constructed by the copy constructor and left unchanged by the assignment. The compiler produces this without a warning, which is why an inspection is not enough.
- The base copy constructor is invoked in the member initialization list and the base assignment operator is called explicitly, and the run states what happens instead when each is omitted. The two omissions have different symptoms and only one of them is easy to see.
- A base member is actually added; every copying function needing a change is named before the compiler is consulted, and then the compiler is consulted. The gap between those two lists is the finding, because the compiler reports none of them.
- The run states the relationship between the two copying functions — why neither should be implemented by calling the other — rather than leaving them as parallel hand-written bodies whose agreement is a coincidence.
- The move counts are recorded, not predicted: the fixed class copies both base members under `std::move`, because hand-written copying functions suppress the implicit move constructor, and the added derived move constructor's counts show the base moved rather than copied. A move constructor that passes `rhs` to the base compiles and copies it, and a class that copies correctly passes every bullet above while every move of it is a copy.
- With the hand-written functions removed, the copy is measured complete and the move measured as moves, and the run names a concrete reason that would justify writing them again rather than treating the repaired versions as the goal.

## Common Failures
- Omitting the base call, so base parts are default-constructed (copy constructor) or left unchanged (assignment).
- Copying only the newly declared derived members and forgetting the inherited ones.
- Passing `rhs` to the base in a derived move constructor: a named rvalue reference is an lvalue, so the base copy constructor is selected.

## Notes
A derived copying function never copies base members for you: the base part is default-constructed or left alone unless the base function is called explicitly, and the compiler says nothing. The same silence covers moves, where hand-written copying functions turn every move into a copy. Writing none of them is often the sturdier repair, because the generated functions stay complete as members are added.
