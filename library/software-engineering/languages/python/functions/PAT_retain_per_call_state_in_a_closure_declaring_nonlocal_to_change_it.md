---
object_id: PAT_retain_per_call_state_in_a_closure_declaring_nonlocal_to_change_it
object_type: pattern
name: Retain Per-Call State in a Closure, Declaring nonlocal to Change It
library_path:
- software-engineering
- languages
- python
- functions
stage_binding: 3 rough
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- functions
- closures
- nonlocal
cross_links:
- rel: related_to
  target_object_id: PAT_treat_def_as_a_runtime_assignment_of_a_function_object
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Retain Per-Call State in a Closure, Declaring nonlocal to Change It

## Pattern Rule
**IF** a function must remember information between calls, needs an independent copy of it per function produced, and that information is private to the function using it
**THEN** build it as a closure — an outer function that assigns the state and returns a nested function that uses it — and declare the state `nonlocal` in the nested function only where the nested function rebinds it
**ELSE** when the name to be assigned lives in the enclosing module rather than an enclosing function, use `global` instead; `nonlocal` cannot reach module or built-in scope at all

## Do
- Assign the state in the outer function, reference it freely in the nested function, and return the nested function without calling it; the captured value stays reachable after the outer call has returned.
- Call the outer function again whenever a second, independent copy is needed; each returned function carries its own captured state, and changing one leaves the others untouched.
- Add `nonlocal name` only for names the nested function rebinds; plain reads of an enclosing function's names need no declaration.
- Expect `nonlocal` to require that the name already exists in an enclosing function when the nested `def` is compiled; it cannot create a new name there, and the error arrives at definition time rather than on a later call.
- Keep both functions at top level and pass the value as an argument instead when the inner function does not actually need captured state; flat code is easier to follow than nesting for its own sake.

## Don't
- Don't rebind a captured name without declaring it; the assignment silently makes that name local to the nested function, and the first read inside raises `UnboundLocalError` even though an enclosing binding exists.
- Don't write `nonlocal` at module level or for a module-level name; it is a syntax error outside a nested function and will not reach the enclosing module.
- Don't expect captured state to be reachable from outside the pair of functions; it is visible only to code inside the nested function, so a caller that must read or set it needs a different mechanism.
- Don't assume one factory call's state is shared with another's; independent copies are the point of this technique, and code written expecting a single shared counter will quietly get one per call instead.

## Checklist
- Does each call to the outer function need its own copy of the state, rather than one shared copy?
- Is `nonlocal` declared for exactly the names the nested function rebinds, and no others?
- Does every `nonlocal` name already exist in an enclosing function's scope?
- Does any caller need to read this state from outside, which this technique cannot provide?

## Notes
The captured value is attached to the nested function object rather than to the outer call's frame, which is why it survives the outer function's return and why each produced function gets its own. `nonlocal` exists because reading an enclosing name has always worked while rebinding one did not: without the declaration, an assignment classifies the name local, and the enclosing binding becomes unreachable from inside. The declaration also narrows lookup for those names to enclosing functions only, so it states both that the name is assignable and where it must already live.
