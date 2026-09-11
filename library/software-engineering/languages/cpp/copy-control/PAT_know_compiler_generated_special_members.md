---
object_id: PAT_know_compiler_generated_special_members
object_type: pattern
name: Know the Special Member Functions the Compiler Writes for You
library_path:
- software-engineering
- languages
- cpp
- copy-control
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- copy_control
- special_members
- class_design
cross_links:
- rel: related_to
  target_object_id: PAT_copy_all_members_and_base_parts
- rel: related_to
  target_object_id: PAT_delete_the_functions_you_want_to_forbid
- rel: related_to
  target_object_id: AP_write_copy_control_for_a_resource_owning_class
reference:
  source_title: 'Effective C++, Third Edition: 55 Specific Ways to Improve Your Programs and Designs'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Know the Special Member Functions the Compiler Writes for You

## Pattern Rule
**IF** a class relies on implicitly declared special members
**THEN** account for all six — default construction, destruction, copy construction, copy assignment, move construction, and move assignment — and verify whether each is generated, deleted, or suppressed before accepting the Rule of Zero result.

## Do
- Expect a generated copy to duplicate each non-static member memberwise: a string member through its own copy constructor, an int member bit-for-bit.
- Expect a generated move to initialize or assign bases and members from rvalues when their operations support it; an individual member may still copy if that is the viable operation.
- Remember the default constructor is generated only when you declare no constructors at all; declaring any constructor suppresses it.
- Know the generated destructor is non-virtual unless a base class already declares a virtual destructor.
- Prefer the Rule of Zero: compose resource-owning members whose own special members are correct, then declare none of the six in the containing class.

## Don't
- Don't assume an implicitly declared operation is usable. It may be defined as deleted because a base or member cannot perform the corresponding operation.
- Don't infer move support from a successful `std::move` call; overload resolution may have selected a copy operation.

## Checklist
- Which special members will the compiler generate for this class, and which am I relying on?
- Is any implicitly declared member defined as deleted by a base, reference, const member, or non-movable resource?
- Do I actually want memberwise copying, or something different?
- Can the class follow the Rule of Zero by delegating ownership to its members?

## Notes
An apparently empty class still has an implicit default constructor, destructor, copy operations, and—when no declaration suppresses them—move operations. Their definitions are memberwise, and any operation may become deleted when a base or member cannot support it. The detailed suppression interactions live in `PAT_understand_special_member_generation`; this card owns the inventory and the Rule of Zero default. Knowing exactly what exists is the prerequisite for every later copy-control decision.
