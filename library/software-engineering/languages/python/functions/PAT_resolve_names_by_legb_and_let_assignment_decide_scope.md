---
object_id: PAT_resolve_names_by_legb_and_let_assignment_decide_scope
object_type: pattern
name: Resolve Names by LEGB and Let Assignment Decide Scope
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
- name-resolution
cross_links:
- rel: related_to
  target_object_id: PAT_copy_a_shared_mutable_object_to_the_depth_the_change_reaches
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Resolve Names by LEGB and Let Assignment Decide Scope

## Pattern Rule
**IF** working out where a name used inside a function lives, or why a name lookup fails
**THEN** apply the lookup order local, then any enclosing functions from inner to outer, then the module's global scope, then built-ins — while remembering that it is the presence of an assignment anywhere in the body that makes a name local for the whole function, not the order of the statements
**ELSE** when the name must refer to something outside the function and still be assigned there, declare it `global` for module level or `nonlocal` for the nearest enclosing function rather than relying on lookup

## Do
- Treat every form of assignment in the body as making that name local for the entire function: `=`, an `import`, a nested `def` or `class`, a parameter name, a `for` or `with` target.
- Expect a reference that precedes the function's own later assignment of the same name to raise `UnboundLocalError` instead of falling back to a global of that name; the name was classified local when the function was compiled.
- Distinguish changing an object from assigning a name: calling `L.append(x)` on a module-level list needs no declaration, while `L = [...]` makes `L` local unless declared otherwise.
- Read scope from where the code sits, not from who calls whom: a function's enclosing scope is the text that encloses it, so a caller's locals are never visible to the function it calls.
- Expect a `for` statement's target to stay bound after the loop ends, since it belongs to the enclosing function or module, while a comprehension's loop variable stays private to the comprehension and never leaks out.
- Copy anything still needed out of an `except ... as name` variable inside the handler, because that name is unbound again as soon as the handler block exits.
- Pass a class-body value into a comprehension in that same class body through the outermost iterable, which is the one part evaluated in the enclosing scope: `[v * 2 for v in vals]` finds `vals`, while a filter or result expression mentioning `vals` would not.

## Don't
- Don't read "global" as program-wide; a global name belongs to one module's namespace, and other files reach it only by importing that module.
- Don't expect a name whose only assignment sits in a branch that never ran to exist at all; classification as local happens when the function is compiled, but binding happens only when the assignment actually executes.
- Don't count on locals surviving a call: every call, including every recursive call, builds its own fresh local namespace that is discarded on return.
- Don't look to an enclosing class for name resolution; only enclosing functions form the middle lookup layer, so code inside a method does not see names assigned in the surrounding class body as plain names.
- Don't reference a class-body name from inside a comprehension written in that same class body. The comprehension has its own scope, and the class body is not an enclosing scope for it, so the name raises `NameError` — even though the line just above could use it freely.

## Checklist
- Does every name this function assigns anywhere actually belong in its local scope?
- For a name that must come from outside and be changed, is there a `global` or `nonlocal` declaration?
- Does any reference occur textually before the function's own assignment of that same name?
- Is an `except ... as` variable used only inside its own handler block?

## Notes
Scope here is lexical and settled by assignment: because names are never declared, the interpreter uses the location of a name's assignment to decide which namespace it belongs to, and decides once for the whole function rather than line by line. That is why a single assignment at the bottom of a function changes what a reference at the top means. The lookup direction (inner to outer, stopping at the first hit) and the assignment direction (always local unless declared) are two separate rules, and most scope confusion comes from applying one where the other governs.
