---
object_id: PAT_use_template_metaprogramming
object_type: pattern
name: Move Work to Compile Time with the Simplest C++ Facility
library_path:
- software-engineering
- languages
- cpp
- metaprogramming
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- metaprogramming
- compile_time
- templates
cross_links:
- rel: related_to
  target_object_id: PAT_use_traits_classes_for_type_info
- rel: related_to
  target_object_id: PAT_prefer_const_and_enum_to_define
reference:
  source_title: 'Effective C++, Third Edition: 55 Specific Ways to Improve Your Programs and Designs'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Move Work to Compile Time with the Simplest C++ Facility

## Pattern Rule
**IF** a computation, constraint, or type-dependent choice can and should be resolved during compilation
**THEN** use the most direct C++20 facility that expresses it — `constexpr` or `consteval`, concepts, `if constexpr`, folds, and standard traits — and use lower-level template metaprogramming only when the result itself is a type or overload set those facilities cannot express cleanly.

## Do
- Use `constexpr` functions for ordinary compile-time-capable algorithms and `consteval` only when every call must be evaluated during translation.
- Use concepts to state admissible types, `if constexpr` for a small local type-dependent branch, and fold expressions for operations over a parameter pack.
- Use traits, specialization, or overload sets when the result is a type, customization, or reusable dispatch decision. Reach for recursive instantiation only for genuinely recursive type structure or compatibility with older code.

## Don't
- Don't use an ordinary runtime `if` when one branch is ill-formed for the selected template argument; use constraints, overloads, or `if constexpr` so the discarded path is not instantiated.
- Don't encode value calculations as recursive template specializations and enum-hack constants when a readable `constexpr` function or variable expresses the same work.
- Don't move work to translation merely because it is possible; account for compile time, diagnostics, code size, and readability.

## Checklist
- Is compile-time evaluation required or materially useful here?
- Is this a value computation, a constraint, a local branch, a pack operation, or a type computation — and have I chosen the direct facility for that category?
- Does splitting per type avoid emitting code that is invalid for some instantiations?
- Is the added complexity and compile-time cost justified by the benefit here?

## Notes
Classic template metaprogramming proved that translation can compute arbitrary results, but its recursive specializations and enum-hack values were mechanisms of necessity. C++20 offers facilities that state the common intentions directly. Traits and overloads still matter when a computation produces types or a reusable dispatch surface; concepts, `if constexpr`, folds, and constant-evaluation functions should carry the ordinary cases. Compile-time dimensional checks, policy composition, and expression templates remain valuable when their earlier errors or generated implementation justify their cost.
