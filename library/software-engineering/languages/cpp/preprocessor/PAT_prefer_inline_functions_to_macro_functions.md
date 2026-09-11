---
object_id: PAT_prefer_inline_functions_to_macro_functions
object_type: pattern
name: Prefer Functions and Lambdas to Function-Like Macros
library_path:
- software-engineering
- languages
- cpp
- preprocessor
stage_binding: 3 rough
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: PAT_adopt_language_features_when_best_tool
tags:
- cpp
- preprocessor
- inline
- templates
cross_links:
- rel: related_to
  target_object_id: PAT_prefer_const_and_enum_to_define
reference:
  source_title: 'Effective C++, Third Edition: 55 Specific Ways to Improve Your Programs and Designs'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Prefer Functions and Lambdas to Function-Like Macros

## Pattern Rule
**IF** you are tempted to write a function-like macro for computation or control flow
**THEN** write a function, function template, generic lambda, or `constexpr` function instead, so arguments are evaluated once and the operation retains types, scope, and normal diagnostics.

## Do
- Turn `#define CALL_WITH_MAX(a,b) ...` into a function template or constrained generic lambda whose parameter policy matches the values it accepts.
- Use `constexpr` when the operation should be available during constant evaluation. Use `inline` when its linkage rules are needed for a header definition; leave actual inlining to the optimizer.

## Don't
- Don't accept a macro's evaluation surprises: `CALL_WITH_MAX(++a, b)` increments `a` a different number of times depending on the value it is compared against.
- Don't lean on remembering to parenthesize every macro argument; a real function needs none of that and still honors scope and access rules, so it can even be private to a class.

## Checklist
- Does this genuinely need preprocessing, or will a function, template, lambda, or `constexpr` function do?
- Could any argument be evaluated more than once when passed to the macro?
- Would a member function or local lambda express the required scope more safely?

## Notes
A function-like macro does not itself guarantee speed; it performs token substitution, may evaluate arguments repeatedly, and bypasses language scope and type checking. Modern functions, templates, and lambdas expose the operation to the optimizer without those hazards. The `inline` keyword primarily changes the multiple-definition rules for a function defined in a header; it does not command the optimizer. Includes and conditional compilation still require preprocessing, but ordinary computation almost never does.
