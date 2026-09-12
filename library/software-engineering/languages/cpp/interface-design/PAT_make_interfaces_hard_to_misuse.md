---
object_id: PAT_make_interfaces_hard_to_misuse
object_type: pattern
name: Make Interfaces Easy to Use Correctly and Hard to Use Incorrectly
library_path:
- software-engineering
- languages
- cpp
- interface-design
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: PAT_make_code_hard_to_misuse
tags:
- cpp
- interface_design
- type_safety
- hard_to_misuse
cross_links:
- rel: related_to
  target_object_id: PAT_convey_usage_through_names_and_types
- rel: related_to
  target_object_id: PAT_design_a_class_as_type
- rel: related_to
  target_object_id: AP_make_a_class_const_correct
reference:
  source_title: 'Effective C++, Third Edition: 55 Specific Ways to Improve Your Programs and Designs'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Make Interfaces Easy to Use Correctly and Hard to Use Incorrectly

## Pattern Rule
**IF** you design a function, class, or template interface
**THEN** shape it so incorrect uses fail to compile and correct uses are the path of least resistance — because when a reasonable client misuses an interface, the interface is partly to blame.

## Do
- Introduce distinct types to bar wrong-order or wrong-kind arguments, and give each an `explicit` constructor from the raw value; wrapping day, month, and year that way stops a `Date(30, 3, 1995)` call from compiling. The keyword is what does the work. With converting constructors the raw call compiles unchanged, and with aggregate wrappers the raw call is refused while a braced call in the wrong order compiles — measured, only explicit constructors rejected both.
- Restrict what a type permits: const-qualify values and the references and pointers that should not write, and constrain valid values (predefined Month objects rather than raw ints). To stop a caller assigning to a returned temporary, ref-qualify the type's assignment operators rather than returning a const value: both reject the assignment, but a const return also turns every move of the result into a copy, while the ref-qualified operator kept the moves when measured. `PAT_return_values_without_top_level_const` owns that choice.
- Remove client bookkeeping: have a factory return a smart pointer so callers cannot forget to release, and bind a custom deleter to head off wrong-release and cross-DLL errors.
- Keep your types consistent with the built-ins and with one another — every standard container but the singly linked list has a `size()` — because consistency is what makes an interface easy to use, and an exception is worth making only as deliberately as that one was.

## Don't
- Don't require clients to remember to do something — call a specific delete, pass arguments in a special order — because whatever they must remember, they can forget.

## Checklist
- Can a plausible wrong use of this interface be made not to compile?
- Does the interface rely on the client remembering a step, an order, or a cleanup?
- Does this type behave like the built-in types the client already knows?

## Notes
This is the C++ realization of making code hard to misuse: the type system is your primary ally, so lean on it. The `Date` example turns a positional-argument trap into a compile error via wrapper types; constrained Month values stop out-of-range input; a factory returning a shared pointer with a bound deleter removes the whole class of release mistakes. Consistency matters as much as any single trick — inconsistency imposes mental friction no IDE removes.
