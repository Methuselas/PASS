---
object_id: PAT_precede_nested_dependent_types_with_typename
object_type: pattern
name: Disambiguate Dependent Type Names with typename
library_path:
- software-engineering
- languages
- cpp
- templates
stage_binding: 3 rough
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- templates
- typename
- dependent_names
cross_links:
- rel: related_to
  target_object_id: PAT_program_to_a_templates_implicit_interface
reference:
  source_title: 'Effective C++, Third Edition: 55 Specific Ways to Improve Your Programs and Designs'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Disambiguate Dependent Type Names with typename

## Pattern Rule
**IF** a qualified name inside a template depends on a template parameter and the surrounding grammar does not already establish that a type is required
**THEN** precede the name with `typename` so the parser treats it as a type.

## Do
- Write `typename` before a dependent qualified type in an ambiguous context, such as a `using value_type` alias to the dependent trait's `value_type` member.
- Prefer a `using` alias for a long dependent type so the full qualified name and its disambiguation appear once.
- Let C++20's type-only contexts do their job: when the grammar already requires a type, `typename` may be omitted. Keep it where ambiguity remains rather than applying or removing it mechanically.

## Don't
- Don't put `typename` on a non-dependent name or on the template parameter itself; it disambiguates a qualified dependent name.
- Don't use typename in a base class list or a member initialization list, even for a nested dependent type name — it is disallowed in those two positions.

## Checklist
- Is this a qualified dependent name in a context where the parser cannot already know it is a type?
- Am I wrongly adding typename to a non-dependent name or in a base-class-list or init-list position?
- Have I used a `using` alias to avoid repeating a long dependent type name?

## Notes
Until the template parameter is known, the parser may not know whether `C::const_iterator` names a type or a value, so `typename` resolves the ambiguity. A base-class list and a member-initializer list do not accept it, and C++20 recognizes additional type-only contexts where it is unnecessary. The stable rule is therefore semantic: use `typename` to disambiguate, not as punctuation before every dependent name.
