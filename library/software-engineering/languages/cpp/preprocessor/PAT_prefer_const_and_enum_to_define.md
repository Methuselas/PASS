---
object_id: PAT_prefer_const_and_enum_to_define
object_type: pattern
name: 'Prefer constexpr Names to #define Constants'
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
- constants
- constexpr
cross_links:
- rel: related_to
  target_object_id: PAT_name_unexplained_values
- rel: related_to
  target_object_id: PAT_prefer_inline_functions_to_macro_functions
reference:
  source_title: 'Effective C++, Third Edition: 55 Specific Ways to Improve Your Programs and Designs'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Prefer constexpr Names to #define Constants

## Pattern Rule
**IF** you need a symbolic constant in C++
**THEN** define it as an appropriately scoped `inline constexpr` object, `constexpr` function, or scoped enumeration rather than a `#define`, so its type, scope, and value remain visible to the language.

## Do
- Replace `#define ASPECT_RATIO 1.653` with `inline constexpr double aspect_ratio = 1.653;`, choosing namespace or class scope to match ownership.
- Use `static inline constexpr` for a class constant. Since C++17 it needs no separate out-of-class definition merely because it is odr-used.
- Use a scoped `enum class` when the values form a closed set with domain meaning; use a `constexpr` object when the value is simply a named constant.

## Don't
- Don't leave a constant as a `#define` you might meet in a compiler error, a debugger, or a symbol table. The macro name is gone before compilation begins, so nothing downstream can show it to you, and what you get instead is whatever the implementation chooses to report - measured on one current compiler, the same failing call reported only the argument's type for both spellings, naming neither the literal nor the constant. The durable point is not the wording of any one diagnostic: it is that a `#define` leaves nothing for any tool to name, while a constant keeps a name that the language, the debugger, and the linker all still know.
- Don't expect a macro to respect class scope or privacy — there is no such thing as a private `#define` constant.
- Don't use the historical enum hack as general constant storage. Modern `constexpr` states the intent directly and preserves the intended type.

## Checklist
- Is this constant visible to the compiler and debugger by its name?
- If it belongs to a class, is it a `static inline constexpr` member?
- Is this a single named value or a closed set that should be a scoped enumeration?

## Notes
The theme is "prefer the language to the preprocessor." A `#define` is text-substituted before compilation, so it has no type, language scope, or ordinary debugger identity. The enum hack solved constant-expression and storage problems on old compilers; `constexpr` and inline variables now express those intentions directly. Keep the hack recognizable when maintaining legacy code, but do not teach it as the C++20 construction.
