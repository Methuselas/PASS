---
object_id: PAT_adapt_rules_to_active_cpp_sublanguage
object_type: pattern
name: Adapt Rules to the Active C++ Language Profile
library_path:
- software-engineering
- languages
- cpp
- foundations
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- sublanguages
- idioms
- parameter_passing
cross_links:
- rel: related_to
  target_object_id: PAT_manually_initialize_builtin_objects
reference:
  source_title: 'Effective C++, Third Edition: 55 Specific Ways to Improve Your Programs and Designs'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Adapt Rules to the Active C++ Language Profile

## Pattern Rule
**IF** you are choosing or applying a C++ rule
**THEN** establish the project's language standard, toolchain support, and the boundary the code crosses — C interop, object lifetime, templates, or library abstractions — then use the convention that fits that active language profile.

## Do
- Read the build configuration and supported compiler matrix before recommending a facility. The project's declared standard wins; when no standard is declared, use C++20 as the default floor.
- Treat C++23 facilities as supported alternatives, not silent requirements: label them, retain a C++20 path, and verify the actual compiler and standard library implement them.
- Distinguish boundaries that impose different constraints. A C API may require pointers and counts; a value type may prefer value semantics; a template should express constraints; a ranges pipeline follows library concepts.
- Reassess inherited rules against the active profile. Prefer modern ownership, constraints, ranges, and compile-time facilities when they solve the problem more directly than a pre-C++11 workaround.

## Don't
- Don't preserve an older workaround merely because the source predates the facility that replaced it.
- Don't equate inclusion in a language standard with availability in every supported compiler and standard library.
- Don't force every decision into the historical four-sublanguage taxonomy; use the concrete interface, lifetime, genericity, and library constraints in front of you.

## Checklist
- What C++ standard and toolchain matrix does this project declare?
- If none is declared, am I using C++20 as the floor and labeling any C++23 option?
- Which boundary or language mechanism changes the rule here?
- Have I verified support instead of assuming that a standardized facility is available?

## Notes
The historical federation-of-languages model remains useful because C interop, object-oriented code, templates, and the standard library do impose different constraints. Modern C++ adds another necessary axis: the project's selected standard and the facilities its toolchains actually implement. C++20 is this module's default when a project supplies no answer; it is not permission to override an explicit C++17 codebase or to assume that every implementation has complete support. Likewise, C++23 can simplify a design without becoming an accidental minimum requirement.
