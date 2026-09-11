---
object_id: PAT_initialize_members_with_init_list
object_type: pattern
name: Initialize Members with the Initializer List, in Declaration Order
library_path:
- software-engineering
- languages
- cpp
- initialization
stage_binding: 3 rough
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- initialization
- constructors
- member_initialization
cross_links:
- rel: related_to
  target_object_id: PAT_manually_initialize_builtin_objects
- rel: related_to
  target_object_id: PAT_replace_nonlocal_statics_with_local_statics
reference:
  source_title: 'Effective C++, Third Edition: 55 Specific Ways to Improve Your Programs and Designs'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Initialize Members with the Initializer List, in Declaration Order

## Pattern Rule
**IF** you are writing a constructor
**THEN** initialize bases and members before the body—using default member initializers for shared defaults and the constructor's initializer list for per-constructor values—and write the list in declaration order.

## Do
- Prefer `: theName(name), theAddress(address), thePhones(phones), numTimesConsulted(0)` to body assignments — each class-type member is copy-constructed once instead of default-constructed and then assigned over.
- Put a repeated default on the member declaration instead of duplicating it across constructor initializer lists; a constructor entry overrides that default when needed.
- Use a delegating constructor when several constructors should share one initialization path rather than repeating lists that can drift.
- Always initialize `const` members and references through the list; they cannot be assigned, so the list is the only option for them.
- Write the list in the same order the members are declared, because that is the order C++ actually initializes them regardless of how the list reads.

## Don't
- Don't assign a member in the constructor body when the value is available during initialization. Assignment may require an unnecessary prior construction and cannot initialize references or const members.
- Don't rely on the list's order to control initialization order — declaration order wins, so a mismatched list only misleads whoever reads it.

## Checklist
- Is every member initialized by a default member initializer or the active constructor's initializer list rather than repaired in the body?
- Are `const` and reference members initialized (not assigned)?
- Does the list order match the class's declaration order?

## Notes
The trap is confusing assignment with initialization. Bases and members are initialized before the constructor body runs, so body assignment may repair an object that was already constructed in the wrong state. Default member initializers centralize class-wide defaults; constructor initializer lists supply exceptions and dependencies; delegating constructors centralize shared construction flows. Actual initialization order remains base classes first and then members in declaration order, regardless of textual list order.
