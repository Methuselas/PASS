---
object_id: AP_build_a_rust_custom_derive_with_structured_tokens_and_diagnostics
object_type: ap
name: Build a Rust Custom Derive with Structured Tokens and Diagnostics
library_path: [software-engineering, languages, rust, macros]
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, procedural_macros, derive, token_stream, diagnostics]
cross_links:
- rel: supports
  target_object_id: PAT_choose_a_rust_macro_only_for_syntax_level_generation
- rel: related_to
  target_object_id: PAT_define_your_code_contract_explicitly
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
references: []
variants: []
---

# Build a Rust Custom Derive with Structured Tokens and Diagnostics

## Objective
Generate a trait implementation from a Rust type declaration without stringifying source, losing generic constraints, panicking on caller mistakes, or emitting code whose paths and spans fail at the invocation site.

## Steps / Flow
1. Define the ordinary trait and its semantic contract first. Specify the supported input items, fields, generic forms, helper attributes, and generated behavior before designing the derive syntax.
2. Put the procedural entry point in a crate configured as a procedural-macro crate. Decide whether the normal library re-exports the derive or whether users depend on the library and derive crates separately.
3. Keep the compiler-facing entry point thin: accept the compiler token stream, parse it directly into a structured syntax tree, and return generated tokens. Do not round-trip source through strings.
4. Move validation and expansion into a function that accepts structured input and returns either a testable token stream or a structured error. Validate item kind, attributes, fields, and unsupported combinations before emission.
5. Extract the type name and preserve its lifetime, type, const-generic, and where-clause structure in the generated implementation. Add bounds only for fields or operations that actually require them.
6. Quote the implementation from structured tokens. Use deliberate support-crate paths and attach generated references and errors to relevant input spans so downstream compiler messages point back to the caller's code.
7. Convert parse and validation failures into spanned compile errors. Combine independent diagnostics when doing so helps the caller repair the invocation in one pass; reserve panics for defects inside the macro itself.
8. Test the expansion boundary with compile-pass and compile-fail fixtures covering unit, named-field, tuple, generic, lifetime, const-generic, where-clause, helper-attribute, malformed, and unsupported inputs. Test the pure expansion helpers separately.
9. Publish compatible library and derive-crate versions together, and document the supported input grammar and generated contract as part of the public API.

## Notes
- The compiler API deliberately exchanges token streams rather than a compiler-internal syntax tree. A parsing library can provide a convenient owned syntax representation, and a quoting library can produce tokens without making formatted source strings the interface.
- Procedural macro output is not magically hygienic. Generated names, paths, and spans must be chosen with the invocation context in mind.
- A procedural macro and its dependencies execute during compilation with build-script-like access to compiler resources. Review and pin that dependency path according to the project's build-time code policy.
- A derive macro adds code; it does not replace the annotated item. Attribute-like and function-like procedural macros have different entry signatures and transformation contracts, so do not silently broaden a derive API into those forms.
