---
object_id: PAT_choose_a_closure_variable_or_function_attribute_for_decorator_state
object_type: pattern
name: Choose a Closure Variable or Function Attribute for Decorator State
library_path:
- software-engineering
- languages
- python
- decorators
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- decorators
- closures
- state
cross_links:
- rel: related_to
  target_object_id: PAT_use_nested_functions_not_callable_classes_for_decorators_that_wrap_methods
- rel: related_to
  target_object_id: PAT_retain_per_call_state_in_a_closure_declaring_nonlocal_to_change_it
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Choose a Closure Variable or Function Attribute for Decorator State

## Pattern Rule
**IF** a function decorator must remember changeable, per-decoration state (a call counter, accumulated time) across repeated calls to the wrapped function
**THEN** keep that state either in an enclosing-scope variable declared `nonlocal` inside the returned wrapper, or as an attribute assigned directly on the wrapper function object — never in a plain module-level (global) variable
**ELSE** when the state never changes after decoration (the original function, a configuration value passed as a decorator argument), an ordinary closure reference with no `nonlocal` is already enough; nothing needs to be mutable

## Do
- Use a `nonlocal`-declared enclosing variable when the state is purely internal to the decorator's own logic and nothing outside needs to read it directly.
- Use a function attribute on the returned wrapper (`wrapper.calls = 0`, incremented inside `wrapper`) when calling code should be able to inspect the state from outside — `spam.calls` reads naturally where a nonlocal variable could not be reached at all.
- Confirm that each call to the decorator (each `@decorator` application) produces its own separate wrapper function and thus its own separate closure cell or attribute namespace, giving each decorated function an independent counter.

## Don't
- Don't move changeable decorator state into a plain module-level global variable to work around scoping; a global is shared by every function the decorator ever wraps, not kept separate per decoration, so one decorated function's calls increment a counter another decorated function also reads.
- Don't assume a closure variable is externally visible; code outside the decorator and its wrapper has no way to read a `nonlocal`-held value directly, only through whatever the wrapper itself chooses to expose.
- Don't forget the `nonlocal` declaration when a nested function's body reassigns (not just reads) an enclosing variable; without it, the assignment silently creates a new local variable inside the wrapper instead of updating the enclosing one.

## Checklist
- Does each decorated function get its own independent copy of the changeable state, rather than sharing one global?
- Where the state must be read from outside the decorator's own code, is it exposed as a function attribute rather than trapped in an inaccessible closure variable?
- Does every reassignment of an enclosing-scope variable inside the wrapper carry the matching `nonlocal` declaration?

## Notes
A global variable and a closure variable fail in opposite directions for this problem: a global is visible everywhere but shared by everything, while an unexposed closure variable is correctly separated per decoration but invisible to anyone outside the wrapper. A function attribute split the difference by attaching the changeable value to the one object — the wrapper itself — that is both unique per decoration and already reachable by name from outside, which is exactly what lets external code read `spam.calls` without needing any access to the decorator's internals.
