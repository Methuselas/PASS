---
object_id: PAT_configure_a_decorator_with_arguments_not_function_annotations
object_type: pattern
name: Configure a Decorator with Decorator Arguments, Not Function Annotations
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
- annotations
- api-design
cross_links:
- rel: related_to
  target_object_id: PAT_choose_a_closure_variable_or_function_attribute_for_decorator_state
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Configure a Decorator with Decorator Arguments, Not Function Annotations

## Pattern Rule
**IF** a decorator needs per-argument or per-call configuration data (range limits, validation rules, labels)
**THEN** pass that data as decorator arguments — `@decorator(low=0, high=10)` — retained in an enclosing scope for the actual decorator to use
**ELSE** never repurpose a function's `__annotations__` to carry decorator configuration; annotations are the established channel for static type information that type checkers and other current tooling read, and a decorator that reads them for something else collides with that convention

## Do
- Thread configuration values through `@decorator(arg=value)` syntax, letting the outer callable retain them in an enclosing scope for use by the actual decorator and its wrapper.
- Keep a decorated function's signature free of decoration-specific markup; its parameters and annotations should describe what the function itself needs, not what a decorator wrapping it happens to check.
- Prefer decorator arguments when more than one independent concern might need to configure the same function (several validation rules, or the same decorator applied with different settings to different functions).

## Don't
- Don't write a decorator that reads `func.__annotations__` for anything other than type information; current Python tooling (type checkers, IDEs, documentation generators) treats annotations as type hints by convention, and a decorator overloading them for unrelated configuration breaks that assumption for every other consumer of the same function.
- Don't assume annotation-based configuration is simpler just because it needs one fewer level of nesting; moving configuration into the function header also limits the function to that one configured purpose, since an annotation slot holds only one expression per argument.
- Don't choose annotations to save a small amount of decorator code at the cost of making the configured function unusable with ordinary type-hint tooling.

## Checklist
- Is decorator configuration passed as decorator arguments rather than folded into the decorated function's own annotations?
- If annotations are present on a decorated function, do they still mean type hints and nothing else?
- Would adding a second, independent decorator to the same function still work cleanly with this configuration scheme?

## Notes
Decorator arguments and function annotations can both carry a value from the function definition to the decorator's wrapper, but they attach it to different things: decorator arguments are retained by the decorator's own enclosing scope, while annotations are stored on the function object itself, in the same dictionary that type checkers and other current tools read as type hints. That shared location is exactly the problem — a decorator that repurposes `__annotations__` for its own configuration is reusing storage some other consumer already has a claim on, while decorator arguments add a channel that is wholly the decorator's own.
