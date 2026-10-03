---
object_id: PAT_default_rust_generic_parameters_for_the_dominant_case
object_type: pattern
name: Default Rust Generic Parameters for the Dominant Case
library_path: [software-engineering, languages, rust, traits]
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, generics, default_type_parameters, traits, api_evolution]
cross_links:
- rel: related_to
  target_object_id: PAT_choose_rust_associated_types_for_one_per_implementor_relationships
- rel: related_to
  target_object_id: PAT_state_your_compatibility_promise_and_its_span
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
references: []
variants: []
---

# Default Rust Generic Parameters for the Dominant Case

## Pattern Rule
**IF** a Rust trait or type has one dominant type argument but must preserve an explicit extension point for uncommon alternatives or compatible evolution
**THEN** give the generic parameter the dominant concrete default and let exceptional implementations override it.
**ELSE** require the type argument explicitly when no choice is safely representative.

## Do
- Choose a default that preserves the meaning most existing callers already expect, such as an operator's right-hand side defaulting to `Self`.
- Keep the override visible in the exceptional implementation so readers can see where the relationship differs from the default.
- Use a default when adding a parameter to an established interface would otherwise force mechanically identical edits across existing implementations.
- Test both the omitted default and at least one explicit alternative, because they are separate public paths.

## Don't
- Don't hide a type choice that materially changes semantics merely to reduce angle-bracket syntax.
- Don't choose a default from the first implementation when the intended callers have no clear dominant case.
- Don't assume a default prevents breaking changes by itself; existing inference, implementations, and coherence must still be checked.

## Checklist
- What proportion of intended uses should choose the default?
- Does omitting the argument preserve the existing or least-surprising behavior?
- Is the exceptional type relationship explicit at its implementation site?
- Do tests exercise both the defaulted and overridden forms?
- Would requiring the argument communicate an important semantic distinction that the default would conceal?

## Notes
A default type parameter does not remove variability; it assigns one value to the unmarked path. That makes it useful for dominant conventions and some compatible extensions, while keeping uncommon relationships expressible where they occur.
