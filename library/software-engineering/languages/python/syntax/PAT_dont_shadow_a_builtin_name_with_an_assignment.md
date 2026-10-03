---
object_id: PAT_dont_shadow_a_builtin_name_with_an_assignment
object_type: pattern
name: Don't Shadow a Built-in Name with an Assignment
library_path:
- software-engineering
- languages
- python
- syntax
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- naming
- builtins
- scope
cross_links:
- rel: related_to
  target_object_id: PAT_resolve_names_by_legb_and_let_assignment_decide_scope
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Don't Shadow a Built-in Name with an Assignment

## Pattern Rule
**IF** naming a variable, parameter, module-level name, or any other assignment target
**THEN** check it isn't also a name Python already binds in the built-in scope (`list`, `dict`, `str`, `type`, `id`, `min`, `max`, `sum`, `input`, `open`, `format`, `all`, `any`, ...), and pick a different name when the rest of that scope still needs the original tool
**ELSE** where nothing in the remaining scope needs the built-in's original meaning, reusing the name is harmless — the assignment only hides it in the scope where the name was reassigned

## Do
- Remember that built-in names are not reserved words: nothing stops `list = [1, 2, 3]` from compiling, and from that point to the end of the enclosing scope, `list` refers to that object, not the type.
- Scope the damage mentally to the assignment's own namespace: a built-in reassigned inside one function is only hidden inside that function; the name is unaffected at module level and in every other function.
- Pick a name adjacent to the built-in's meaning instead of the built-in itself when the concept is similar — `items`, `values`, `the_list`, a domain word — rather than reaching for the shortest name that happens to collide.
- Reach for a linter that flags built-in shadowing if the codebase is large enough that a human review cannot be expected to catch every case.

## Don't
- Don't assume Python will warn you when an assignment shadows a built-in; it compiles and runs silently, and the failure shows up later as a confusing error where the built-in is needed again.
- Don't shadow a built-in and then try to reach the original through its name later in the same scope; once reassigned, the name resolves to your object for the rest of that scope, not the built-in.
- Don't name a parameter after a built-in just because it describes the argument well (e.g. `def f(list, id, type):`); a parameter assignment shadows exactly like any other.

## Checklist
- Does this name already belong to something in Python's built-in scope?
- Does any code later in this same scope still need the original built-in?
- Would a slightly more specific name avoid the collision without costing clarity?

## Notes
Shadowing works because of the same LEGB lookup every other name resolution follows — see `PAT_resolve_names_by_legb_and_let_assignment_decide_scope`. A built-in is found only when no local, enclosing, or global name matches first; assigning to that name anywhere in a scope creates exactly such a match, and the lookup never gets as far as the built-in tier again in that scope.
