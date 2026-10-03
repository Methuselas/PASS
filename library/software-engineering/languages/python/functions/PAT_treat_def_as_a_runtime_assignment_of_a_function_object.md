---
object_id: PAT_treat_def_as_a_runtime_assignment_of_a_function_object
object_type: pattern
name: Treat def as a Runtime Assignment of a Function Object
library_path:
- software-engineering
- languages
- python
- functions
stage_binding: 1 skeleton
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- functions
- first-class-objects
- runtime
cross_links:
- rel: related_to
  target_object_id: PAT_always_call_a_function_with_parentheses_even_with_no_arguments
- rel: related_to
  target_object_id: PAT_dispatch_a_multiway_branch_with_a_dict_instead_of_an_elif_chain
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Treat def as a Runtime Assignment of a Function Object

## Pattern Rule
**IF** writing or reasoning about a `def` in Python — where it may appear, what it produces, or what its name actually holds
**THEN** treat it as an executable statement that, when reached at runtime, builds a function object and binds it to the name exactly as an assignment would, so the name is an ordinary reference that can be rebound, aliased, stored, or passed, and the `def` itself can sit anywhere a statement is legal
**ELSE** when a function must exist for every caller regardless of control flow, keep its `def` at module top level, where importing the module runs it once — not buried in a branch that may never execute

## Do
- Expect a `def` to create and bind the function and nothing more; the body's code runs only when something calls it, and runs again from the start on every call.
- Nest a `def` inside an `if`, a loop, or another `def` when the definition itself should depend on runtime conditions — selecting between two implementations by branch is legal and occasionally the clearest option.
- Alias a function freely: after `other = func`, calling `other()` runs the same object, because the name was never more than a reference to it.
- Store functions in lists, dicts, or other containers and pass them as arguments for the same reason — a function is an ordinary object, not a special kind of declaration.
- Attach attributes to a function object (`func.attr = value`) when a small amount of data belongs with the function itself rather than in a separate structure.
- Expect a function that falls off the end of its body, or runs a bare `return`, to hand back `None`; only an explicit `return value` sends anything else.

## Don't
- Don't expect a function to exist before its `def` has actually run; Python has no separate definition phase, so a top-level call placed above its `def` in the same file fails.
- Don't treat the name as part of the function's identity; nothing about the object depends on the name it was first bound to, and rebinding or deleting that name leaves every other reference to the same function working.
- Don't read a bare `def` as also invoking the function; defining and calling are separate steps, and the body stays unexecuted until a call expression reaches it.
- Don't assume a conditional or nested `def` is exotic enough to avoid; the risk is not that it is illegal but that a reader may not notice the definition is reached only on some paths.

## Checklist
- Has the `def` actually run before any code calls the function?
- If a `def` sits inside a branch or another function, is that conditional definition deliberate rather than accidental?
- Where a function is passed, stored, or aliased, is it referenced by bare name rather than called by mistake?
- Does any caller depend on a return value the function never explicitly returns?

## Notes
`def` is closer to `=` than to a declaration in a compiled language: it evaluates where it is reached, builds an object, and binds a name. Every practical consequence follows from that one fact — there is no phase in which functions simply "exist," so execution order decides what is defined; the function's name is one reference among however many the program later makes; and anything that can be done with an object can be done with a function.

The complementary rule at the call site is `PAT_always_call_a_function_with_parentheses_even_with_no_arguments`: because a bare name is a legitimate reference to the function object, omitting the parentheses is never an error, only a different operation.
