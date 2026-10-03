---
object_id: PAT_declare_global_only_to_assign_a_module_level_name
object_type: pattern
name: Declare global Only to Assign a Module-Level Name
library_path:
- software-engineering
- languages
- python
- functions
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- functions
- scopes
- global
cross_links:
- rel: related_to
  target_object_id: PAT_avoid_global_state_inject_shared_state
- rel: related_to
  target_object_id: PAT_start_a_variable_at_the_narrowest_scope
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Declare global Only to Assign a Module-Level Name

## Pattern Rule
**IF** a function needs to work with a name that lives at the top level of its own module
**THEN** reference it directly with no declaration, and add `global name` only where the function must rebind it, treating the statement as a namespace declaration that says which scope the assignment lands in
**ELSE** when the information is really a value the caller should supply or receive, pass it in as an argument and hand it back with `return` instead of reaching into module scope at all

## Do
- Leave `global` out for reads; lookup finds module-level names from inside a function with no declaration needed.
- List every module-level name the function assigns in one `global` statement near the top of the body, where a reader meets it before the assignments it governs.
- Expect `global` to create the module-level name if it does not exist yet, which is why a function can introduce a module attribute on its first call.
- Route another module's changes through a function in that module rather than assigning its names from outside: a caller writing `mod.set_limit(88)` announces a change that `mod.limit = 88` hides from anyone reading `mod` alone.

## Don't
- Don't add `global` for a name the function only mutates in place; appending to a module-level list changes the object rather than the binding and needs no declaration.
- Don't substitute importing your own module, or indexing the loaded-modules table, to assign module attributes from inside a function; both reach the same effect as `global` with more code and less visible intent.
- Don't let module-level names serve as the channel between functions where arguments and return values would do; the value then depends on the order of calls, which no reader can determine from the file in front of them.

## Checklist
- Is every `global` in this function present because of an assignment rather than a reference?
- Could this value be a parameter and a return value instead of a module-level name?
- When another module changes this name, does the change go through a function that makes it visible?

## Notes
The statement is a namespace declaration, not a type or storage declaration: it does not describe the value, only which scope an assignment binds in. The design question of whether shared mutable state should exist at all belongs to `PAT_avoid_global_state_inject_shared_state`, and how widely any name should be visible, including its prescription to share through access routines, belongs to `PAT_start_a_variable_at_the_narrowest_scope`. This card covers only the Python mechanics those judgments are carried out with.
